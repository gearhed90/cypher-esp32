# Cypher Hardware — Body, Tracks & Power

**Last Updated:** July 30, 2026  
**Body:** V3 (central body + modular track modules)  
**Current Running Configuration:** Still wheeled while tracked modules are finished

---

## 1. Body V3 Structure

- **Central body** — houses electronics, motors, power distribution, battery, converter
- **Track modules** (left/right) — framework for tensioner carriage, suspension wheels, track path
- **Drive sprockets** mount on the motor shafts (motors stay in the central body)
- **Top cover** — planned as four pieces (front central, rear central, left fender, right fender), magnetic attachment; cosmetic, lowest priority

### Electronics & Camera Layout
- Main electronics stay in the **center channel**
- **Camera + pan-tilt head** on a **pedestal** rising from the center channel
- ESP32/Pi controller stack mount: **designed**
- Battery + Drok placement: **decided**, tray still to design
- Charge port + power switch: **back panel**

---

## 2. Camera Pedestal & Pan-Tilt

| Item | Status |
|------|--------|
| Pedestal (first version) | Done |
| Pan drive | **Direct drive** (belt drive dropped) |
| Pan servo mount | Cross member in the pedestal |
| Tilt servo | In the camera head |
| Tilt linkage | Below pivot line, attaches to the rotating base |

Pan/tilt GPIO: Pan = 12, Tilt = 13 (locked). GPIO 12 is a strapping pin — boot must not be held in a bad state.

---

## 3. Track System (High-Level — details in track thread)

- **Type:** Segmented track (PLA for now; TPU later possible). One track already printed and tested.
- **Modules:** Modular assemblies with proper end-supported axles
- **Axles:** 4× 60 mm fixed end-supported, dual 624ZZ bearings per wheel, set-screw lock + printed spacers
- **Drive:** Motor shaft → flanged hub → spacer → sprocket hub → drive sprocket (motors in body)
- **Tensioner:** Previous center-support / clamp design is obsolete. New design is a carriage with adjustable bearing on a ramp (side-to-side adjustment pushes carriage out or allows it in). Details live in the track thread.

---

## 4. 5 V Power Architecture (Foundation — Locked)

**Battery:** 12 V pack  
**Primary 5 V converter (in use):** existing **Drok**  
**Upgrade candidate:** TOBSUN EA75-5V if needed later

- Single 5 V source → short distribution rail / bus in the center channel
- Branches: Brain (Pi/ESP32/camera), Actuators (servos/laser), future LEDs/sensors
- Local capacitors at spike points retained
- Extra fusing deferred until longer run times
- Motors on 12 V via TB6612; chassis fans (if added) on 12 V

---

## 5. Pin Map (ESP32)

### Motors (TB6612FNG) — Locked
| Function | GPIO |
|----------|------|
| Left AIN1 / AIN2 / PWMA | 25 / 26 / 27 |
| Right BIN1 / BIN2 / PWMB | 33 / 32 / 14 |

### UART to Pi — Locked
| ESP32 | Pi |
|-------|-----|
| TX 18 | GPIO 10 (RX) |
| RX 19 | GPIO 8 (TX) |

### Pan-Tilt — Locked
| Function | GPIO | Notes |
|----------|------|-------|
| Pan | 12 | Strapping pin — protect boot |
| Tilt | 13 | |

### Laser — Provisional
| Function | GPIO |
|----------|------|
| KY-008 | 4 |

---

## 6. Boot Policy

**Always boot to Manual + Stopped.**

---

## 7. Central Body Checklist (for track testing)

| Item | Status |
|------|--------|
| Motor mounting | Done |
| ESP32/Pi stack mount | Designed |
| Camera pedestal v1 | Done |
| Pan = direct drive on cross member | Locked |
| Tilt = head-mounted servo + linkage | Locked (detail design open) |
| Battery + Drok tray | Placement decided, tray to design |
| 5 V / ground bus board | Not started |
| Charge port + power switch (back panel) | Decided, simple |
| Wiring paths / strain relief | Open |
| Top cover (4-piece, magnets) | Lowest priority / cosmetic |

---

## 8. Change Log

| Date | Change |
|------|--------|
| July 24 2026 | 5 V architecture, pan/tilt pins, boot policy, center-channel layout |
| July 27 2026 | Modular track assemblies, axle system, segmented track; old tensioner obsolete |
| July 30 2026 | Body V3; pedestal v1; direct-drive pan; tilt linkage concept; ESP32/Pi mount; back-panel power |

---

**Status:** Central body is the critical path for full track testing. Pedestal and controller mount are in place; battery/Drok tray and servo mounting details are the next design work.
