# Cypher Architecture

**Last Updated:** July 24, 2026  
**Phase:** Foundation

## Overview

Cypher uses a clear separation of responsibilities:

- The **Raspberry Pi 4** is the central brain and the **sole control interface**.
- The **ESP32** is a dedicated motor controller that receives commands over UART and enforces a safety timeout.

All higher-level logic (dashboard, future vision, autonomy, remote access) lives on the Pi. The ESP32 stays simple and deterministic.

## System Components

| Component | Role | Location | Notes |
|-----------|------|----------|-------|
| Dashboard (Flask) | Control UI + camera | `pi/dashboard/` | Owns the serial port via ESP32Bridge |
| ESP32Bridge | UART + heartbeat | `pi/bridge/esp32_bridge.py` | Instantiated inside the dashboard process |
| ESP32 Firmware | Motor control + 1.5 s timeout | `firmware/src/main.cpp` | Pure motor controller |
| Camera Stream | Live video | External service (port 8080) | Handled by Pi |

## Communication Flow

```
Browser (buttons / keyboard)
    ↓  HTTP POST /api/move | /api/stop
Dashboard (Flask)
    ↓
ESP32Bridge (UART + heartbeat every ~800 ms)
    ↓
UART (/dev/serial0 @ 115200)
    ↓
ESP32 (motor controller)
```

- Commands: `MOVE:throttle,steering`, `STOP`, `HEARTBEAT`, `STATUS?`
- ESP32 stops motors if no command arrives for 1.5 seconds.
- Heartbeat from the bridge prevents the timeout during idle periods.

## Control Methods

- On-screen D-pad (hold = move, release = stop)
- Keyboard arrow keys + Space (emergency stop)
- Speed slider (updates live while a direction is held)
- Page-hide / blur automatically sends STOP

## Safety Features

- 1.5-second motor timeout on the ESP32
- Automatic heartbeat from the Pi bridge
- Motors stop if the Pi crashes, the service dies, or the serial link is lost
- Frontend also sends STOP on tab hide / window blur

## Guiding Principles

1. Protect the motor-control foundation.
2. New capabilities interact with motors only through the UART protocol.
3. Keep the ESP32 simple and deterministic.
4. Documentation must stay in sync with the running system.

---

See also: [UART_PROTOCOL.md](UART_PROTOCOL.md) · [CURRENT_STATE.md](CURRENT_STATE.md) · [ROADMAP.md](ROADMAP.md)
