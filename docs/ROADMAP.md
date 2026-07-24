# Cypher Robot — Development Roadmap

**Last Updated:** July 24, 2026

## Core Philosophy

Stable, predictable manual control first. New features are layered on top; they do not rewrite the core.

## Foundation Definition

The robot is considered past Foundation when:

- A human can reliably drive it remotely
- It always boots to Manual + Stopped
- Power is clean and documented
- Core docs match reality
- Sensors and higher features can be added without touching motor control

## Phase 1 — Foundation (Active)

**Done**
- Clean ESP32 motor controller
- Dashboard owns motors (buttons, keyboard, discrete speed)
- UART protocol + safety timeout
- Documentation lock-in
- Track tensioner design
- 5 V converter choice (TOBSUN)
- Pan/Tilt pins locked (12/13)
- Boot policy: always Manual + Stopped
- Electronics layout concept (center channel + camera post)

**Still open**
- Laser pin confirmation
- Detailed 5 V distribution (deeper discussion needed)
- Remote-access hardening → thread “Cypher Remote Control”
- Motor balancing / smooth open-loop feel (discussion needed)
- Systemd enforcement of boot-to-stopped

## Phase 2 — Sensors & Closed-Loop (next major design)
- Hall sensors + AS5600
- Pi-side straight-line assist
- Rear ToF / ultrasonic, later lidar
- All sensing stays on the Pi

## Phase 3 — Mechanical completion
- Full tracked modules
- Final body / channel details

## Phase 4 — Future utilities
- Groove LEDs / status lighting
- Laser cat-play mode
- Retractable arms
- Vision tracking and limited autonomy

---

Priority remains finishing the remaining Foundation gaps before opening the sensor thread in earnest.
