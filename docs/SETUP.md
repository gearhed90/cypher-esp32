# Cypher Robot — Setup Guide

**Last Updated:** August 22, 2026

## Prerequisites

- ESP32 (WROVER / DevKit) + PlatformIO
- Raspberry Pi 4, Raspberry Pi OS, Python 3
- UART wiring + 5 V rail for motors/servos
- Camera Module 3 (IMX708) on Pi CSI

## 1. ESP32 firmware

```bash
git clone https://github.com/gearhed90/cypher-esp32.git
cd cypher-esp32/firmware
# requires ESP32Servo in platformio.ini
pio run -t upload
```

Confirm serial boot banner and **Serial2 RX=19 TX=18** in firmware.

## 2. UART wiring

See [UART_PROTOCOL.md](UART_PROTOCOL.md).  
Pi user must be in `dialout`. Prefer `/dev/serial0`.

## 3. Dashboard

```bash
cd cypher-esp32/pi/dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`.env` example:

```
CYPHER_STREAM_URL=http://100.70.99.34:8080/stream
CYPHER_SERIAL_PORT=/dev/serial0
```

Systemd:

```bash
sudo cp cypher-dashboard.service /etc/systemd/system/
sudo systemctl enable --now cypher-dashboard.service
```

## 4. Camera stream

```bash
sudo tee /etc/systemd/system/cypher-stream.service > /dev/null << 'EOF'
[Unit]
Description=Cypher MJPEG camera stream
After=network-online.target

[Service]
Type=simple
User=sentry
WorkingDirectory=/home/sentry/cypher-esp32
ExecStart=/home/sentry/cypher-esp32/pi/dashboard/venv/bin/python /home/sentry/cypher-esp32/pi/vision/mjpeg_stream.py
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now cypher-stream.service
```

**Do not** run `sentry-tracker.service` at the same time (camera + UART conflict).

```bash
sudo systemctl disable --now sentry-tracker.service
```

## 5. Teach boot head pose (optional)

With dashboard stopped or via serial:

```text
PT:0,0
PT_SAVE_BOOT
```

Or move with UI then send `PT_SAVE_BOOT` over UART.

## 6. Verify

1. `STATUS?` returns `STATUS:MANUAL,...` over UART  
2. Motors from dashboard  
3. Pan/tilt hold-to-repeat  
4. `http://<pi-ip>:8080/stream` shows correct colors  
5. Dashboard embeds stream

## Troubleshooting

| Symptom | Check |
|---------|--------|
| No UART replies | `Serial2.begin(..., 19, 18)`; TX/RX not swapped; GND; stop other serial users |
| Connected true but no motion | Bridge only tracks sends; confirm ESP32 ACKs; wiring |
| Camera busy | Stop `sentry-tracker` / other picamera users |
| Wrong colors | This Pi: **no** RGB/BGR swap in `mjpeg_stream.py` |
| Disk full | `df -h`; clean apt/journal before pip/pio |
| Port permission | `dialout` group; `chmod`/`udev` for USB flash |

---

See [UART_PROTOCOL.md](UART_PROTOCOL.md) · [CURRENT_STATE.md](CURRENT_STATE.md)
