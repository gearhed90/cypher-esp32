# Cypher — Current State

**Last Updated:** July 24, 2026  
**Phase:** Foundation

## Working

- UART command protocol (`MOVE`, `STOP`, `HEARTBEAT`, `STATUS?`) on ESP32
- 1.5-second safety timeout on the ESP32
- ESP32Bridge with automatic heartbeat (~800 ms)
- **Dashboard owns motor control** — on-screen D-pad, speed slider, keyboard arrows + Space, emergency stop
- API endpoints `/api/move`, `/api/stop`, `/api/status`
- Camera stream embedding (when stream service is running)
- Graceful offline mode when the serial port cannot be opened

## Firmware Status

- ESP32 is a pure UART motor controller (WiFi / WebServer / OTA removed).

## Dashboard Status

The dashboard is now the single control interface:
- Live camera feed
- Directional buttons (hold to drive, release to stop)
- Keyboard support (arrows + Space)
- Speed slider (live update while moving)
- Connection status indicator

## Hardware Progress (July 2026)

- Track tensioner design **locked**: rigid sliding bar + dual M3 clamp, ~30 mm travel
- Continuous TPU track direction remains the target
- Body still on wheeled platform while tracked modules are finalized

## Known Gaps / Foundation Work Remaining

1. **Remote access hardening** — reliable Tailscale + optional nginx to the dashboard.
2. **Motor balancing / smooth control** — refine throttle/steering response and mechanical trim.
3. **Clean power distribution & lid electronics**.
4. Mechanical track completion (tensioner wheel, sprocket, full modules).
5. On the Pi: ensure the `sentry` user is in the `dialout` group so `/dev/serial0` is accessible.

## Services Snapshot

| Service | Status | Notes |
|---------|--------|-------|
| `cypher-dashboard.service` | Available | Starts UI + owns the serial bridge |
| `cypher-bridge.service` | Stopped | Intentionally unused |

## Access

- Local dashboard: `http://cypher:5000`
- Remote: via Tailscale to the Raspberry Pi

---

See [ROADMAP.md](ROADMAP.md) and [cypher-remote-access.md](cypher-remote-access.md).
