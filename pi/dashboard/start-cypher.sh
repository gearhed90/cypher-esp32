#!/bin/bash
#
# start-cypher.sh
# Robust startup script for Cypher Dashboard on Raspberry Pi
#
# Usage:
#   ./start-cypher.sh
#
# This script:
#   - Changes to the correct directory (/home/sentry/cypher-dashboard)
#   - Activates the virtual environment
#   - Loads .env if present
#   - Starts the Flask app bound to 0.0.0.0:5000 using the venv python
#
# For production use, prefer the systemd service.
#

set -e

DASHBOARD_DIR="/home/sentry/cypher-dashboard"
VENV_DIR="$DASHBOARD_DIR/venv"
PYTHON="$VENV_DIR/bin/python"

echo "==> Starting Cypher Dashboard (user: sentry)..."

# Change to the dashboard directory (critical for relative paths and .env)
cd "$DASHBOARD_DIR" || {
    echo "ERROR: Cannot cd to $DASHBOARD_DIR"
    exit 1
}

# Verify and activate virtual environment
if [ ! -x "$PYTHON" ]; then
    echo "ERROR: Virtual environment python not found at $PYTHON"
    echo "Please run setup steps from README.md first."
    exit 1
fi

# Load .env if it exists (the app also loads it, but we export for the script too)
if [ -f ".env" ]; then
    echo "==> Loading .env"
    set -a
    source .env
    set +a
fi

# Silence Flask's .env tip (we load .env manually)
export FLASK_SKIP_DOTENV=1

# Set sensible defaults if not provided
export CYPHER_STREAM_URL="${CYPHER_STREAM_URL:-http://cypher:8080/stream}"
export CYPHER_CONTROL_URL="${CYPHER_CONTROL_URL:-http://sentrybot.local}"

echo "==> Using Python: $PYTHON"
echo "==> Stream URL:   $CYPHER_STREAM_URL"
echo "==> Control URL:  $CYPHER_CONTROL_URL"
echo "==> Starting server on http://0.0.0.0:5000"

# Print helpful Tailscale info (Flask only lists normal OS interfaces)
echo ""
echo "==> Tailscale access:"
echo "==>   Recommended: http://cypher:5000"
TS_IP=$(tailscale ip -4 2>/dev/null || echo "")
if [ -n "$TS_IP" ]; then
    echo "==>   Direct IP:     http://$TS_IP:5000"
fi
echo ""
echo "==> Note: Flask's 'Running on' lines below will usually only show"
echo "==>       127.0.0.1 and your normal LAN IP (like 192.168.x.x)."
echo "==>       The Tailscale IP (100.x.x.x) is often missing from that list."
echo "==>       This is normal and NOT a problem — the server IS listening"
echo "==>       on the Tailscale interface (we bound to 0.0.0.0)."
echo "==>       Just use http://cypher:5000 from other Tailscale devices."
echo ""

# Start using the venv's python + flask module (most reliable)
exec "$PYTHON" -m flask --app app run --host=0.0.0.0 --port=5000

# Alternative (if you prefer direct):
# exec "$PYTHON" app.py
