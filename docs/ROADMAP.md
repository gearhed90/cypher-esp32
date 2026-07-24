# Cypher Robot — Development Roadmap

**Last Updated:** July 24, 2026

## Core Philosophy

The foundation of this project is **stable, predictable manual control**.

Motor control, basic movement, and the communication layer between the Pi and ESP32 must remain reliable. New features are built **on top** of this foundation rather than modifying the core movement logic directly.

## Current Phase: Foundation (Active)

## Roadmap

### Phase 1: Stable Manual Foundation
- [x] Remove autonomous / straight-tracking logic from ESP32
- [x] Establish clean manual tank-drive control on the ESP32 side
- [x] Project reorganization (`firmware/` + `pi/`)
- [x] Basic UART protocol + heartbeat + safety timeout
- [x] Remove residual WiFi/WebServer/OTA code from ESP32
- [x] Documentation lock-in
- [x] Wire ESP32Bridge into the dashboard UI (buttons + keyboard → MOVE/STOP)

### Phase 2: Reliability & Boot Behavior
- [ ] Harden systemd services (dashboard auto-start, logging, restart-on-failure)
- [ ] Safe default boot state (always Manual + Stopped)
- [ ] Robust serial auto-reconnect and health reporting
- [ ] Clean power distribution and lid electronics layout
- [ ] Ensure `sentry` user is in `dialout` for serial access

### Phase 3: Remote Access & Observability
- [ ] Reliable Tailscale + nginx access to the dashboard
- [ ] Simple robot status page (ESP32 health, services, camera, battery later)
- [ ] Documented recovery procedures for ESP32 and Pi

### Phase 4: Mechanical Completion (Tracks)
- [x] Track tensioner design locked (rigid sliding bar + dual M3)
- [ ] Finalize tensioner wheel + axle retention
- [ ] Finalize continuous TPU track geometry and sprocket
- [ ] Suspension geometry and travel
- [ ] Full tracked modules installed and tested

### Phase 5: Future Capabilities (After Foundation)
- Vision / object tracking
- Retractable / foldable arms
- Carefully re-introduce limited autonomy on top of the stable base
- Enhanced UI feedback and telemetry

## Guiding Principles

1. Protect the Foundation.
2. Layered architecture — new capabilities talk to motors only through UART.
3. Reproducibility.
4. Incremental progress.
5. Documentation stays current.

---

Priority remains finishing Foundation before expanding scope.
