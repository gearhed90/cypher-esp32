# Cypher Robot - Development Roadmap

## Core Philosophy

The foundation of this project is **stable, predictable manual control**. 

Motor control, basic movement, and the communication layer between the Pi and ESP32 must remain reliable. New features (especially autonomous behaviors) should be built **on top** of this foundation rather than modifying the core movement logic directly.

## Current Status (June 2026)

- ✅ Clean manual-only ESP32 firmware (all autonomous/straight-tracking code removed)
- ✅ Project reorganized into a maintainable structure (`firmware/` + `pi/`)
- ✅ Repository cleaned up (venv, build artifacts, and unused folders removed)
- ✅ Basic documentation added

## Roadmap

### Phase 1: Stable Foundation (Completed)
- Remove all autonomous / straight tracking logic from ESP32
- Establish clean, simple manual tank drive control
- Basic web UI on the ESP32 for manual control
- Project reorganization and cleanup

### Phase 2: Pi ↔ ESP32 Communication (Next Priority)
- Design a clean, versioned UART command protocol
- Implement reliable command sending from the Raspberry Pi to the ESP32
- Add heartbeat / connection monitoring between Pi and ESP32
- Allow the Pi to safely control motors without directly modifying motor code
- Create a stable bridge layer that future features can use

### Phase 3: System Reliability & Boot Behavior
- Create systemd services for:
  - Flask dashboard
  - Pi ↔ ESP32 communication bridge
- Ensure everything starts automatically and reliably on boot
- Implement safe default boot state (always start in **Manual + Stopped**)
- Add proper logging and automatic restart on failure

### Phase 4: Remote Access & Observability
- Improve Tailscale reliability and auto-connection
- Create a simple **Robot Status page** on the Pi (shows health of ESP32, services, camera, etc.)
- Improve nginx reverse proxy setup
- Better remote debugging and monitoring tools

### Phase 5: Future Capabilities (Later)
- Carefully reintroduce tracking / autonomous behaviors **on top** of the stable base
- Improve camera streaming and integration
- Enhance the web UI (better controls, status feedback, etc.)
- Explore more advanced features while protecting core movement stability

## Guiding Principles

1. **Protect the Foundation** — Motor control and basic movement should be treated as protected code.
2. **Layered Architecture** — New capabilities should interact with the motor layer through clean interfaces when possible.
3. **Reproducibility** — The repository should allow someone to recreate the full system with reasonable effort.
4. **Incremental Progress** — Add features in small, testable steps rather than large risky changes.

## Notes

This roadmap may evolve as the project progresses. The priority is to first build a rock-solid manual control system before layering on more complex behaviors.

---

Last updated: June 2026
