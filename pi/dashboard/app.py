#!/usr/bin/env python3
"""
Cypher Dashboard
Lightweight Flask application serving the robot monitoring interface.
Run on the Raspberry Pi and access over Tailscale as cypher:5000 (or your chosen port).
"""

import os
from flask import Flask, render_template


def load_env_file(filepath=".env"):
    """Load environment variables from a .env file (stdlib only, no extra deps)."""
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


# Load .env early if present (useful when running directly)
load_env_file()

app = Flask(__name__)

# Configuration - override via environment variables or .env file
# Recommended values for Tailscale access:
#   CYPHER_STREAM_URL=http://cypher:8080/stream
#   CYPHER_CONTROL_URL=http://sentrybot.local
STREAM_URL = os.environ.get("CYPHER_STREAM_URL", "http://cypher:8080/stream")
CONTROL_URL = os.environ.get("CYPHER_CONTROL_URL", "http://sentrybot.local")
DASHBOARD_TITLE = os.environ.get("DASHBOARD_TITLE", "Cypher")


@app.route("/")
def index():
    return render_template(
        "index.html",
        stream_url=STREAM_URL,
        control_url=CONTROL_URL,
        title=DASHBOARD_TITLE
    )


if __name__ == "__main__":
    # Bind to all interfaces so it is reachable over Tailscale / network
    # Use a different port if 5000 conflicts with other services
    app.run(host="0.0.0.0", port=5000, debug=False)