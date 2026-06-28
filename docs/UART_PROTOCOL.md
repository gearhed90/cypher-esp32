# Cypher UART Communication Protocol

This document describes the reliable UART communication protocol between the Raspberry Pi and the ESP32.

## Overview

- **Purpose**: Allow the Raspberry Pi to send movement commands to the ESP32 and receive status/acknowledgments.
- **Physical Layer**: UART (Serial2 on ESP32, `/dev/serial0` on Raspberry Pi)
- **Baud Rate**: 115200
- **Data Format**: 8N1 (8 data bits, no parity, 1 stop bit)
- **Safety Feature**: The ESP32 has a 1.5-second motor safety timeout. If no command is received for more than 1.5 seconds, the motors are automatically stopped.

## Wiring

| ESP32          | Raspberry Pi     | Direction     | Purpose                  |
|----------------|------------------|---------------|--------------------------|
| GPIO 18 (TX2)  | GPIO 10 (Pin 19) | ESP32 → Pi    | Data from ESP32 to Pi    |
| GPIO 19 (RX2)  | GPIO 8  (Pin 10) | Pi → ESP32    | Data from Pi to ESP32    |
| GND            | Any GND          | Common        | Ground reference         |

## Command Protocol (Pi → ESP32)

All commands are sent as plain text followed by a newline (`\n`).

| Command                  | Description                          | Example                  |
|--------------------------|--------------------------------------|--------------------------|
| `MOVE:throttle,steering` | Set motor speeds                     | `MOVE:80,25`             |
| `STOP`                   | Emergency stop (throttle=0, steering=0) | `STOP`                |
| `STATUS?`                | Request current status               | `STATUS?`                |
| `HEARTBEAT`              | Keep-alive (sent automatically)      | `HEARTBEAT`              |
| `MODE:MANUAL`            | Set manual control mode              | `MODE:MANUAL`            |
| `MODE:AUTO`              | Set autonomous mode (future)         | `MODE:AUTO`              |

## Responses (ESP32 → Pi)

| Response                    | Description                              |
|-----------------------------|------------------------------------------|
| `ACK:MOVE`                  | Command received and applied             |
| `ACK:STOP`                  | Emergency stop executed                  |
| `HEARTBEAT`                 | Response to heartbeat (optional)         |
| `STATUS:MANUAL,throttle,steering` | Current mode and motor values       |
| `ERR:UNKNOWN_CMD`           | Command was not recognized               |

## Heartbeat & Safety Timeout

- The Python bridge (`esp32_bridge.py`) automatically sends a `HEARTBEAT` command every **~800ms**.
- This prevents the ESP32’s 1.5-second safety timeout from triggering during idle periods.
- If the bridge stops (Pi crash, service failure, etc.), the ESP32 will automatically stop the motors after 1.5 seconds of silence.

## Example Session

Pi  → ESP32:  MOVE:60,0
ESP32 → Pi:   ACK:MOVE
Pi  → ESP32:  STOP
ESP32 → Pi:   ACK:STOP
(Pi bridge sends HEARTBEAT every 800ms automatically)
text## Implementation Notes

- **ESP32**: Uses `Serial2` on GPIO 18 (TX) and GPIO 19 (RX). Commands are parsed in `processCommand()`.
- **Raspberry Pi**: Uses the `ESP32Bridge` class in `pi/bridge/esp32_bridge.py`. The bridge runs as a systemd service (`cypher-bridge.service`).
- All commands are case-sensitive.
- The bridge uses a background thread for the heartbeat so it does not block other operations.

## Future Extensions

- Add `MODE:AUTO` / `MODE:MANUAL` switching
- Expand `STATUS?` response with more telemetry (battery, IMU, etc.)
- Add checksums for noisy environments (if needed)

---

**Status**: Working and stable as of June 2026.
