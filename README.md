# Cypher

Cypher is a robot project where the Raspberry Pi acts as the central brain and the ESP32 handles motor control.

## Current Status

- **Dashboard**: Running at `http://cypher:5000`
- **Controls**: On-screen buttons + keyboard arrow keys + speed slider
- **Communication**: UART between Pi and ESP32 with automatic heartbeat
- **Safety**: 1.5s motor timeout on the ESP32
- **Architecture**: Pi is the only control interface (ESP32 has no web server)

## Quick Start

```bash
# Restart dashboard
sudo systemctl restart cypher-dashboard.service

# View logs
sudo journalctl -u cypher-dashboard.service -f
Documentation
See docs/ARCHITECTURE.md for a detailed overview of the system.
Project Structure
textcypher-esp32/
├── firmware/               # ESP32 motor controller code
├── pi/
│   ├── dashboard/          # Flask web interface
│   └── bridge/             # ESP32Bridge class
└── docs/
    └── ARCHITECTURE.md
