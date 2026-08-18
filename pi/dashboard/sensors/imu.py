"""
IMU stub (e.g. MPU6050 / ICM on I2C).

When feature flag "imu" is off, all calls no-op.
Replace read() body when hardware is installed.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("cypher-imu")

_started = False
_ok = False
_last: Dict[str, Any] = {
    "roll": None,
    "pitch": None,
    "yaw": None,
    "ax": None,
    "ay": None,
    "az": None,
}


def start() -> bool:
    """Init bus/device only if feature enabled."""
    global _started, _ok
    from features import is_enabled

    if not is_enabled("imu"):
        _ok = False
        return False
    if _started:
        return _ok
    _started = True
    try:
        # TODO: open I2C, configure IMU
        # e.g. smbus / adafruit_mpu6050
        logger.info("IMU enabled (stub — no hardware driver yet)")
        _ok = True
        return True
    except Exception as e:
        logger.warning("IMU init failed: %s", e)
        _ok = False
        return False


def is_ok() -> bool:
    return _ok


def read() -> Dict[str, Any]:
    """Return last sample dict. Stub returns nulls until driver exists."""
    from features import is_enabled

    if not is_enabled("imu"):
        return {"enabled": False, **_last}
    if not _ok:
        start()
    # TODO: read registers / fused orientation
    return {"enabled": True, "ok": _ok, **_last}


def stop() -> None:
    global _started, _ok
    _started = False
    _ok = False
