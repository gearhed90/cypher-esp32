# ESP32 Bridge

This module provides a clean, reliable communication layer between the Raspberry Pi and the ESP32 over UART.

## Usage Example

```python
from pi.bridge.esp32_bridge import ESP32Bridge
import time

bridge = ESP32Bridge(port='/dev/serial0', baudrate=115200)

if bridge.start():
    bridge.move(throttle=120, steering=0)   # Move forward
    time.sleep(1)
    bridge.stop()
    bridge.close()
Features

Simple move(), stop(), get_status() interface
Background heartbeat for connection monitoring
Automatic safety stop if connection is lost
Thread-safe
Easy to integrate into the dashboard or vision code later
