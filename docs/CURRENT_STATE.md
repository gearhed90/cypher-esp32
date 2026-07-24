# Cypher — Current State

**Last Updated:** July 24, 2026  
**Phase:** Foundation

## Working

- UART command protocol (`MOVE`, `STOP`, `HEARTBEAT`, `STATUS?`) fully implemented on ESP32
- 1.5-second safety timeout on the ESP32
- ESP32Bridge class with automatic heartbeat (~800 ms)
- `cypher-dashboard.service` can start the monitoring interface
- Camera stream embedding in the dashboard (when stream service is running)

## Firmware Status (July 24 2026)

- **ESP32 is now a pure motor controller.**  
  Residual WiFi, WebServer, OTA, HTML UI, and hardcoded credentials have been removed.  
  The firmware only listens on UART and drives the motors with the safety timeout.

## Dashboard Status (Accurate)

The current dashboard is a **monitoring / status page**:
- Live camera stream
- Link button that opens the control interface

Full on-screen directional buttons + keyboard control that talk directly to the ESP32Bridge are **not yet wired into the dashboard UI**. That integration remains a Foundation task.

## Hardware Progress (July 2026)

- Track tensioner design **locked**: rigid sliding bar + dual M3 clamp, ~30 mm travel
- Continuous TPU track direction remains the target mechanical configuration
- Body still on wheeled platform while tracked modules are finalized

## Known Gaps / Foundation Work Remaining

1. **Dashboard control integration** — wire the ESP32Bridge into the dashboard so buttons/keyboard send `MOVE`/`STOP` directly (instead of linking out to an old web UI).
2. **Remote access hardening** — reliable Tailscale + optional nginx access to the dashboard.
3. **Motor balancing / smooth control** — refine throttle/steering response and any mechanical trim.
4. **Clean power distribution & lid electronics**.
5. Mechanical track completion (tensioner wheel, sprocket, full modules).

## Services Snapshot

| Service | Status | Notes |
|---------|--------|-------|
| `cypher-dashboard.service` | Available | Starts the monitoring UI |
| `cypher-bridge.service` | Stopped | Intentionally unused for now |

## Access

- Local dashboard: `http://cypher:5000`
- Remote: via Tailscale to the Raspberry Pi

## Notes

- All production motor commands should go through UART from the Pi.
- Future features (vision, arms, autonomy) stay parked until the Foundation is solid.

---

See [ROADMAP.md](ROADMAP.md) for the phased plan and [cypher-remote-access.md](cypher-remote-access.md) for recovery procedures.
