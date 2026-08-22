#!/usr/bin/env python3
"""
ESP32 Bridge - Robust communication layer between Raspberry Pi and ESP32.

Focus: Reliability, auto-recovery, and clean interface.
Motors + pan/tilt servos over UART.
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
    - Pan/tilt commands (ESP32 hardware PWM)
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

        self.logger = logging.getLogger("ESP32Bridge")
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
            self.logger.addHandler(handler)

    def start(self) -> bool:
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            time.sleep(0.4)
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
        return (time.time() - self.last_heartbeat) < self.heartbeat_timeout

    def is_healthy(self) -> bool:
        return self.is_connected()

    def close(self):
        self.logger.info("Shutting down ESP32 bridge...")
        self._stop_event.set()

        if self._heartbeat_thread:
            self._heartbeat_thread.join(timeout=2.0)

        if self.ser and self.ser.is_open:
            try:
                self._send_raw("STOP")
            except Exception:
                pass
            self.ser.close()

        self.connected = False
        self.logger.info("Bridge closed.")

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exp_type, exp_val, exp_tb):
        self.close()

    def _send_raw(self, message: str):
        if not self.ser or not self.ser.is_open:
            raise ConnectionError("Serial port is not open")

        with self._lock:
            self.ser.write((message + "\n").encode("utf-8"))
            self.ser.flush()

    def move(self, throttle: int, steering: int) -> bool:
        if not self.connected:
            return False
        try:
            self._send_raw(f"MOVE:{throttle},{steering}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send MOVE command: {e}")
            self._attempt_reconnect()
            return False

    def stop(self) -> bool:
        try:
            self._send_raw("STOP")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send STOP: {e}")
            return False

    def get_status(self) -> Optional[str]:
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
        if not self.connected:
            return False
        try:
            self._send_raw(f"MODE:{mode.upper()}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to set mode: {e}")
            return False

    def pt(self, pan: float, tilt: float) -> bool:
        if not self.connected:
            return False
        try:
            self._send_raw(f"PT:{pan},{tilt}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send PT: {e}")
            return False

    def pan(self, angle: float) -> bool:
        if not self.connected:
            return False
        try:
            self._send_raw(f"PAN:{angle}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send PAN: {e}")
            return False

    def tilt(self, angle: float) -> bool:
        if not self.connected:
            return False
        try:
            self._send_raw(f"TILT:{angle}")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send TILT: {e}")
            return False

    def pt_center(self) -> bool:
        if not self.connected:
            return False
        try:
            self._send_raw("PT_CENTER")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send PT_CENTER: {e}")
            return False

    def pt_sleep(self) -> bool:
        if not self.connected:
            return False
        try:
            self._send_raw("PT_SLEEP")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send PT_SLEEP: {e}")
            return False

    def pt_save_boot(self) -> bool:
        """Save current head pose as boot pose (NVS on ESP32)."""
        if not self.connected:
            return False
        try:
            self._send_raw("PT_SAVE_BOOT")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send PT_SAVE_BOOT: {e}")
            return False

    def pt_boot(self) -> bool:
        if not self.connected:
            return False
        try:
            self._send_raw("PT_BOOT")
            return True
        except Exception as e:
            self.logger.warning(f"Failed to send PT_BOOT: {e}")
            return False
