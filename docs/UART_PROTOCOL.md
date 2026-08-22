# Cypher UART Communication Protocol

**Last Updated:** August 22, 2026  
**Status:** Motors + pan/tilt working

## Overview

- **Purpose**: Command channel from Raspberry Pi → ESP32 for **motors and pan/tilt servos**.
- **Physical Layer**: UART (Serial2 on ESP32, `/dev/serial0` → `ttyS0` on Raspberry Pi)
- **Baud Rate**: 115200
- **Data Format**: 8N1
- **Safety**: ESP32 stops **motors** if no command for 1.5 s. Servos are **not** timed out (hold last pose).

## Wiring

### UART

| ESP32 | Raspberry Pi | Direction | Purpose |
|-------|--------------|-----------|---------|
| GPIO **18** (TX2) | GPIO 10 (pin 19) | ESP32 → Pi | Data from ESP32 |
| GPIO **19** (RX2) | GPIO 8 (pin 10) | Pi → ESP32 | Data to ESP32 |
| GND | GND | Common | Ground |

Firmware **must** call:

```cpp
Serial2.begin(115200, SERIAL_8N1, 19, 18);  // RX=19, TX=18
```

Default `Serial2.begin(baud)` alone uses wrong pins and breaks the link.

### Servo signals (ESP32)

| Function | GPIO | Notes |
|----------|------|-------|
| Pan | **13** | |
| Tilt | **12** | Strapping pin — avoid holding low at boot |
| Power | 5 V rail + local caps | Not Pi 5 V pin |

## Commands (Pi → ESP32)

All commands: plain text + `\n`.

### Motors

| Command | Description | Example |
|---------|-------------|---------|
| `MOVE:throttle,steering` | Motor speeds −255…255 | `MOVE:80,25` |
| `STOP` | throttle=0, steering=0 | `STOP` |
| `HEARTBEAT` | Keep-alive (bridge ~800 ms) | `HEARTBEAT` |
| `STATUS?` | Request status | `STATUS?` |
| `MODE:MANUAL` / `MODE:AUTO` | Future | |

### Pan / tilt

| Command | Description | Example |
|---------|-------------|---------|
| `PT:pan,tilt` | Set both (degrees, clamped) | `PT:20,5` |
| `PAN:angle` | Pan only | `PAN:-15` |
| `TILT:angle` | Tilt only | `TILT:-5` |
| `PT_CENTER` | (0, 0) | `PT_CENTER` |
| `PT_SLEEP` | Sleep pose (0, −9) | `PT_SLEEP` |
| `PT_SAVE_BOOT` | Save current pose to NVS | `PT_SAVE_BOOT` |
| `PT_BOOT` | Go to saved boot pose | `PT_BOOT` |

**Software limits:** pan **±45°**, tilt **±9°** (mechanical).  
**Motion:** rate-limited ~28°/s.  
**Invert:** both axes inverted in firmware (`INVERT_PAN` / `INVERT_TILT`) so dashboard directions match the robot.  
**Boot:** loads pose from NVS if saved; else (0, 0).

## Responses (ESP32 → Pi)

| Response | Meaning |
|----------|---------|
| `ACK:MOVE` / `ACK:STOP` | Motor command accepted |
| `ACK:PT` / `ACK:PAN` / `ACK:TILT` | Servo command accepted |
| `ACK:PT_CENTER` / `ACK:PT_SLEEP` / `ACK:PT_SAVE_BOOT` / `ACK:PT_BOOT` | Pose helpers |
| `HEARTBEAT` | Optional echo |
| `STATUS:MANUAL,thr,str,pan,tilt` | Mode + motors + head angles |
| `ERR:UNKNOWN_CMD` | Bad command |

## Heartbeat & motor timeout

- Bridge sends `HEARTBEAT` ~every 800 ms.
- 1.5 s silence → motors stop.
- Servos keep position across motor timeout.

## Implementation notes

- **ESP32:** `firmware/src/main.cpp` — motors + ESP32Servo, NVS boot pose.
- **Pi bridge:** `pi/bridge/esp32_bridge.py` — `move`, `stop`, `pt`, `pan`, `tilt`, `pt_center`, `pt_sleep`, `pt_save_boot`, `pt_boot`.
- **Dashboard:** `/api/pan_tilt` and center use the bridge (not Pi GPIO).
- Commands are case-sensitive.

## Conflicts

Do **not** run `sentry-tracker.service` while using the Cypher dashboard — it opens the same UART path and drives servos/motors independently.

---

See [ARCHITECTURE.md](ARCHITECTURE.md) · [CURRENT_STATE.md](CURRENT_STATE.md)
