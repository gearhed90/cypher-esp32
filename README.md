# Cypher

Cypher is a tracked robot platform where the **Raspberry Pi 4 acts as the central brain** and the **ESP32 acts as a dedicated motor controller**.

## Current Architecture (Foundation)

- **Raspberry Pi 4** — sole control interface, camera, higher-level logic, remote access gateway
- **ESP32** — motor control only (TB6612FNG), UART command receiver, 1.5 s safety timeout
- **Communication** — UART at 115200 baud with automatic heartbeat
- **Control UI** — Flask dashboard on the Pi (`http://cypher:5000` or via Tailscale)
- **Safety** — motors stop automatically if the Pi stops sending commands for > 1.5 s

> **Note:** The ESP32 firmware still contains residual WiFi + WebServer code from an earlier design. Cleaning this residual code is a Foundation task so the ESP32 remains a pure motor controller.

## Quick Start

```bash
# Restart dashboard
sudo systemctl restart cypher-dashboard.service

# View live logs
sudo journalctl -u cypher-dashboard.service -f
```

Dashboard URL (local): `http://cypher:5000`  
Remote access: via Tailscale to the Pi.

## Project Structure

```
cypher-esp32/
├── firmware/               # ESP32 motor controller (PlatformIO)
├── pi/
│   ├── dashboard/          # Flask web interface (primary control UI)
│   ├── bridge/             # ESP32Bridge class (UART + heartbeat)
│   ├── services/           # systemd units
│   └── vision/             # future camera / tracking work
└── docs/
    ├── ARCHITECTURE.md
    ├── CURRENT_STATE.md
    ├── ROADMAP.md
    ├── UART_PROTOCOL.md
    ├── SETUP.md
    ├── cypher-remote-access.md
    └── hardware.md
```

## Documentation

| Document | Purpose |
|----------|---------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and data flow |
| [CURRENT_STATE.md](docs/CURRENT_STATE.md) | What is working right now |
| [ROADMAP.md](docs/ROADMAP.md) | Phased plan (Foundation first) |
| [UART_PROTOCOL.md](docs/UART_PROTOCOL.md) | Command protocol between Pi and ESP32 |
| [SETUP.md](docs/SETUP.md) | How to bring a new machine up |
| [cypher-remote-access.md](docs/cypher-remote-access.md) | Remote access + ESP32 recovery |
| [hardware.md](docs/hardware.md) | Chassis, tracks, mechanical status |

## Core Principles

1. Protect the foundation — motor control and basic movement stay simple and reliable.
2. Layer new features on top of the stable base; do not modify core movement logic directly.
3. Keep documentation accurate and in sync with the running system.

---

**Last updated:** July 24, 2026  
**Phase:** Foundation
