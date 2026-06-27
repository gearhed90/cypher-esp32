# Cypher Robot

A modular robot project built around an ESP32 and Raspberry Pi 4.

## Current Status

- **ESP32 Firmware**: Clean manual-only foundation (all autonomous/straight-tracking code has been removed for stability).
- **Core Philosophy**: Keep motor control and basic movement rock-solid. New features should be added on top without modifying the base movement layer.
- **Project Structure**: Reorganized for better maintainability and reproducibility.

## Project Structure

cypher-esp32/
├── firmware/              # ESP32 code (PlatformIO)
│   ├── src/
│   │   └── main.cpp
│   └── platformio.ini
├── pi/
│   ├── dashboard/         # Flask web UI
│   ├── vision/            # Camera streaming + tracking (future)
│   └── services/          # systemd services, nginx config, etc.
├── docs/
├── .gitignore
└── README.md

## Getting Started

### ESP32 Firmware

1. Open the `firmware/` folder in PlatformIO.
2. Build and upload:

```bash
cd firmware
pio run --target upload
cd pi/dashboard
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
Then access it at http://<pi-ip>:5000.
Goals & Roadmap

Phase 1 (Current): Stable manual control foundation on ESP32.
Phase 2: Reliable UART communication between Pi and ESP32.
Phase 3: Clean systemd services + auto-start on boot.
Phase 4: Remote access improvements + monitoring.
Phase 5 (Later): Carefully reintroduce autonomous/tracking features on top of the stable base.
Notes

Autonomous / straight-tracking behavior has been intentionally removed for now to keep the core movement layer stable and predictable.
The goal is to be able to recreate the entire robot from this repository with minimal effort.

License
TBD
