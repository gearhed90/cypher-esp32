#!/usr/bin/env python3
"""
ESP32 Bridge - Robust communication layer between Raspberry Pi and ESP32.

Focus: Reliability, auto-recovery, and clean interface.
"""

import serial
import threading
import time
import logging
from typing import Optional


class ESP32Bridge:
    """
    Reliable UART bridge to the ESP32.

    Features:
    - Auto-reconnect on serial failure
    - Background heartbeat with health monitoring
    - Clean start/stop interface
    - Safe motor stop on connection loss
    """

    def __init__(
        self,
        port: str = "/dev/serial0",
        baudrate: int = 115200,
        timeout: float = 1.0,
        heartbeat_interval: float = 0.8,
        heartbeat_timeout: float = 1.5,
        log_level: int = logging.INFO
    ):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout

        self.ser: Optional[serial.Serial] = None
        self.connected = False
        self.last_heartbeat = 0.0

        self._stop_event = threading.Event()
        self._heartbeat_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        # Setup logging
        self.logger = logging.getLogger("ESP32Bridge")
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
            self.logger.addHandler(handler)

    # ====================== Connection Management ======================

    def start(self) -> bool:
        """Open serial connection and start heartbeat thread."""
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(0.4)  # Give ESP32 time to boot if needed
            self.connected = True
            self.last_heartbeat = time.time()

            self._stop_event.clear()
            self._heartbeat_thread = threading.Thread(
                target=self._heartbeat_loop, daemon=True, name="ESP32-Heartbeat"
            )
            self._heartbeat_thread.start()

            self.logger.info(f"Connected to ESP32 on {self.port}")
            return True

        except serial.SerialException as e:
            self.logger.error(f"Failed to open serial port {self.port}: {e}")
            self.connected = False
            return False

    def _heartbeat_loop(self):
        """Send periodic heartbeats and monitor connection health."""
        while not self._stop_event.is_set():
            try:
                if self.connected and self.ser and self.ser.is_open:
                    self._send_raw("HEARTBEAT")
                    self.last_heartbeat = time.time()
            except Exception as e:
                self.logger.warning(f"Heartbeat send failed: {e}")
                self._attempt_reconnect()

            time.sleep(self.heartbeat_interval)

    def _attempt_reconnect(self):
        """Try to recover the serial connection."""
        self.logger.warning("Attempting to reconnect to ESP32...")
        self.connected = False

        try:
            if self.ser:
                self.ser.close()
            time.sleep(1.0)
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            self.connected = True
            self.last_heartbeat = time.time()
            self.logger.info("Reconnected to ESP32 successfully.")
        except Exception as e:
            self.logger.error(f"Reconnect failed: {e}")

    def is_connected(self) -> bool:
        """Returns True if we recently received/sent a heartbeat."""
        return (time.time() - self.last_heartbeat) < self.heartbeat_timeout

    def is_healthy(self) -> bool:
        """Stronger health check (currently same as is_connected)."""
        return self.is_connected()

    def close(self):
        """Cleanly shut down the bridge."""
        self.logger.info("Shutting down ESP32 bridge...")
        self._stop_event.set()

        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2.0)

        if self.ser and self.ser.is_open:
            try:
                self._send_raw("STOP")  # Best effort stop
            except Exception:
                pass
            self.ser.close()

        self.connected = False
        self.logger.info("Bridge closed.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # ====================== Command Interface ======================

    def _send_raw(self, message: str):
        """Internal method to send a raw command."""
        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Serial port is not open")

        with self._lock:
            self.ser.write((message + "\n").encode("utf-8"))
            self.ser.flush()

    def move(self, throttle: int, steering: int) -> bool:
        """Send movement command to ESP32."""
        if not self.connected:
            return False
        try:
            cmd = f"MOVE:{throttle},{steering}"
            self._send_raw(cmd)
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send MOVE command: {e}")
            self._attempt_reconnect()
            return False

    def stop(self) -> bool:
        """Send emergency stop command."""
        try:
            self._send_raw("STOP")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send STOP: {e}")
            return False

    def get_status(self) -> Optional[str]:
        """Request current status from ESP32."""
        if not self.connected:
            return None
        try:
            self._send_raw("STATUS?")
            time.sleep(0.08)
            if self.ser and self.ser.in_waiting > 0:
                return self.ser.readline().decode("utf-8").strip()
        except Exception as e:
            self.logger.warning(f"Status request failed: {e}")
        return None

    def set_mode(self, mode: str) -> bool:
        """Set control mode (MANUAL or AUTO)."""
        if not self.connected:
            return False
        try:
            self._send_raw(f"MODE:{mode.upper()}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to set mode: {e}")
            return False
