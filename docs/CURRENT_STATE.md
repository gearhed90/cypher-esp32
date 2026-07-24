# Cypher — Current State

**Last Updated:** July 24, 2026  
**Phase:** Foundation

## Working

- Manual tank-drive control from the Pi dashboard (buttons + keyboard)
- Combined movement (forward + turning simultaneously)
- Speed slider
- UART command protocol (`MOVE`, `STOP`, `HEARTBEAT`, `STATUS?`)
- 1.5-second safety timeout on the ESP32
- Automatic heartbeat from the Pi bridge (~800 ms)
- `cypher-dashboard.service` starts and runs the control interface

## Hardware Progress (July 2026)

- Track tensioner design **locked**: rigid sliding bar + dual M3 clamp, ~30 mm travel
- Continuous TPU track direction remains the target mechanical configuration
- Body still on wheeled platform while tracked modules are finalized

## Known Gaps / Foundation Work Remaining

1. **ESP32 firmware cleanup** — residual WiFi + WebServer code is still present and should be removed so the ESP32 is a pure motor controller.
2. **Remote access hardening** — reliable Tailscale + nginx access to the *dashboard* (not the old ESP32 web UI).
3. **Documentation lock-in** — this set of docs (July 24) is the current single source of truth.
4. **Motor balancing / smooth control** — continue refining throttle/steering response and any mechanical trim.
5. **Clean power distribution & lid electronics** — still part of the Foundation checklist.

## Services Snapshot

| Service | Status | Notes |
|---------|--------|-------|
| `cypher-dashboard.service` | Running | Primary control interface |
| `cypher-bridge.service` | Stopped | Intentionally unused |

## Access

- Local dashboard: `http://cypher:5000`
- Remote: via Tailscale to the Raspberry Pi
- ESP32 is currently often left on USB for monitoring during development

## Notes

- All control traffic goes through the Pi. The ESP32 no longer hosts a production web UI.
- Future features (vision, arms, autonomy) stay parked until the Foundation is solid.

---

See [ROADMAP.md](ROADMAP.md) for the phased plan and [cypher-remote-access.md](cypher-remote-access.md) for recovery procedures.
