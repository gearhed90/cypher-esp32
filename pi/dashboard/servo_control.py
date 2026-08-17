"""
Cypher pan/tilt servo control (Raspberry Pi GPIOs).

Pan  = GPIO 18 (BCM)
Tilt = GPIO 17 (BCM)

Power servos from the 5 V rail, not the Pi 5 V pin.
Signal wires to these GPIOs; common ground with the Pi.

Uses gpiozero AngularServo. Requires gpiozero (and usually
the system pigpio or RPi.GPIO backend on Raspberry Pi OS).
"""

from __future__ import annotations

import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger("cypher-servos")

PAN_GPIO = int(os.environ.get("CYPHER_PAN_GPIO", "18"))
TILT_GPIO = int(os.environ.get("CYPHER_TILT_GPIO", "17"))

# Typical MG90S-ish range; adjust if your horns hit hard stops
PAN_MIN = float(os.environ.get("CYPHER_PAN_MIN", "-90"))
PAN_MAX = float(os.environ.get("CYPHER_PAN_MAX", "90"))
TILT_MIN = float(os.environ.get("CYPHER_TILT_MIN", "-45"))
TILT_MAX = float(os.environ.get("CYPHER_TILT_MAX", "45"))

_pan = None
_tilt = None
_ok = False
_pan_angle = 0.0
_tilt_angle = 0.0


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def start() -> bool:
    """Initialize servos and center them. Safe to call more than once."""
    global _pan, _tilt, _ok, _pan_angle, _tilt_angle
    if _ok:
        return True
    try:
        from gpiozero import AngularServo
        from gpiozero.pins.lgpio import LGPIOFactory

        # lgpio is preferred on modern Pi OS; fall back to default factory
        try:
            factory = LGPIOFactory()
            _pan = AngularServo(
                PAN_GPIO,
                min_angle=PAN_MIN,
                max_angle=PAN_MAX,
                min_pulse_width=0.0005,
                max_pulse_width=0.0025,
                pin_factory=factory,
            )
            _tilt = AngularServo(
                TILT_GPIO,
                min_angle=TILT_MIN,
                max_angle=TILT_MAX,
                min_pulse_width=0.0005,
                max_pulse_width=0.0025,
                pin_factory=factory,
            )
        except Exception:
            _pan = AngularServo(
                PAN_GPIO,
                min_angle=PAN_MIN,
                max_angle=PAN_MAX,
                min_pulse_width=0.0005,
                max_pulse_width=0.0025,
            )
            _tilt = AngularServo(
                TILT_GPIO,
                min_angle=TILT_MIN,
                max_angle=TILT_MAX,
                min_pulse_width=0.0005,
                max_pulse_width=0.0025,
            )

        _pan.angle = 0
        _tilt.angle = 0
        _pan_angle = 0.0
        _tilt_angle = 0.0
        _ok = True
        logger.info("Servos ready: pan=GPIO%d tilt=GPIO%d (centered)", PAN_GPIO, TILT_GPIO)
        return True
    except Exception as e:
        logger.warning("Servo init failed (gpiozero/hardware?): %s", e)
        _ok = False
        _pan = None
        _tilt = None
        return False


def is_ok() -> bool:
    return _ok


def get_angles() -> Tuple[float, float]:
    return _pan_angle, _tilt_angle


def set_angles(pan: Optional[float] = None, tilt: Optional[float] = None) -> bool:
    """Set absolute angles in degrees. None = leave unchanged."""
    global _pan_angle, _tilt_angle
    if not _ok or _pan is None or _tilt is None:
        if not start():
            return False
    try:
        if pan is not None:
            a = _clamp(float(pan), PAN_MIN, PAN_MAX)
            _pan.angle = a
            _pan_angle = a
        if tilt is not None:
            a = _clamp(float(tilt), TILT_MIN, TILT_MAX)
            _tilt.angle = a
            _tilt_angle = a
        return True
    except Exception as e:
        logger.warning("set_angles failed: %s", e)
        return False


def nudge(pan_delta: float = 0.0, tilt_delta: float = 0.0) -> bool:
    """Relative move from current angles."""
    return set_angles(_pan_angle + pan_delta, _tilt_angle + tilt_delta)


def center() -> bool:
    return set_angles(0.0, 0.0)


def stop_pwm() -> None:
    """Detach PWM (servos may go limp depending on hardware)."""
    global _ok
    try:
        if _pan is not None:
            _pan.detach()
        if _tilt is not None:
            _tilt.detach()
    except Exception:
        pass
