# Cypher ESP32 Bridge

This module provides reliable UART communication between the Raspberry Pi and the ESP32 motor controller.

## Features

- Automatic heartbeat (every ~800ms) to keep the ESP32 safety timeout happy
- Auto-reconnect on communication failure
- Clean command interface (`move()`, `stop()`, `get_status()`, etc.)
- Context manager support

## Usage

```python
from esp32_bridge import ESP32Bridge

with ESP32Bridge() as bridge:
    bridge.move(80, 20)
    time.sleep(2)
    bridge.stop()
Protocol
See docs/UART_PROTOCOL.md for the full command/response specification.
Systemd Service
The bridge runs as cypher-bridge.service and starts automatically on boot.
Files

esp32_bridge.py — Main bridge implementation
cypher-bridge.service — systemd unit file
