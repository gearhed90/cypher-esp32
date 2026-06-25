# Cypher Dashboard

A calm, precise, high-tech monitoring interface for the Cypher robot.

## Features

- **Branding**: "CYPH ER" with "Analytical Guardian" designation
- **Live Camera Stream**: Prominent embedded MJPEG feed (responsive)
- **Control Access**: Large, prominent button to open the ESP32 control interface
- **Cyberpunk Analytical Aesthetic**: Deep dark theme with subtle cyan/blue accents
- **Responsive**: Works cleanly on desktop and mobile
- **Minimal Dependencies**: Pure Flask + vanilla JS/CSS

## Personality

The interface is designed to feel like a calm tactical command screen — analytical, observant, and slightly synthetic. Dark background, clean typography, understated neon accents.

## Important: Running on Raspberry Pi (User: sentry)

The correct location on your Pi is:

```
/home/sentry/cypher-dashboard/
```

**Never run with the system Python.** Always use the virtual environment.

---

## 1. Initial Setup (One-time)

SSH into your Pi as user `sentry` (or switch user after login).

```bash
# Go to the dashboard directory
cd /home/sentry/cypher-dashboard

# Create a virtual environment (using python3 explicitly)
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Verify Flask is installed correctly:

```bash
which python
python -c "import flask; print('Flask version:', flask.__version__)"
```

You should see the path pointing inside `venv/bin/python`.

---

## 2. Configure Environment Variables

Create a `.env` file (or export variables directly):

```bash
cd /home/sentry/cypher-dashboard

# Create .env file
cat > .env << 'EOF'
CYPHER_STREAM_URL=http://cypher:8080/stream
CYPHER_CONTROL_URL=http://sentrybot.local
EOF
```

**Customize the values:**

- `CYPHER_STREAM_URL`: URL of your working camera stream (usually the MJPEG endpoint on the Pi).
- `CYPHER_CONTROL_URL`: Address of the ESP32 web UI (use Tailscale/MagicDNS names).

Example using Tailscale names:
```bash
CYPHER_STREAM_URL=http://cypher:8080/stream
CYPHER_CONTROL_URL=http://cypher-esp.local
```

---

## 3. Starting the Dashboard

### Option A: Manual Start (for testing)

Use the provided startup script (recommended for manual runs):

```bash
cd /home/sentry/cypher-dashboard

# Make executable (first time)
chmod +x start-cypher.sh

# Run it
./start-cypher.sh
```

The script will:
- Change to the correct directory
- Activate the virtual environment
- Load `.env` if present
- Start the server on `0.0.0.0:5000`

Access it from any Tailscale device:
```
http://cypher:5000
```

To stop: Press `Ctrl+C`.

### Option B: Using systemd (Recommended for Production)

This is the most reliable way. The service will start automatically on boot and restart if it crashes.

#### Step 1: Install the service file

```bash
cd /home/sentry/cypher-dashboard

# Copy the service file (you may need to edit paths if different)
sudo cp cypher-dashboard.service /etc/systemd/system/cypher-dashboard.service

# Reload systemd
sudo systemctl daemon-reload
```

#### Step 2: Enable and start the service

```bash
sudo systemctl enable cypher-dashboard
sudo systemctl start cypher-dashboard
```

#### Step 3: Check status

```bash
sudo systemctl status cypher-dashboard
```

#### Useful systemd commands

```bash
# Check status
sudo systemctl status cypher-dashboard

# View live logs
sudo journalctl -u cypher-dashboard -f

# Restart the service
sudo systemctl restart cypher-dashboard

# Stop the service
sudo systemctl stop cypher-dashboard

# Disable auto-start on boot
sudo systemctl disable cypher-dashboard
```

---

## 4. Full Recommended Setup Sequence

After copying the files to `/home/sentry/cypher-dashboard/` on the Pi, run these commands in order:

```bash
cd /home/sentry/cypher-dashboard

# 1. Create venv
python3 -m venv venv

# 2. Activate and install
source venv/bin/activate
pip install -r requirements.txt

# 3. Configure environment (edit values as needed)
cat > .env << 'EOF'
CYPHER_STREAM_URL=http://cypher:8080/stream
CYPHER_CONTROL_URL=http://sentrybot.local
EOF

# 4. (Optional but recommended) Test manually first
chmod +x start-cypher.sh
./start-cypher.sh
# (Ctrl+C to stop)

# 5. Set up systemd (recommended)
sudo cp cypher-dashboard.service /etc/systemd/system/cypher-dashboard.service
sudo systemctl daemon-reload
sudo systemctl enable cypher-dashboard
sudo systemctl start cypher-dashboard

# Verify
sudo systemctl status cypher-dashboard
```

---

## 5. Accessing the Dashboard

**The correct URL is always:**

```
http://cypher:5000
```

Use this from **any other machine** that is connected to the same Tailscale network.

### Why the startup log doesn't show the Tailscale IP

When the server starts, you see:

```
* Running on http://127.0.0.1:5000
* Running on http://192.168.12.21:5000
```

**This is normal.** Flask's startup banner only shows some of the interfaces it detects (usually localhost and your regular LAN IP like 192.168.x.x).

It often skips the Tailscale IP (the `100.x.x.x` address assigned to the `tailscale0` interface). This is just how Flask/Werkzeug prints the message — it does **not** mean the server isn't listening on the Tailscale interface.

The server binds to `0.0.0.0`, so it listens on **all** interfaces, including Tailscale.

### How to see and use the Tailscale IP

On the Pi:
```bash
tailscale ip -4
```

This gives you the IP (starts with 100.).

From any other device on the same Tailscale network you can use:

- `http://cypher:5000` (easiest, if MagicDNS is enabled)
- `http://100.x.x.x:5000` (the raw Tailscale IP)

The updated `start-cypher.sh` now explicitly prints the Tailscale access info (including the IP) right before Flask's normal log lines.

### Quick verification

```bash
# On the Pi
tailscale ip -4
tailscale status

# From another Tailscale machine
curl -I http://cypher:5000
# or
curl -I http://<tailscale-ip-from-above>:5000
```

---

## Troubleshooting

**"No module named flask"**
- You are using system Python. Always activate the venv first:
  ```bash
  source /home/sentry/cypher-dashboard/venv/bin/activate
  ```

**Service fails to start**
- Check logs: `sudo journalctl -u cypher-dashboard -n 50`
- Ensure the paths in `/etc/systemd/system/cypher-dashboard.service` are correct.
- Re-run `sudo systemctl daemon-reload` after editing the service file.

**Stream not showing**
- Verify `CYPHER_STREAM_URL` is correct and reachable.
- Test the stream directly in browser: `http://cypher:8080/stream`
- Check that your camera streamer is running.

**Port already in use**
- Change the port in the service file and startup script (e.g. `--port=8081`).

---

## Project Structure

```
cypher-dashboard/
├── app.py
├── requirements.txt
├── start-cypher.sh          # Manual startup script
├── cypher-dashboard.service # systemd unit file (copy to /etc/systemd/system/)
├── .env.example
├── templates/
│   └── index.html
├── static/
│   ├── css/style.css
│   └── js/main.js
└── README.md
```

## Customizing

- **URLs**: Edit `.env` or the environment variables in the service file.
- **Theme**: `static/css/style.css`
- **Content**: `templates/index.html`

The systemd approach ensures the dashboard survives reboots and terminal sessions. Use it.

---

## License

MIT