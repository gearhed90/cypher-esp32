# Cypher Hardware - Chassis & Tracks

**Last Updated:** June 23, 2026  
**Current Configuration:** 2-wheel differential drive + casters  
**Target Configuration:** Tracked (tank-style) drive system with continuous TPU track

---

## 1. Current Mechanical Configuration (Wheeled)

- **Drive Type:** 2-wheel differential drive with rear casters for stability.
- **Wheels:** 200mm diameter × 40mm wide (currently installed).
- **Motors:** Greartisan 12V 300rpm gear motors with 1:17.4 reduction.
- **Motor Mounting:** Motors are mounted in the chassis with offset output shafts. Currently mounted such that most of the motor mass sits above the axle line.
- **Battery:** 12V battery pack mounted above the axle centerline (position has been adjusted multiple times during testing).
- **Chassis:** 3D printed (PLA), currently a large bowl-style body with wheel wells.

**Notes:**
- The current design has gone through significant iteration around center of gravity and battery positioning to improve balancing behavior.
- The bot is currently using a non-balancing 2-wheel + caster layout.

---

## 2. Target Configuration: Tracked Drive System

### Design Goals
- Switch to a **tracked (tank-style)** platform for better terrain capability and stability.
- Use a **one-piece continuous TPU track** (no segmented links or pins).
- Use the existing Greartisan gear motors initially, with the option to upgrade to larger/higher-torque motors later.
- Maintain a relatively low center of gravity.
- Keep the overall visual width of the track close to the original 40 mm wheels.

### Planned Track Layout (Triangular)

| Position     | Wheel Type     | Diameter      | Function                          | Notes |
|--------------|----------------|---------------|-----------------------------------|-------|
| Rear         | Drive Sprocket | ~95 mm (pitch)| Powered by motor                  | Grooved sprocket for slot/groove drive |
| Front        | Tensioner      | TBD           | Adjustable for track tension      | Smooth or lightly flanged |
| Top          | Idler          | TBD           | Returns the track                 | Smooth or lightly flanged |

### Track Specifications (Continuous Loop)

- **Style:** One-piece continuous TPU track
- **Pitch Diameter (reference circle):** 215 mm
- **Number of Drive Lugs:** 45
- **Pitch:** 15 mm (center-to-center between lugs)
- **Total Track Circumference:** ~675 mm
- **Overall Track Width:** 50 mm
- **Base Thickness:** ~3.5–4 mm

**Drive Lugs (on inner face):**
- Width: **25 mm** (centered)
- Length (travel direction): **6 mm**
- Height (inward protrusion): **6 mm**
- Draft: 1.5° on leading/trailing faces
- Top edges: 1 mm chamfer/radius
- Base fillet: 1–1.5 mm radius

**Side Lips (for lateral guidance):**
- Thickness: **4 mm** each side
- Height above outer face: **4.5 mm**
- Inner width between lips: ~42 mm
- Inner vertical faces: chamfered (0.8–1.0 mm × 45°) for printability

**Outer Tread:**
- Chevron pattern on the ground-contact face
- Edges chamfered for printability and reduced stress

### Drive Method: Slot/Groove

The track uses a **slot/groove** drive system. Drive lugs on the inner face of the track drop into matching grooves on the sprocket. The sides of the grooves push against the lugs to drive the track. This method was chosen for simpler visual appearance and good printability in TPU.

### Sprocket Design (Current Baseline)

- **Pitch Diameter:** 95 mm
- **Number of Grooves:** 20
- **Groove Width:** 27 mm (25 mm lug + 1 mm clearance per side)
- **Groove Depth:** 8 mm (6 mm lug + 2 mm clearance)
- **Groove Profile:** Rectangular with 1.5° draft on vertical walls
- **Side Flanges:** 7 mm tall above groove floor (track lips ride here)
- **Overall Outer Diameter:** ~112–115 mm
- **Hub:** 6 mm bore with flat or keyway + M3/M4 setscrew

### Motor Integration Plans
- Motors will be mounted in the main chassis (not directly on the track module) to keep heavy motor mass centralized and low.
- Power will be transferred to the drive sprocket via a short shaft + flexible coupling (or other alignment-tolerant connection).

### Bearing & Axle Approach
- 6 mm rod used as axles.
- 606 bearings planned.
- Bearings will be mounted in the track frame / chassis side plates.
- Drive sprocket supported on both sides by bearings for rigidity.

---

## 3. Center of Gravity & Weight Distribution
- Primary goal: Keep overall CG as low and central as possible for stability.
- Battery is already well-positioned from prior wheeled iterations — preserve this low/central placement.
- Keeping motors in the main chassis helps significantly with CG and reduces unsprung weight on the tracks.
- Track adds mass at the sides and bottom; design for reasonable wall thickness and infill.

## 4. 3D Printing & Manufacturing Considerations
- **Track:** Print as one continuous loop in TPU. Use 4+ perimeters and high infill (60–100%) on lugs and side lips. Chamfers on lips and lugs improve printability without supports.
- **Sprocket:** Print in PET-CF or strong filament. 4–6 perimeters, 40–60% gyroid infill. Orient for good shear strength on groove walls. Consider a metal sleeve or bushing in the 6 mm bore.
- Prototyping approach: Print the full track first, then the sprocket. Test engagement and fit before committing to final tensioner/idler diameters.

---

## 5. Bill of Materials (Starting)

| Component              | Qty | Material          | Notes / Status                  |
|------------------------|-----|-------------------|---------------------------------|
| Continuous TPU Track   | 2   | TPU (flexible)    | 215 mm diameter, 45 lugs, chevron tread |
| Drive Sprocket         | 2   | PET-CF / Strong filament | 95 mm pitch diameter, 20 grooves |
| Tensioner Wheel        | 2   | PETG / PET-CF     | TBD diameter                    |
| Idler Wheel            | 2   | PETG / PET-CF     | TBD diameter                    |
| 6 mm Axle Rod          | TBD | Steel / Stainless | For sprocket, tensioner, idler  |
| 606 Bearings           | TBD | —                 | For sprocket support            |
| Flexible Coupling      | 2   | —                 | Motor shaft to sprocket axle    |
| M3/M4 Setscrews        | TBD | —                 | For sprocket hub                |

*This is a starting list. Tensioner/idler diameters and exact hardware counts will be added once those parts are designed.*

---

## 6. Open Questions & Decisions Needed

| Topic                              | Current Status                                      | Decision Needed                                      | Priority |
|------------------------------------|-----------------------------------------------------|------------------------------------------------------|----------|
| Sprocket groove engagement         | 95 mm pitch diameter, 20 grooves defined            | Print and test first engagement with track           | High     |
| Tensioner & idler diameters        | TBD                                                 | Size to fit cleanly inside 215 mm track loop         | High     |
| Motor-to-sprocket coupling         | Not decided                                         | Direct shaft, flexible coupler, or other?            | High     |
| Track tensioning mechanism         | Front wheel moves forward/back                      | Refine adjustment method and access                  | Medium   |
| Motor upgrade path                 | Keep current Greartisan motors                      | When / what to upgrade to                            | Low      |

---

## 7. Change Log

| Date          | Change                                                                 | Notes |
|---------------|------------------------------------------------------------------------|-------|
| June 23, 2026 | Major redesign: Switched from segmented track to one-piece continuous TPU track. Updated to 215 mm diameter, 45 lugs @ 15 mm pitch, 25 mm wide lugs, 4 mm side lips, chevron tread, and slot/groove drive method. Added sprocket baseline (95 mm pitch diameter, 20 grooves). Added starting BOM section. | Major design pivot based on user preference for continuous track and groove drive |
