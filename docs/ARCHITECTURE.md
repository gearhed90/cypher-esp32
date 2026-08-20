# Cypher Architecture

**Last Updated:** August 20, 2026  
**Phase:** Foundation  
**Hub role:** High-level planning & organization only; implementation lives in dedicated threads.

## Overview

Cypher uses a clear separation of responsibilities:

- The **Raspberry Pi 4** is the central brain: dashboard, sensors (planned), pan/tilt servos, camera stream, remote access.
- The **ESP32** is a **pure motor controller** over UART (no WiFi, no web UI, no OTA).

Live control UI **runs on the Pi**. GitHub holds source only — it is not a runtime host for the dashboard.

## System Components

| Component | Role | Location | Notes |
|-----------|------|----------|-------|
| Dashboard (Flask) | Drive UI + pan/tilt API + status | `pi/dashboard/` | Owns UART via ESP32Bridge; servos via `servo_control.py` |
| ESP32Bridge | UART + heartbeat | `pi/bridge/esp32_bridge.py` | Inside dashboard process |
| ESP32 firmware | Motors + 1.5 s timeout | `firmware/src/main.cpp` | Motors only |
| Pan/tilt servos | Camera head | Pi BCM **18** (pan), **17** (tilt) | Power from 5 V rail |
| Camera stream | MJPEG | `pi/vision/mjpeg_stream.py` (port 8080) | Optional process |
| Wi‑Fi / field access | Station, Tailscale, AP recovery | `pi/wifi-setup/`, `docs/cypher-remote-access.md` | Remote-access thread |

## Communication Flow

```
Browser / PWA
    ↓  HTTP  /api/move | /api/stop | /api/pan_tilt
Dashboard (Flask on Pi)
    ├─ ESP32Bridge → UART → ESP32 motors
    └─ gpiozero servos → pan/tilt
```

- Motor commands: `MOVE:throttle,steering`, `STOP`, `HEARTBEAT`, `STATUS?`
- ESP32 stops motors if no command for 1.5 s; bridge heartbeat keeps link alive when idle.

## Control Methods (dashboard)

- Mobile continuous throttle/steer sliders + trim; desktop dual-stick / keyboard
- Discrete speed 10%–100% (number keys 1–0 on desktop path)
- Pan/tilt nudge + center via API/UI
- STOP on tab hide / blur

## Safety

- 1.5 s motor timeout on ESP32
- Heartbeat from Pi bridge
- Boot policy: **Manual + Stopped** (motors off until commanded)
- Frontend STOP on hide/blur

## Guiding Principles

1. Protect the motor-control foundation.
2. New capabilities use motors only through the UART protocol.
3. Keep the ESP32 simple and deterministic.
4. All sensing on the Pi (when added).
5. Documentation stays in sync with the running system.
6. This planning hub does not own deep implementation (hardware, remote, sensors threads do).

---

See: [UART_PROTOCOL.md](UART_PROTOCOL.md) · [CURRENT_STATE.md](CURRENT_STATE.md) · [ROADMAP.md](ROADMAP.md) · [hardware.md](hardware.md) · [cypher-remote-access.md](cypher-remote-access.md)
