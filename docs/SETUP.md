# Cypher Robot - Setup Guide

This guide explains how to set up the Cypher robot from scratch using this repository.

## Project Philosophy

The core motor control and manual movement layer is intentionally kept **simple and stable**. All autonomous/straight-tracking logic has been removed for now. New features should be built **on top** of this foundation without modifying the base movement code.

## Prerequisites

### For ESP32 Firmware
- [PlatformIO](https://platformio.org/) installed (VS Code extension recommended)
- USB-to-serial adapter (for initial flashing)
- ESP32-WROVER-CAM board

### For Raspberry Pi
- Raspberry Pi 4 (or 5)
- Raspberry Pi OS (Bookworm or newer recommended)
- Python 3.11+

## 1. ESP32 Firmware Setup

1. Clone this repository:

```bash
git clone https://github.com/gearhed90/cypher-esp32.git
cd cypher-esp32
Open the firmware/ folder in PlatformIO (or VS Code with PlatformIO extension).
Build and upload the firmware:

Bashcd firmware
pio run --target upload

After flashing, the ESP32 should create a WiFi access point or connect to your configured network and serve a basic manual control web interface.

Note: WiFi credentials are currently hardcoded in firmware/src/main.cpp. Update them before flashing if needed.
2. Raspberry Pi Dashboard Setup

SSH into your Raspberry Pi.
Clone the repository (or copy it over):

Bashgit clone https://github.com/gearhed90/cypher-esp32.git
cd cypher-esp32/pi/dashboard

Create and activate a virtual environment:

Bashpython3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Run the dashboard:

Bashpython app.py

Access the dashboard from your browser at:

texthttp://<raspberry-pi-ip>:5000
3. Recommended Next Steps
After basic setup is working:

Set up systemd services so everything starts automatically on boot (pi/services/)
Establish reliable UART communication between the Pi and ESP32
Add monitoring / status page
Improve remote access (Tailscale, reverse proxy, etc.)

Folder Structure
textcypher-esp32/
├── firmware/          # ESP32 code (clean manual foundation)
├── pi/
│   ├── dashboard/     # Flask web interface
│   ├── vision/        # Camera + tracking code (to be added)
│   └── services/      # systemd + startup scripts
├── docs/
└── README.md
Important Notes

The current ESP32 firmware is manual control only. Autonomous behaviors have been intentionally removed to keep the base layer stable.
Motor control logic lives in firmware/src/main.cpp and should be treated as protected code.
When adding new features later, try to interact with the motor layer through clean interfaces rather than modifying it directly.

Troubleshooting

ESP32 not responding: Check serial output during boot. Make sure WiFi credentials are correct.
Dashboard not starting: Ensure you're inside the virtual environment and all dependencies are installed.
Port conflicts: The dashboard runs on port 5000 by default.


Last updated: June 2026
