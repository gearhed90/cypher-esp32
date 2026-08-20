# Cypher — Current State

**Last Updated:** August 20, 2026  
**Phase:** Foundation  
**Source:** High-level project hub (this thread) + repo reality

## Working / locked (software & architecture)

- UART protocol + 1.5 s safety timeout
- ESP32 pure motor controller (no WiFi / web / OTA)
- Dashboard owns motors (mobile sliders, desktop sticks/keyboard, discrete speed steps)
- Pan/tilt on **Pi** (BCM 18 pan, 17 tilt); ESP32 no longer drives servos
- Boot policy: always Manual + Stopped
- Architecture: Pi = brain; ESP32 = motors only; GitHub = source, not live UI host

## Working / locked (hardware — high level)

- Body **V3**: central body + modular track modules
- Track type: **segmented** (PLA proven; TPU production direction); modular end-supported axles
- Tensioner: **carriage + adjustable bearing on ramp** (old sliding-bar/clamp design obsolete)
- Drive: motors in body → flanged hub → spacer → sprocket hub → drive sprocket
- 5 V: **Drok in use**; short distribution rail planned; TOBSUN = upgrade candidate only
- Electronics in center channel; camera on pedestal; charge port + power switch on back panel
- ESP32/Pi stack mount designed; pedestal v1 done; battery/Drok placement decided (tray TBD)

## Foundation definition

1. Reliably controllable by a human over a remote link  
2. Safe on every boot (motors off, manual)  
3. Documented accurately  
4. Powered cleanly enough for daily use  
5. Ready for sensors/features without rewriting motor control  

Does **not** require closed-loop drive, obstacle avoidance, LEDs, arms, or autonomy.

## Remaining Foundation gaps (hub view)

| Item | Status | Owner |
|------|--------|--------|
| Pan/tilt electrical bring-up (shake / limits / pulse range) | In progress | **Hardware thread** |
| Field + Tailscale access (AP, deck, PWA modes) | Design in progress | **Remote-access thread** |
| Battery/Drok tray, 5 V bus board, wiring/strain relief | Open | Hardware / body |
| Systemd enforce boot-to-stopped | Policy locked; implement pending | Pi / dashboard |
| Laser pin | Provisional | Hardware |
| Motor balancing / open-loop trim | **Parked until tracks on** | Hub |
| Hall wheel-speed (A3144, 6 magnets/side, ~2 mm gap) | Planned for body; not closed-loop yet | Sensors / body |

## Explicitly out of Foundation / parked

- AS5600 (dropped for now — no viable magnet mount on shaft)
- Closed-loop straight assist (Pi-side later; needs reliable halls)
- Obstacle ToF/lidar, groove LEDs, cat-play, retractable arms, autonomy

## Thread ownership

| Thread | Scope |
|--------|--------|
| **This hub** | High-level decisions, phase, prioritization, doc coherence |
| Hardware | Servos, power wiring, body details, pan/tilt debug |
| Remote access | Tailscale, Cypher-Setup AP, cyberdeck link, PWA Direct vs Tailscale |
| Sensors | Hall/odometry, closed-loop, future perception |
| Track | Module geometry, tensioner, TPU links |

---

See [ROADMAP.md](ROADMAP.md) · [ARCHITECTURE.md](ARCHITECTURE.md) · [hardware.md](hardware.md) · [cypher-remote-access.md](cypher-remote-access.md)
