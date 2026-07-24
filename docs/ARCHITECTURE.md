# Cypher Architecture

**Last Updated:** July 24, 2026  
**Phase:** Foundation

## Overview

Cypher uses a clear separation of responsibilities:

- The **Raspberry Pi 4** is the central brain and the **only control interface**.
- The **ESP32** is a dedicated motor controller that receives commands over UART and enforces a safety timeout.

All higher-level logic (dashboard, future vision, autonomy, remote access) lives on the Pi. The ESP32 stays simple and predictable.

## System Components

| Component | Role | Location | Notes |
|-----------|------|----------|-------|
| Dashboard (Flask) | Main control UI + status | `pi/dashboard/app.py` | Runs on port 5000 |
| ESP32Bridge | UART communication + heartbeat | `pi/bridge/esp32_bridge.py` | Owned by the dashboard process |
| ESP32 Firmware | Motor control + 1.5 s safety timeout | `firmware/src/main.cpp` | Currently still contains residual web-server code |
| Camera Stream | Live video | External service (port 8080) | Handled by Pi |

## Communication Flow

```
Dashboard (Pi)
    ↓
ESP32Bridge (UART + heartbeat every ~800 ms)
    ↓
UART (/dev/serial0 @ 115200)
    ↓
ESP32 (motor controller)
```

- Commands: `MOVE:throttle,steering`, `STOP`, `HEARTBEAT`, `STATUS?`
- ESP32 automatically stops motors if no command arrives for 1.5 seconds.
- Heartbeat from the Pi prevents the timeout during normal operation.

## Control Methods (Dashboard)

- On-screen directional buttons
- Keyboard arrow keys (supports combined forward + turn)
- Spacebar = emergency stop
- Speed slider

## Safety Features

- **1.5-second motor timeout** on the ESP32
- Automatic heartbeat from the Pi bridge
- Motors stop if the Pi crashes, the service dies, or the serial link is lost

## Current Services

| Service | Status | Purpose |
|---------|--------|---------|
| `cypher-dashboard.service` | Running | Web UI and robot control |
| `cypher-bridge.service` | Stopped | Not used — dashboard owns the serial port |

## Residual Code Note

`firmware/src/main.cpp` still contains WiFi connection logic, a WebServer, and an HTML control page from an earlier design phase.  
**This residual code should be removed** as part of Foundation work so the ESP32 becomes a pure UART motor controller (no web server, WiFi optional / disabled by default).

## Guiding Principles

1. Protect the motor-control foundation.
2. New capabilities interact with motors only through the UART protocol.
3. Keep the ESP32 simple and deterministic.
4. Documentation must stay in sync with the running system.

---

See also: [UART_PROTOCOL.md](UART_PROTOCOL.md) · [CURRENT_STATE.md](CURRENT_STATE.md) · [ROADMAP.md](ROADMAP.md)
