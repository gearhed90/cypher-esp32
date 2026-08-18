"""
Cypher pan/tilt servo control (Raspberry Pi GPIOs).

Pan  = GPIO 18 (BCM)
Tilt = GPIO 17 (BCM)

Power servos from the 5 V rail, not the Pi 5 V pin.
Signal wires to these GPIOs; common ground with the Pi.

On startup the PWM is attached then immediately detached so the
servos do NOT move or hold until the first explicit command
(set_angles / nudge / center). That lets you teach min/max travel
before anything drives into a hard stop.

Uses gpiozero AngularServo.
"""

from __future__ import annotations

import logging
import os
from typing import Optional, Tuple

logger = logging.getLogger("cypher-servos")

PAN_GPIO = int(os.environ.get("CYPHER_PAN_GPIO", "18"))
TILT_GPIO = int(os.environ.get("CYPHER_TILT_GPIO", "17"))

# Adjust via .env after you measure real travel
PAN_MIN = float(os.environ.get("CYPHER_PAN_MIN", "-90"))
PAN_MAX = float(os.environ.get("CYPHER_PAN_MAX", "90"))
TILT_MIN = float(os.environ.get("CYPHER_TILT_MIN", "-45"))
TILT_MAX = float(os.environ.get("CYPHER_TILT_MAX", "45"))

_pan = None
_tilt = None
_ok = False
_armed = False  # True after first real move command
_pan_angle = 0.0
_tilt_angle = 0.0


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _make_servo(gpio, min_a, max_a, factory=None):
    from gpiozero import AngularServo

    kwargs = dict(
        min_angle=min_a,
        max_angle=max_a,
        min_pulse_width=0.0005,
        max_pulse_width=0.0025,
    )
    if factory is not None:
        kwargs["pin_factory"] = factory
    return AngularServo(gpio, **kwargs)


def start() -> bool:
    """Create servo objects but do not drive them (no sweep on boot)."""
    global _pan, _tilt, _ok, _armed, _pan_angle, _tilt_angle
    if _ok:
        return True
    try:
        factory = None
        try:
            from gpiozero.pins.lgpio import LGPIOFactory
            factory = LGPIOFactory()
        except Exception:
            factory = None

        _pan = _make_servo(PAN_GPIO, PAN_MIN, PAN_MAX, factory)
        _tilt = _make_servo(TILT_GPIO, TILT_MIN, TILT_MAX, factory)

        # Critical: release PWM immediately so horns stay where they are
        try:
            _pan.detach()
        except Exception:
            pass
        try:
            _tilt.detach()
        except Exception:
            pass

        _armed = False
        _pan_angle = 0.0
        _tilt_angle = 0.0
        _ok = True
        logger.info(
            "Servos ready (idle/detached): pan=GPIO%d tilt=GPIO%d — no move until commanded",
            PAN_GPIO,
            TILT_GPIO,
        )
        return True
    except Exception as e:
        logger.warning("Servo init failed (gpiozero/hardware?): %s", e)
        _ok = False
        _pan = None
        _tilt = None
        return False


def is_ok() -> bool:
    return _ok


def is_armed() -> bool:
    return _armed


def get_angles() -> Tuple[float, float]:
    return _pan_angle, _tilt_angle


def set_angles(pan: Optional[float] = None, tilt: Optional[float] = None) -> bool:
    """Set absolute angles in degrees. First call arms the servos."""
    global _pan_angle, _tilt_angle, _armed
    if not _ok or _pan is None or _tilt is None:
        if not start():
            return False
    try:
        if pan is not None:
            a = _clamp(float(pan), PAN_MIN, PAN_MAX)
            _pan.angle = a
            _pan_angle = a
            _armed = True
        if tilt is not None:
            a = _clamp(float(tilt), TILT_MIN, TILT_MAX)
            _tilt.angle = a
            _tilt_angle = a
            _armed = True
        return True
    except Exception as e:
        logger.warning("set_angles failed: %s", e)
        return False


def nudge(pan_delta: float = 0.0, tilt_delta: float = 0.0) -> bool:
    """Relative move from last commanded angles."""
    return set_angles(_pan_angle + pan_delta, _tilt_angle + tilt_delta)


def center() -> bool:
    """Explicit center only — not called on startup."""
    return set_angles(0.0, 0.0)


def stop_pwm() -> None:
    """Detach PWM (servos go limp / hold last mechanical position)."""
    global _armed
    try:
        if _pan is not None:
            _pan.detach()
        if _tilt is not None:
            _tilt.detach()
        _armed = False
    except Exception:
        pass
