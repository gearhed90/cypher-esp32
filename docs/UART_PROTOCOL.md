# Cypher UART Communication Protocol

**Last Updated:** July 24, 2026  
**Status:** Working and stable

## Overview

- **Purpose**: Reliable command channel from Raspberry Pi → ESP32 for motor control and safety.
- **Physical Layer**: UART (Serial2 on ESP32, `/dev/serial0` on Raspberry Pi)
- **Baud Rate**: 115200
- **Data Format**: 8N1
- **Safety**: ESP32 stops motors if no command is received for 1.5 seconds.

## Wiring

| ESP32          | Raspberry Pi     | Direction     | Purpose                  |
|----------------|------------------|---------------|--------------------------|
| GPIO 18 (TX2)  | GPIO 10 (Pin 19) | ESP32 → Pi    | Data from ESP32 to Pi    |
| GPIO 19 (RX2)  | GPIO 8  (Pin 10) | Pi → ESP32    | Data from Pi to ESP32    |
| GND            | Any GND          | Common        | Ground reference         |

## Commands (Pi → ESP32)

All commands are plain text followed by a newline (`\n`).

| Command                  | Description                              | Example            |
|--------------------------|------------------------------------------|--------------------|
| `MOVE:throttle,steering` | Set motor speeds (−255…255)              | `MOVE:80,25`       |
| `STOP`                   | Emergency stop (throttle=0, steering=0)  | `STOP`             |
| `HEARTBEAT`              | Keep-alive (sent automatically by bridge)| `HEARTBEAT`        |
| `STATUS?`                | Request current status                   | `STATUS?`          |
| `MODE:MANUAL`            | Set manual control mode (future use)     | `MODE:MANUAL`      |
| `MODE:AUTO`              | Set autonomous mode (future)             | `MODE:AUTO`        |

## Responses (ESP32 → Pi)

| Response                          | Description                          |
|-----------------------------------|--------------------------------------|
| `ACK:MOVE`                        | MOVE command accepted                |
| `ACK:STOP`                        | STOP executed                        |
| `HEARTBEAT`                       | Heartbeat acknowledgment (optional)  |
| `STATUS:MANUAL,throttle,steering` | Current mode and motor values        |
| `ERR:UNKNOWN_CMD`                 | Unrecognized command                 |

## Heartbeat & Safety Timeout

- The Python bridge (`esp32_bridge.py`) sends `HEARTBEAT` every **~800 ms**.
- This keeps the ESP32’s 1.5-second safety timeout from firing during normal idle periods.
- If the bridge or Pi stops, the ESP32 will stop the motors after 1.5 s of silence.

## Implementation Notes

- **ESP32**: Uses `Serial2` on GPIO 18/19. Commands parsed in `processCommand()`.
- **Raspberry Pi**: `ESP32Bridge` class in `pi/bridge/esp32_bridge.py`. Currently run inside the dashboard process (the separate `cypher-bridge.service` is stopped).
- Commands are case-sensitive.
- The bridge uses a background thread for the heartbeat so it never blocks control commands.

## Future Extensions (After Foundation)

- Expand `STATUS?` with battery, IMU, or other telemetry
- Optional checksums if the environment becomes noisy
- Clean mode switching once autonomy is re-introduced carefully

---

See [ARCHITECTURE.md](ARCHITECTURE.md) for the larger system context.
