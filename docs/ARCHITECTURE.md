# Cypher Architecture

**Last Updated:** August 22, 2026  
**Phase:** Foundation

## Overview

- **Raspberry Pi 4** — brain: dashboard, camera stream, Tailscale, higher-level logic.
- **ESP32** — real-time **motors + pan/tilt** over UART (hardware PWM for servos). No WiFi control path.

## System components

| Component | Role | Location | Notes |
|-----------|------|----------|-------|
| Dashboard (Flask) | Drive + pan/tilt UI | `pi/dashboard/` | Owns serial via ESP32Bridge |
| ESP32Bridge | UART + heartbeat | `pi/bridge/esp32_bridge.py` | Inside dashboard process |
| ESP32 firmware | Motors + pan/tilt + motor timeout | `firmware/src/main.cpp` | Serial2 RX=19 TX=18 |
| Pan/tilt servos | Camera head | ESP32 GPIO **13** (pan), **12** (tilt) | 5 V rail + caps |
| Camera stream | MJPEG | `pi/vision/mjpeg_stream.py` | Port **8080**, systemd `cypher-stream` |
| Power | 5 V | Drok → center-channel rail | Locked |

## Communication flow

```
Browser / PWA
  → HTTP /api/move | /api/stop | /api/pan_tilt
Dashboard (Flask)
  → ESP32Bridge (UART + heartbeat ~800 ms)
  → /dev/serial0 @ 115200
  → ESP32 (motors + servo PWM)

Browser
  → http://<pi>:8080/stream  (MJPEG, separate process)
```

## Control methods

- Drive: D-pad / sliders / WASD / arrows; Space = stop; speed 10–100%.
- Pan/tilt: hold-to-repeat buttons + center; UART to ESP32.
- Page hide / blur → motor STOP.

## Safety

- 1.5 s **motor** timeout on ESP32.
- Heartbeat from bridge.
- Boot: motors stopped; head to NVS boot pose or (0,0).
- Keep `sentry-tracker.service` **disabled** during Cypher use (camera + competing UART control).

## Guiding principles

1. Protect motor foundation.
2. Actuators only via UART protocol.
3. ESP32 stays simple; use hardware timers for servos.
4. Docs match the running system.

---

See [UART_PROTOCOL.md](UART_PROTOCOL.md) · [CURRENT_STATE.md](CURRENT_STATE.md) · [SETUP.md](SETUP.md)
