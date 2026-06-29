# Cypher Architecture

## Overview
Cypher is a robot where the **Raspberry Pi** acts as the central brain, and the **ESP32** acts as a dedicated motor controller.

### Key Principles
- The Raspberry Pi is the only control interface.
- The ESP32 is kept simple (no web server, WiFi disabled by default).
- All movement commands, safety logic, and future features (vision, autonomy, etc.) live on the Pi.
- Communication between Pi and ESP32 happens over UART.

## System Components

| Component                    | Role                                      | Location                          | Notes |
|-----------------------------|-------------------------------------------|-----------------------------------|-------|
| **Dashboard (Flask)**       | Main control interface + web UI           | `pi/dashboard/app.py`             | Runs at port 5000 |
| **ESP32Bridge**             | Handles UART communication + heartbeat    | `pi/bridge/esp32_bridge.py`       | Runs inside the dashboard |
| **ESP32 Firmware**          | Motor control + safety timeout            | `firmware/src/main.cpp`           | Simplified (no web server) |
| **Camera Stream**           | Live video feed                           | External service                  | Currently on port 8080 |

## Communication Flow

Dashboard (Pi)  →  ESP32Bridge  →  UART  →  ESP32 (Motor Controller)
↑
Heartbeat every ~800ms
text- The dashboard sends `MOVE`, `STOP`, and `HEARTBEAT` commands.
- The ESP32 has a **1.5-second safety timeout**. If no command is received for 1.5 seconds, motors automatically stop.
- The heartbeat prevents the safety timeout from triggering during normal operation.

## Current Control Methods

- On-screen buttons (↑ ↓ ← → STOP)
- Keyboard arrow keys (supports combined movement, e.g. forward + turning)
- Spacebar = Emergency Stop
- Speed slider (adjusts movement speed in real time)

## Running Services

| Service                    | Status     | Purpose |
|---------------------------|------------|--------|
| `cypher-dashboard.service` | Running    | Main web interface and robot control |
| `cypher-bridge.service`    | Stopped    | Not used (dashboard owns the serial port) |

## Safety Features

- **ESP32 Safety Timeout**: 1.5 seconds
- **Heartbeat**: Sent automatically by the dashboard
- **Motor Stop on Disconnect**: If the Pi crashes or the bridge stops, motors will stop within 1.5 seconds

## Current State (as of June 2026)

- Pi is the single source of control.
- ESP32 firmware is simplified (web server removed).
- Dashboard includes speed control and combined keyboard movement.
- System is stable and functional.

## Future Possibilities

- Enable OTA on ESP32 via UART command when wireless flashing is needed
- Add vision / autonomy features on the Pi
- Improve UI feedback (connection status, telemetry, etc.)
- Revisit architecture if multiple services need to talk to the ESP32

