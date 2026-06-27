# Cypher Robot - Architecture Overview

This document describes the intended architecture and layering of the Cypher robot project.

## Core Philosophy

The most important principle in this project is **protecting the foundation**.

Motor control and basic movement must remain stable, predictable, and safe. All other features (dashboard, vision, autonomy, etc.) should be built **on top** of this foundation rather than modifying it directly.

## High-Level Layers
┌─────────────────────────────────────────────────────────────┐
│                        External Access                       │
│   (Browser, Tailscale, SSH, Web UI, Status Page, etc.)      │
└────────────────────────────┬────────────────────────────────┘
│
┌────────────────────────────▼────────────────────────────────┐
│                     Raspberry Pi (Higher Level)              │
│  ┌──────────────────┐   ┌──────────────────┐                │
│  │   Dashboard      │   │     Vision       │                │
│  │  (Flask Web UI)  │   │ (Camera + AI)    │                │
│  └────────┬─────────┘   └────────┬─────────┘                │
│           │                      │                           │
│  ┌────────▼──────────────────────▼─────────┐                │
│  │         Communication Bridge             │                │
│  │     (UART protocol + heartbeat)          │                │
│  └──────────────────┬───────────────────────┘                │
└─────────────────────┼───────────────────────────────────────┘
│ UART
┌─────────────────────▼───────────────────────────────────────┐
│                     ESP32 (Low Level)                        │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Motor Control Layer                     │    │
│  │   (Tank drive, speed, steering, safety limits)       │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Basic Web Server                        │    │
│  │         (Manual control UI + OTA)                    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
text## Layer Responsibilities

### ESP32 Firmware (`firmware/`)

**Core responsibilities:**
- Motor control (left/right tank drive)
- Basic safety (speed limits, stop on command loss)
- Simple web-based manual control interface
- OTA (Over-The-Air) firmware updates
- Receiving and executing commands from the Raspberry Pi over UART

**Design goal:** This layer should be **as small and stable as possible**. Most new features should **not** require changes here.

### Raspberry Pi (`pi/`)

**Core responsibilities:**
- Higher-level logic and orchestration
- Web dashboard (Flask)
- Camera / vision processing
- System services and monitoring
- Sending high-level commands to the ESP32 over UART

**Communication Bridge:**
The Pi should communicate with the ESP32 through a well-defined, versioned command protocol over UART rather than directly controlling motors.

### Communication (UART)

- Primary communication channel between Pi and ESP32.
- Should be simple, reliable, and versioned.
- Should include heartbeat / connection monitoring.
- The ESP32 should be the authority on motor safety.

## Design Principles

1. **Protect the Motor Layer**  
   Changes to motor behavior should be rare and well-justified.

2. **Layered Communication**  
   The Pi sends high-level commands (e.g., "move forward at speed X", "stop", "set mode"). The ESP32 translates those into motor signals.

3. **Safe Defaults**  
   The system should always boot into a safe state (Manual + Stopped).

4. **Reproducibility**  
   The repository should contain everything needed to recreate the full system.

5. **Incremental Development**  
   Add features in small, testable layers rather than large risky changes.

## Future Considerations

When autonomous behaviors are reintroduced later, they should:
- Live primarily on the Raspberry Pi side
- Send commands to the ESP32 through the existing communication bridge
- Never directly modify the core motor control code in the ESP32

---

Last updated: June 2026
