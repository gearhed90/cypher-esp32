# Cypher — Current State

**Last Updated:** August 22, 2026  
**Phase:** Foundation

## Working

- UART motors + pan/tilt on ESP32 (explicit Serial2 pins RX=19, TX=18)
- Dashboard drive UI + hold-to-repeat pan/tilt via bridge
- 1.5 s motor safety timeout; heartbeat ~800 ms
- Servo limits ±45° pan / ±9° tilt; rate-limited motion; axis invert in firmware
- `PT_SAVE_BOOT` / NVS boot pose; `PT_CENTER`, `PT_SLEEP`
- Camera Module 3 stream: 1280×720, q=85, correct colors (no channel swap on this Pi)
- Tailscale remote access to dashboard and stream
- Track modules functional; tensioner implemented; rover driven from dashboard

## Firmware

- `firmware/src/main.cpp`: motors + ESP32Servo pan/tilt, NVS, invert flags
- Must flash with PlatformIO + `ESP32Servo` lib; Serial2 pins required

## Dashboard / services

| Service | Role |
|---------|------|
| `cypher-dashboard.service` | UI + UART bridge |
| `cypher-stream.service` | MJPEG on :8080 |
| `cypher-bridge.service` | Unused (bridge in-process) |
| `sentry-tracker.service` | **Keep stopped/disabled** while using Cypher (holds camera, sends competing servo/motor commands) |

Stream URL (example): `CYPHER_STREAM_URL=http://100.70.99.34:8080/stream` in `pi/dashboard/.env`.

## Access

- Dashboard: `http://100.70.99.34:5000` or `http://cypher:5000`
- Stream: `http://100.70.99.34:8080/stream`

## Known gaps / next

1. Mechanical: tilt linkage / horn alignment for true optical center; head aim for desired FOV
2. Optional motor wire swap if drive direction still reversed after software invert of servos only
3. Lid + power distribution polish
4. Disk space on Pi root was critically full during bring-up — monitor `df -h`
5. Motor balancing parked until needed
6. Do not enable sentry-tracker alongside Cypher stream/control without a shared camera design

## Recently closed (this thread)

- Pan/tilt moved from Pi GPIO to ESP32 hardware PWM
- UART pin fix; servo motion confirmed quiet under continuous hold
- Bridge + dashboard API on UART; hold-to-repeat UI
- Stream service + color path verified

---

See [UART_PROTOCOL.md](UART_PROTOCOL.md) · [ARCHITECTURE.md](ARCHITECTURE.md) · [SETUP.md](SETUP.md)
