#!/usr/bin/env python3
"""
ESP32 Bridge - Clean communication layer between Raspberry Pi and ESP32.

This module provides a simple, reliable interface for sending movement
commands to the ESP32 over UART while maintaining a heartbeat for safety.
"""

import serial
import threading
import time
from typing import Optional, Tuple


class ESP32Bridge:
    """
    Clean interface for communicating with the ESP32 over UART.
    
    Usage:
        bridge = ESP32Bridge(port='/dev/serial0', baudrate=115200)
        bridge.start()
        bridge.move(throttle=120, steering=0)
        bridge.stop()
        bridge.close()
    """

    def __init__(self, port: str = '/dev/serial0', baudrate: int = 115200, timeout: float = 1.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.connected = False
        self.last_heartbeat = 0
        self.heartbeat_interval = 0.8  # seconds
        self.heartbeat_timeout = 1.5   # seconds before considering connection lost
        self._stop_event = threading.Event()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self) -> bool:
        """Open the serial connection and start the heartbeat thread."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(0.5)  # Give ESP32 time to reset if needed
            self.connected = True
            self.last_heartbeat = time.time()

            # Start heartbeat thread
            self._stop_event.clear()
            self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
            self._heartbeat_thread.start()

            print(f"[Bridge] Connected to ESP32 on {self.port}")
            return True

        except serial.SerialException as e:
            print(f"[Bridge] Failed to open serial port: {e}")
            self.connected = False
            return False

    def _heartbeat_loop(self):
        """Background thread that sends periodic heartbeats."""
        while not self._stop_event.is_set():
            try:
                if self.connected and self.ser and self.ser.is_open:
                    self._send_raw("HEARTBEAT")
                    self.last_heartbeat = time.time()
            except Exception as e:
                print(f"[Bridge] Heartbeat error: {e}")

            time.sleep(self.heartbeat_interval)

    def _send_raw(self, message: str):
        """Send a raw message to the ESP32."""
        if self.ser and self.ser.is_open:
            with self._lock:
                self.ser.write((message + "\n").encode('utf-8'))
                self.ser.flush()

    def move(self, throttle: int, steering: int):
        """
        Send movement command.
        
        Args:
            throttle: Forward/back speed (-255 to 255)
            steering: Left/right steering (-255 to 255)
        """
        if not self.connected:
            return False

        cmd = f"MOVE:{throttle},{steering}"
        self._send_raw(cmd)
        return True

    def stop(self):
        """Emergency stop."""
        self._send_raw("STOP")

    def get_status(self) -> Optional[str]:
        """Request current status from ESP32."""
        if not self.connected:
            return None

        self._send_raw("STATUS?")
        time.sleep(0.1)

        if self.ser and self.ser.in_waiting > 0:
            try:
                response = self.ser.readline().decode('utf-8').strip()
                return response
            except Exception:
                return None
        return None

    def set_mode(self, mode: str):
        """Set control mode (MANUAL or AUTO)."""
        self._send_raw(f"MODE:{mode.upper()}")

    def is_connected(self) -> bool:
        """Check if we're still receiving heartbeats."""
        return (time.time() - self.last_heartbeat) < self.heartbeat_timeout

    def close(self):
        """Cleanly close the connection."""
        self._stop_event.set()
        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=1.0)

        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        print("[Bridge] Connection closed")


# Simple test when running this file directly
if __name__ == "__main__":
    print("Testing ESP32 Bridge...")

    bridge = ESP32Bridge(port='/dev/serial0', baudrate=115200)
    
    if bridge.start():
        print("Bridge started successfully.")
        
        # Example usage
        bridge.move(100, 0)
        time.sleep(1)
        bridge.stop()
        
        status = bridge.get_status()
        print(f"Status: {status}")
        
        time.sleep(2)
        bridge.close()
    else:
        print("Failed to start bridge.")
