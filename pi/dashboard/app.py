#!/usr/bin/env python3
"""
Cypher Dashboard
Flask application that serves the monitoring UI and owns the UART
link to the ESP32 motor controller.

All movement commands go through ESP32Bridge.
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify

# Make the sibling bridge package importable when running from this directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bridge.esp32_bridge import ESP32Bridge


def load_env_file(filepath=".env"):
    """Load environment variables from a .env file (stdlib only)."""
    if not os.path.exists(filepath):
        return
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and value and key not in os.environ:
                os.environ[key] = value


load_env_file()

app = Flask(__name__)

# Configuration
STREAM_URL = os.environ.get("CYPHER_STREAM_URL", "http://cypher:8080/stream")
DASHBOARD_TITLE = os.environ.get("DASHBOARD_TITLE", "Cypher")
SERIAL_PORT = os.environ.get("CYPHER_SERIAL_PORT", "/dev/serial0")
SERIAL_BAUD = int(os.environ.get("CYPHER_SERIAL_BAUD", "115200"))

# Logging
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("cypher-dashboard")

# Global bridge instance (started once at import / first request)
bridge = ESP32Bridge(
    port=SERIAL_PORT,
    baudrate=SERIAL_BAUD,
    heartbeat_interval=0.8,
    heartbeat_timeout=1.5,
)

_bridge_started = False


def ensure_bridge():
    """Start the bridge on first use. Safe to call repeatedly."""
    global _bridge_started
    if not _bridge_started:
        ok = bridge.start()
        if ok:
            logger.info("ESP32Bridge started on %s", SERIAL_PORT)
        else:
            logger.warning("ESP32Bridge failed to open %s — control will be offline until reconnect", SERIAL_PORT)
        _bridge_started = True
    return bridge.is_connected()


@app.route("/")
def index():
    ensure_bridge()
    return render_template(
        "index.html",
        stream_url=STREAM_URL,
        title=DASHBOARD_TITLE,
        bridge_ok=bridge.is_connected(),
    )


@app.route("/api/status")
def api_status():
    ensure_bridge()
    return jsonify({
        "connected": bridge.is_connected(),
        "healthy": bridge.is_healthy(),
    })


@app.route("/api/move", methods=["POST"])
def api_move():
    """Send MOVE:throttle,steering to the ESP32."""
    ensure_bridge()
    data = request.get_json(silent=True) or {}
    try:
        throttle = int(data.get("throttle", 0))
        steering = int(data.get("steering", 0))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "invalid throttle/steering"}), 400

    throttle = max(-255, min(255, throttle))
    steering = max(-255, min(255, steering))

    if not bridge.is_connected():
        return jsonify({"ok": False, "error": "ESP32 not connected"}), 503

    ok = bridge.move(throttle, steering)
    return jsonify({"ok": ok, "throttle": throttle, "steering": steering})


@app.route("/api/stop", methods=["POST"])
def api_stop():
    """Emergency stop."""
    ensure_bridge()
    if not bridge.is_connected():
        return jsonify({"ok": False, "error": "ESP32 not connected"}), 503
    ok = bridge.stop()
    return jsonify({"ok": ok})


@app.teardown_appcontext
def shutdown_bridge(exception=None):
    # Do not close the bridge on every request; only on process exit.
    pass


if __name__ == "__main__":
    ensure_bridge()
    app.run(host="0.0.0.0", port=5000, debug=False)
