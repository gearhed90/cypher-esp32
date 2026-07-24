# Cypher Robot — Setup Guide

**Last Updated:** July 24, 2026

This guide explains how to bring up the Cypher robot from this repository.

## Project Philosophy

The core motor-control and manual-movement layer is kept **simple and stable**.  
New features are built on top of this foundation. Do not modify the base movement code unless you are deliberately improving the Foundation itself.

## Prerequisites

### ESP32
- PlatformIO (VS Code extension recommended)
- USB-to-serial adapter (for flashing / recovery)
- ESP32-WROVER-CAM (or compatible)

### Raspberry Pi
- Raspberry Pi 4 (or 5)
- Raspberry Pi OS (Bookworm or newer)
- Python 3.11+

## 1. ESP32 Firmware

```bash
git clone https://github.com/gearhed90/cypher-esp32.git
cd cypher-esp32/firmware
pio run --target upload
```

After flashing, monitor the serial console. The ESP32 should boot, initialize UART, and wait for commands from the Pi.

> **Note:** The current firmware still contains residual WiFi + WebServer code.  
> Removing that residual code is a Foundation task. Until then, the web server may start, but the production control path is UART only.

## 2. Raspberry Pi Dashboard

```bash
cd cypher-esp32/pi/dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Access the dashboard at:

```
http://<raspberry-pi-ip>:5000
```

or via mDNS / Tailscale once configured.

## 3. Systemd (Recommended)

Use the provided service file so the dashboard starts on boot:

```bash
sudo cp cypher-dashboard.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now cypher-dashboard.service
```

## 4. UART Wiring

See [UART_PROTOCOL.md](UART_PROTOCOL.md) for the exact pinout (GPIO 18/19 on ESP32 ↔ pins 19/10 on Pi).

## Recommended Order After Basic Bring-up

1. Confirm dashboard can send `MOVE` / `STOP` and that the ESP32 responds.
2. Confirm the 1.5 s safety timeout works (stop the dashboard and watch motors stop).
3. Clean residual web-server code from the ESP32 firmware.
4. Harden remote access (Tailscale + nginx) — see [cypher-remote-access.md](cypher-remote-access.md).
5. Continue mechanical track work (tensioner is already locked).

## Folder Structure

```
cypher-esp32/
├── firmware/          # ESP32 motor controller
├── pi/
│   ├── dashboard/     # Flask control UI
│   ├── bridge/        # UART bridge class
│   ├── services/      # systemd units
│   └── vision/        # future work
└── docs/
```

## Troubleshooting

| Symptom | Checks |
|---------|--------|
| ESP32 silent | Serial console at 115200, power, strapping pins |
| Dashboard cannot open serial | Permissions on `/dev/serial0`, another process holding the port |
| Motors never stop | Confirm heartbeat is running and timeout code is active |
| Port 5000 conflict | Change port in `app.py` or stop the conflicting service |

---

**Last updated:** July 24, 2026
