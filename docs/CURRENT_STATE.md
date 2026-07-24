# Cypher — Current State

**Last Updated:** July 24, 2026  
**Phase:** Foundation

## Working

- UART command protocol and 1.5 s safety timeout
- ESP32 pure motor controller (no WiFi / web server)
- Dashboard owns motor control (D-pad, keyboard, 10 % speed steps via number keys)
- Track tensioner design locked
- 5 V converter decision locked (TOBSUN EA75-5V)
- Pan/Tilt pins locked (GPIO 12 / 13)
- Boot policy locked: always Manual + Stopped
- High-level electronics layout: center channel + camera post

## Foundation Definition (Review)

Foundation means the robot is:

1. Reliably controllable by a human over a remote link
2. Electrically and mechanically safe on every boot (motors off, manual mode)
3. Documented accurately
4. Powered cleanly enough for daily use
5. Ready for sensors and higher features to be added without rewriting the core

It does **not** require closed-loop driving, obstacle avoidance, LEDs, arms, or autonomy.

## Remaining Foundation Gaps

| Item | Status |
|------|--------|
| Laser pin confirmation | Provisional (GPIO 4) |
| Detailed 5 V distribution (wiring, fusing, injection) | Needs deeper discussion |
| Remote-access hardening | Owned by thread “Cypher Remote Control” |
| Motor balancing / smooth open-loop feel | Needs discussion |
| Systemd hardening to enforce boot-to-stopped | Confirmed as required; implementation pending |
| Lid / channel mechanical details | Concept locked; detailed design later |

## Future (explicitly out of Foundation)

- Hall + AS5600 + closed-loop straight assist
- Obstacle avoidance / lidar / ToF
- Groove LEDs
- Cat-play laser mode
- Retractable arms
- Full tracked modules
- Vision tracking / autonomy

---

See [ROADMAP.md](ROADMAP.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
