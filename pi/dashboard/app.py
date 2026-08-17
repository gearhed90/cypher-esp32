#!/usr/bin/env python3
"""
Cypher Dashboard
Flask application that serves the monitoring UI, owns the UART
link to the ESP32 motor controller, and drives pan/tilt servos on the Pi.
"""

import os
import sys
import logging
from flask import Flask, render_template, request, jsonify

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from bridge.esp32_bridge import ESP32Bridge

import servo_control


def load_env_file(filepath=".env"):
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

STREAM_URL = os.environ.get("CYPHER_STREAM_URL", "http://cypher:8080/stream")
DASHBOARD_TITLE = os.environ.get("DASHBOARD_TITLE", "Cypher")
SERIAL_PORT = os.environ.get("CYPHER_SERIAL_PORT", "/dev/serial0")
SERIAL_BAUD = int(os.environ.get("CYPHER_SERIAL_BAUD", "115200"))

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("cypher-dashboard")

bridge = ESP32Bridge(
    port=SERIAL_PORT,
    baudrate=SERIAL_BAUD,
    heartbeat_interval=0.8,
    heartbeat_timeout=1.5,
)

_bridge_started = False
_servos_started = False


def ensure_bridge():
    global _bridge_started
    if not _bridge_started:
        ok = bridge.start()
        if ok:
            logger.info("ESP32Bridge started on %s", SERIAL_PORT)
        else:
            logger.warning("ESP32Bridge failed to open %s", SERIAL_PORT)
        _bridge_started = True
    return bridge.is_connected()


def ensure_servos():
    global _servos_started
    if not _servos_started:
        ok = servo_control.start()
        if ok:
            logger.info("Pan/tilt servos ready")
        else:
            logger.warning("Pan/tilt servos unavailable (install gpiozero / check wiring)")
        _servos_started = True
    return servo_control.is_ok()


@app.route("/")
def index():
    ensure_bridge()
    ensure_servos()
    return render_template(
        "index.html",
        stream_url=STREAM_URL,
        title=DASHBOARD_TITLE,
        bridge_ok=bridge.is_connected(),
    )


@app.route("/api/status")
def api_status():
    ensure_bridge()
    ensure_servos()
    pan, tilt = servo_control.get_angles()
    return jsonify({
        "connected": bridge.is_connected(),
        "healthy": bridge.is_healthy(),
        "servos": servo_control.is_ok(),
        "pan": pan,
        "tilt": tilt,
    })


@app.route("/api/move", methods=["POST"])
def api_move():
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
    ensure_bridge()
    if not bridge.is_connected():
        return jsonify({"ok": False, "error": "ESP32 not connected"}), 503
    ok = bridge.stop()
    return jsonify({"ok": ok})


@app.route("/api/pan_tilt", methods=["POST"])
def api_pan_tilt():
    """Set or nudge pan/tilt. Body JSON:
    {"pan": 0, "tilt": 0} absolute degrees, and/or
    {"pan_delta": 5, "tilt_delta": -5} relative.
    """
    ensure_servos()
    if not servo_control.is_ok():
        return jsonify({"ok": False, "error": "servos unavailable"}), 503

    data = request.get_json(silent=True) or {}
    ok = True
    if "pan_delta" in data or "tilt_delta" in data:
        try:
            pd = float(data.get("pan_delta", 0) or 0)
            td = float(data.get("tilt_delta", 0) or 0)
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "invalid delta"}), 400
        ok = servo_control.nudge(pd, td)
    if "pan" in data or "tilt" in data:
        pan = data.get("pan", None)
        tilt = data.get("tilt", None)
        try:
            pan = float(pan) if pan is not None else None
            tilt = float(tilt) if tilt is not None else None
        except (TypeError, ValueError):
            return jsonify({"ok": False, "error": "invalid angle"}), 400
        ok = servo_control.set_angles(pan, tilt) and ok

    pan, tilt = servo_control.get_angles()
    return jsonify({"ok": ok, "pan": pan, "tilt": tilt})


@app.route("/api/pan_tilt/center", methods=["POST"])
def api_pan_tilt_center():
    ensure_servos()
    if not servo_control.is_ok():
        return jsonify({"ok": False, "error": "servos unavailable"}), 503
    ok = servo_control.center()
    pan, tilt = servo_control.get_angles()
    return jsonify({"ok": ok, "pan": pan, "tilt": tilt})


@app.teardown_appcontext
def shutdown_bridge(exception=None):
    pass


if __name__ == "__main__":
    ensure_bridge()
    ensure_servos()
    app.run(host="0.0.0.0", port=5000, debug=False)
