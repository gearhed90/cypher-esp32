# Cypher Architecture

**Last Updated:** July 24, 2026  
**Phase:** Foundation

## Overview

Cypher uses a clear separation of responsibilities:

- The **Raspberry Pi 4** is the central brain and the intended control interface.
- The **ESP32** is a dedicated motor controller that receives commands over UART and enforces a safety timeout.

All higher-level logic (dashboard, future vision, autonomy, remote access) lives on the Pi. The ESP32 stays simple and deterministic.

## System Components

| Component | Role | Location | Notes |
|-----------|------|----------|-------|
| Dashboard (Flask) | Monitoring UI + future control surface | `pi/dashboard/` | Currently shows camera + link; full control integration still pending |
| ESP32Bridge | UART communication + heartbeat | `pi/bridge/esp32_bridge.py` | Ready for use by the dashboard |
| ESP32 Firmware | Motor control + 1.5 s safety timeout | `firmware/src/main.cpp` | **Pure motor controller** (WiFi/WebServer removed July 24) |
| Camera Stream | Live video | External service (port 8080) | Handled by Pi |

## Communication Flow (Intended)

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

## Current vs Intended Control Path

| Aspect | Current (July 24) | Intended Foundation end-state |
|--------|-------------------|-------------------------------|
| ESP32 | Pure UART motor controller | Same |
| Dashboard | Camera viewer + link button | Full on-screen buttons + keyboard that call the bridge |
| Control traffic | Still partially external | 100 % through ESP32Bridge |

## Safety Features

- **1.5-second motor timeout** on the ESP32
- Automatic heartbeat from the Pi bridge (when the bridge is running)
- Motors stop if the Pi crashes, the service dies, or the serial link is lost

## Guiding Principles

1. Protect the motor-control foundation.
2. New capabilities interact with motors only through the UART protocol.
3. Keep the ESP32 simple and deterministic.
4. Documentation must stay in sync with the running system.

---

See also: [UART_PROTOCOL.md](UART_PROTOCOL.md) · [CURRENT_STATE.md](CURRENT_STATE.md) · [ROADMAP.md](ROADMAP.md)
