# Cypher Robot — Development Roadmap

**Last Updated:** August 20, 2026

## Core Philosophy

Stable, predictable manual control first. New features layer on top; they do not rewrite the core.

## Foundation exit criteria

- Human can reliably drive remotely (including a field path when home Wi‑Fi is absent)
- Always boots Manual + Stopped
- Power documented and good enough for daily use
- Core docs match reality
- Sensors/features can be added without touching motor control

## Phase 1 — Foundation (active)

**Done (hub-level)**
- Clean ESP32 motor controller + dashboard motor ownership
- UART protocol + safety timeout
- Pi-centric architecture; pan/tilt moved to Pi GPIOs
- Body V3 concept; modular tracks; ramp/carriage tensioner direction
- 5 V architecture (Drok primary; rail planned)
- Boot policy Manual + Stopped
- Doc lock-in process; implementation split across threads

**Open**
- Finish pan/tilt bring-up (hardware thread)
- Field AP + Tailscale + PWA connection modes (remote-access thread)
- Physical 5 V rail / tray / fusing as needed
- Systemd hardening for boot-to-stopped
- Hall mounts on drive side for later odometry (body/sensors)

## Phase 2 — Sensors & closed-loop
- A3144 hall wheel speed (6 magnets/side planned); AS5600 deferred
- Pi-side straight-line assist after halls proven
- Rear ToF/ultrasonic later; lidar later
- All sensing on Pi

## Phase 3 — Mechanical completion
- Track modules production (TPU links, pin retention)
- Final body/channel/top cover

## Phase 4 — Future utilities
- Groove LEDs, laser cat-play, retractable arms, vision tracking, limited autonomy

---

Hub prioritizes Foundation gaps owned by hardware + remote-access threads before expanding autonomy.
