# Cypher Hardware — Chassis, Tracks & Power

**Last Updated:** July 24, 2026  
**Current Mechanical Focus:** Tracked drive system — tensioner design locked  
**Current Running Configuration:** 2-wheel differential drive + casters (tracked modules still in progress)

---

## 1. Track Tensioner (Final Design — Locked)

**Type:** Fully rigid adjustable (no springs)

**Mechanism**
- Sliding bar (same geometry previously tested with the spring version)
- Clamp with **two M3 screws** (clamp body lengthened to accept the second screw)
- Tight sliding fit in the middle suspension mount for guidance and anti-rotation

**Key Specs**
- Travel: ~30 mm (excess capacity; 10–12 mm is sufficient)
- Clamp hardware: 2× M3
- Access: Easy — outer side plate removes with the top cover for maintenance and adjustment

**Rationale**
- A sliding carriage between side plates was not practical because the tensioner axle is supported from the middle suspension mount.
- The existing rounded/sliding bar style already proved stable. Tight tolerances + dual M3 clamp give sufficient anti-rotation and holding force.
- Over-built clamp preferred rather than risking slip under load.

**Status:** Design locked. Ready for final modeling and testing.

### Related Open Items
- Final tensioner wheel + axle retention details
- Track segment / continuous track finalization (pitch, lug geometry)
- Drive sprocket tooth / groove profile confirmation
- Suspension wheel positions and travel

---

## 2. Target Configuration — Continuous TPU Tracked Drive

### Design Goals
- Switch to a tracked (tank-style) platform for better terrain capability and stability.
- One-piece continuous TPU track (no segmented links or pins).
- Keep overall height low and CG central.
- Motors remain in the main chassis (not on the track modules) to keep heavy mass low and central.

### Track Specifications (Baseline)

| Parameter                    | Value                          |
|------------------------------|--------------------------------|
| Style                        | One-piece continuous TPU       |
| Pitch diameter (reference)   | 215 mm                         |
| Number of drive lugs         | 45                             |
| Pitch                        | 15 mm                          |
| Approximate circumference    | ~675 mm                        |
| Overall track width          | 50 mm                          |
| Base thickness               | ~3.5–4 mm                      |

**Drive lugs (inner face)**  
Width 25 mm (centered), length 6 mm, height 6 mm, 1.5° draft, chamfers/fillets for printability.

**Side lips**  
4 mm thick, 4.5 mm high, ~42 mm inner width between lips.

**Outer tread**  
Chevron pattern, edges chamfered.

### Drive Method
Slot / groove drive: lugs drop into matching grooves on the sprocket.

### Sprocket Baseline
- Pitch diameter ~95 mm, 20 grooves
- Groove width 27 mm, depth 8 mm
- Side flanges ~7 mm tall
- 6 mm bore with setscrew (or key)

### Motor Integration
- Existing Greartisan 12 V 300 rpm gear motors initially
- Motors stay in the main chassis
- Power transferred to sprocket axle via short shaft + flexible coupling (or equivalent alignment-tolerant method)

---

## 3. Current Running Configuration (Wheeled)

- Drive: 2-wheel differential + rear casters
- Wheels: 200 mm diameter × 40 mm wide
- Motors: Greartisan 12 V 300 rpm, 1:17.4 reduction
- Battery: 12 V pack, position iterated for CG
- Chassis: 3D-printed PLA, bowl-style body with wheel wells

This configuration remains the daily driver while tracked modules are finished.

---

## 4. 5 V Power Architecture (Foundation — Locked)

**Battery:** 12 V pack  
**Primary 5 V converter (in use):** existing **Drok** buck converter  
**Upgrade candidate:** TOBSUN EA75-5V (if the Drok runs out of headroom or runs hot under longer duty cycles)

### Distribution plan
- Single 5 V source (the Drok) feeding a **short distribution rail / bus** in the center channel.
- Loads take short dedicated branches off the rail.
- Logical branches (can be added as needed):
  - **Brain** — Pi + ESP32 + camera
  - **Actuators** — pan/tilt servos + laser
  - **Future LEDs** — groove strip when added
  - **Sensors / misc** — ToF, hall, AS5600, etc.
- Local capacitors already placed at spike-prone points are retained.

### Protection
- Current setup has had no issues in normal use.
- Pi has its own case fan; no chassis fans fitted yet.
- Extra input/output fusing and per-branch protection will be added later when the robot runs for longer periods. Not required to call this Foundation decision locked.

### Loads on 5 V vs 12 V
| Load | Rail |
|------|------|
| Raspberry Pi 4 | 5 V |
| ESP32 | 5 V |
| Camera | 5 V |
| Pan/tilt servos | 5 V |
| Laser | 5 V |
| Future LEDs / sensors | 5 V |
| Drive motors (TB6612) | 12 V |
| Chassis fans (if added) | 12 V |

### Status
High-level architecture locked. Physical rail, branch wiring, and fusing details belong in an implementation pass when ready.

---

## 5. Electronics & Camera Layout (High-Level)

- **Main electronics** (Pi, ESP32, motor driver, power conversion, future sensor electronics) stay in the **center channel**.
- **Camera + pan-tilt head** mount on a **post rising from the center channel**.
- This keeps mass low/central while giving the camera a clear elevated viewpoint and clean mechanical separation from the drive system.

---

## 6. Pin Map (ESP32)

### Motors (TB6612FNG) — Locked

| Function     | GPIO |
|--------------|------|
| Left AIN1    | 25   |
| Left AIN2    | 26   |
| Left PWMA    | 27   |
| Right BIN1   | 33   |
| Right BIN2   | 32   |
| Right PWMB   | 14   |

### UART to Raspberry Pi — Locked

| Function | ESP32 GPIO | Pi side        |
|----------|------------|----------------|
| TX       | 18         | GPIO 10 (RX)   |
| RX       | 19         | GPIO 8  (TX)   |

### Pan-Tilt Servos — Locked

| Function   | GPIO | Notes |
|------------|------|-------|
| Pan servo  | 12   | Strapping pin. Firmware/boot must ensure it is not held in a state that prevents normal boot. |
| Tilt servo | 13   | |

### Laser — Provisional

| Function       | GPIO | Notes |
|----------------|------|-------|
| Laser (KY-008) | 4    | Simple on/off. Still provisional until confirmed on hardware. |

---

## 7. Boot Policy (Foundation)

**Always boot to Manual + Stopped.**

Motors must be off and the system must be in manual control mode after every power-up or service restart until an explicit command is received. This is a hard Foundation requirement.

---

## 8. Change Log

| Date          | Change                                                                 | Notes |
|---------------|------------------------------------------------------------------------|-------|
| June 23 2026  | Major pivot to continuous TPU track + slot/groove drive               | |
| June 29 2026  | Body Design V2 direction started                                       | |
| July 23 2026  | Switched tensioner from spring to rigid adjustable                     | |
| July 24 2026  | Track tensioner design locked                                          | |
| July 24 2026  | Pan/Tilt pins locked (12/13); laser still provisional                  | |
| July 24 2026  | Electronics stay in center channel; camera/servo on post from channel  | |
| July 24 2026  | Boot policy locked: always Manual + Stopped                            | |
| July 24 2026  | 5 V architecture locked: Drok (current) → short rail; protection later | TOBSUN = upgrade path |

---

**Status:** Tensioner, 5 V architecture, pan/tilt pins, layout concept, and boot policy locked. Laser pin still provisional. Detailed rail/fusing is implementation work.
