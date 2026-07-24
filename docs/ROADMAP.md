# Cypher Robot — Development Roadmap

**Last Updated:** July 24, 2026

## Core Philosophy

The foundation of this project is **stable, predictable manual control**.

Motor control, basic movement, and the communication layer between the Pi and ESP32 must remain reliable. New features (especially autonomous behaviors or complex mechanisms) are built **on top** of this foundation rather than modifying the core movement logic directly.

## Current Phase: Foundation (Active)

Focus areas that must be solid before adding complex features:

- Reliable remote access to the dashboard
- Smooth and balanced motor control
- Clean ESP32 firmware (remove residual web-server code)
- Proper, up-to-date documentation
- Clean power distribution and lid-mounted electronics + cooling

## Roadmap

### Phase 1: Stable Manual Foundation — Largely Complete
- [x] Remove autonomous / straight-tracking logic from ESP32
- [x] Establish clean manual tank-drive control
- [x] Project reorganization (`firmware/` + `pi/`)
- [x] Basic UART protocol + heartbeat + safety timeout
- [ ] Remove residual WiFi/WebServer code from ESP32 firmware
- [ ] Final documentation lock-in (this commit)

### Phase 2: Reliability & Boot Behavior
- [ ] Harden systemd services (dashboard auto-start, logging, restart-on-failure)
- [ ] Safe default boot state (always Manual + Stopped)
- [ ] Robust serial auto-reconnect and health reporting
- [ ] Clean power distribution and lid electronics layout

### Phase 3: Remote Access & Observability
- [ ] Reliable Tailscale + nginx access to the **dashboard**
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
- Retractable / foldable arms (see `future_utilities_roadmap.md`)
- Carefully re-introduce limited autonomy **on top of** the stable base
- Enhanced UI feedback and telemetry

## Guiding Principles

1. **Protect the Foundation** — treat motor control and basic movement as protected code.
2. **Layered Architecture** — new capabilities talk to motors only through the UART protocol.
3. **Reproducibility** — the repository should allow recreating the system with reasonable effort.
4. **Incremental Progress** — small, testable steps.
5. **Documentation stays current** — every meaningful decision is reflected in the docs.

---

This roadmap evolves with the project. The priority remains finishing Foundation before expanding scope.
