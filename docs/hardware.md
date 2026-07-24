# Cypher Hardware — Chassis & Tracks

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

## 4. Change Log

| Date          | Change                                                                 | Notes |
|---------------|------------------------------------------------------------------------|-------|
| June 23 2026  | Major pivot to continuous TPU track + slot/groove drive               | Previous segmented track archived |
| June 29 2026  | Body Design V2 direction started (low-profile angular, inboard pockets)| Active body direction |
| July 23 2026  | Switched tensioner from spring to rigid adjustable                     | Springs over-compressed |
| July 24 2026  | Track tensioner design locked (rigid sliding bar + dual M3 clamp)      | Current |

---

**Status:** Tensioner locked. Continue with wheel/axle details, sprocket confirmation, and full track geometry while the software Foundation is finished.
