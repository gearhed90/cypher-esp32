# Cypher Hardware — Body, Tracks & Power

**Last Updated:** August 20, 2026  
**Body:** V3 (central body + modular track modules)  
**Running config:** Moving to tracked modules; segmented track in work  
**Note:** Deep servo/power debug → hardware implementation thread. This file is the hub-level hardware record.

---

## 1. Body V3 Structure

- **Central body** — electronics, motors, power distribution, battery, converter
- **Track modules** (L/R) — tensioner carriage, suspension wheels, track path
- **Drive sprockets** on motor shafts (motors stay in central body)
- **Top cover** — four pieces (front central, rear central, side fenders), magnetic attachment; cosmetic, lowest priority

### Electronics & camera layout
- Main electronics in the **center channel**
- **Camera + pan-tilt** on a **pedestal** from the center channel
- ESP32/Pi stack mount: designed
- Battery + Drok: placement decided; tray TBD
- Charge port + power switch: **back panel**

---

## 2. Camera pedestal & pan-tilt

| Item | Status |
|------|--------|
| Pedestal v1 | Done |
| Pan | Direct drive, servo on pedestal cross member, bearings |
| Tilt | Direct drive on tilt pivot, bearings (linkage dropped) |
| **Control** | **Raspberry Pi** — not ESP32 |
| Pan GPIO (BCM) | **18** |
| Tilt GPIO (BCM) | **17** |
| Power | 5 V rail (not Pi 5 V pin); common GND with Pi |

Software: `pi/dashboard/servo_control.py`, `/api/pan_tilt`. Center-on-start is configurable (`CYPHER_SERVOS_CENTER_ON_START`). Travel limits via env min/max after mechanical teach-in.

**Bring-up note (Aug 2026):** Pan one-way + shake under investigation in hardware thread (pulse range, ground, possible servo damage). Not a closed hub issue.

---

## 3. Track system (high-level — detail in track thread)

- **Type:** Segmented (PLA proven; TPU production direction; pin retention work ongoing)
- **Modules:** End-supported axles (4× 60 mm, dual 624ZZ per wheel, set-screw + spacers)
- **Drive:** Motor shaft → flanged hub → spacer → sprocket hub → drive sprocket
- **Tensioner:** Carriage with adjustable bearing on a **ramp** (old clamp/sliding-bar design obsolete)

### Wheel-speed sensing (planned)
- **A3144** halls, labeled face toward magnet, ~1.5–2.5 mm gap
- **6 magnets** per side on ~32.3 mm path diameter; same polarity (south to sensor)
- AS5600 **dropped for now** (no viable shaft magnet mount)
- Wiring to **Pi** (5 V VCC, OUT pulled to 3.3 V)

---

## 4. 5 V power (Foundation — locked)

| Item | Decision |
|------|----------|
| Battery | 12 V pack |
| Converter **in use** | **Drok** |
| Upgrade candidate | TOBSUN EA75-5V if headroom/heat requires |
| Topology | Single source → short **rail/bus** in center channel |
| Branches | Brain / Actuators / future LEDs / sensors |
| Protection | Extra fusing deferred until longer duty cycles |
| Motors | 12 V via TB6612 |
| Fans (if any) | 12 V |

---

## 5. Pin map

### ESP32 — motors (TB6612) locked
| Function | GPIO |
|----------|------|
| Left AIN1 / AIN2 / PWMA | 25 / 26 / 27 |
| Right BIN1 / BIN2 / PWMB | 33 / 32 / 14 |

### ESP32 ↔ Pi UART locked
| ESP32 | Pi |
|-------|-----|
| TX 18 | (see install; often serial0 mapping) |
| RX 19 | |

### Pan/tilt — Pi (not ESP32)
| Function | BCM |
|----------|-----|
| Pan | 18 |
| Tilt | 17 |

### Laser — provisional
| Function | Notes |
|----------|--------|
| KY-008 | Pin TBD (was ESP32 4; may move with Pi actuators) |

---

## 6. Boot policy

**Always boot to Manual + Stopped** (motors off until commanded).

---

## 7. Central body checklist

| Item | Status |
|------|--------|
| Motor mounting | Done |
| ESP32/Pi stack mount | Designed |
| Camera pedestal v1 | Done |
| Pan/tilt direct drive + bearings | Locked mechanically |
| Pan/tilt on Pi GPIOs | Locked |
| Battery + Drok tray | Placement decided; design open |
| 5 V / GND bus board | Open |
| Charge port + power switch | Back panel |
| Hall magnet path / mounts | Planned |
| Wiring / strain relief | Open |
| Top cover | Lowest priority |

---

## 8. Change log

| Date | Change |
|------|--------|
| July 24 2026 | 5 V concept, boot policy, center-channel layout |
| July 27 2026 | Modular tracks, axles, segmented track; old tensioner obsolete |
| July 30 2026 | Body V3; pedestal; direct-drive pan/tilt; Drok vs TOBSUN clarified |
| Aug 13 2026 | TPU track direction; pin retention |
| Aug 16–17 2026 | **Pan/tilt → Pi BCM 18/17**; ESP32 motors-only |
| Aug 20 2026 | Hub doc sync; hall plan (6× A3144); servo debug owned by hardware thread |

---

**Status:** Mechanical and power architecture locked at hub level. Servo electrical bring-up and fine body CAD live in the hardware thread.
