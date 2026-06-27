# UART Communication Protocol (Pi ↔ ESP32)

This document defines the planned communication protocol between the Raspberry Pi and the ESP32.

## Goals

- Simple and reliable
- Easy to extend without breaking existing commands
- Clear separation between high-level commands (Pi) and low-level motor control (ESP32)
- Include basic connection monitoring (heartbeat)

## Current Status

**Not yet implemented.** This document serves as the design spec for Phase 2.

## Design Principles

1. The **ESP32 is the authority** on motor safety.
2. The **Pi sends high-level commands** (e.g. "move forward", "stop", "set speed").
3. Commands should be **human-readable** when possible (easier debugging).
4. Every command should receive an acknowledgment when practical.

## Proposed Message Format

**Simple text-based protocol** (one command per line, newline terminated):
CMD:VALUE1,VALUE2,...\n
text### Examples

| Command from Pi              | Meaning                              | ESP32 Response      |
|-----------------------------|--------------------------------------|---------------------|
| `MOVE:120,0`                | Move forward at speed 120            | `ACK:MOVE`          |
| `MOVE:0,0`                  | Stop                                 | `ACK:STOP`          |
| `MOVE:-80,40`               | Move backward + turn right           | `ACK:MOVE`          |
| `HEARTBEAT`                 | Connection check                     | `HEARTBEAT`         |
| `STATUS?`                   | Request current state                | `STATUS:MANUAL,0,0` |
| `MODE:MANUAL`               | Force manual mode                    | `ACK:MODE`          |

### Status Response Format
STATUS:<MODE>,<THROTTLE>,<STEERING>
textExample: `STATUS:MANUAL,120,0`

## Safety Rules (ESP32 Side)

- If no valid command is received for **X** milliseconds → **stop motors**.
- Always default to stopped on boot or lost connection.
- Ignore invalid or malformed commands.

## Future Extensions

Possible future command groups:

- `HEAD:pan,tilt` — Pan/tilt camera head
- `LIGHT:state` — Control lights
- `CONFIG:KEY=VALUE` — Runtime configuration

These will be added only after the base movement protocol is solid.

## Implementation Plan

1. Define exact command set for basic movement
2. Implement simple parser on ESP32
3. Implement sender + heartbeat on Raspberry Pi
4. Add connection monitoring + automatic safe stop
5. Document final protocol in this file

---

Last updated: June 2026
