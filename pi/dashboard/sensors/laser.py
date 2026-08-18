"""
Laser diode control stub.

Provisional GPIO: CYPHER_LASER_GPIO (default BCM 4).

Safety:
  - Feature flag "laser" must be on
  - Never turns on during import or start()
  - set_on(True) is the only path that would assert the pin (still stubbed)
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

logger = logging.getLogger("cypher-laser")

LASER_GPIO = int(os.environ.get("CYPHER_LASER_GPIO", "4"))

_ok = False
_on = False
_started = False


def start() -> bool:
    """Claim GPIO only if feature enabled; leave laser OFF."""
    global _started, _ok, _on
    from features import is_enabled

    if not is_enabled("laser"):
        _ok = False
        _on = False
        return False
    if _started:
        return _ok
    _started = True
    try:
        # TODO: gpiozero DigitalOutputDevice(LASER_GPIO, initial_value=False)
        logger.info("Laser feature enabled (stub) GPIO %d — output held OFF", LASER_GPIO)
        _ok = True
        _on = False
        return True
    except Exception as e:
        logger.warning("Laser init failed: %s", e)
        _ok = False
        return False


def is_ok() -> bool:
    return _ok


def is_on() -> bool:
    return _on


def set_on(on: bool) -> bool:
    """Arm/disarm laser. Refuses if feature flag off."""
    global _on
    from features import is_enabled

    if not is_enabled("laser"):
        _on = False
        return False
    if not _ok:
        start()
    if not _ok:
        return False
    # TODO: device.on() / device.off()
    _on = bool(on)
    logger.info("Laser stub set_on(%s)", _on)
    return True


def status() -> Dict[str, Any]:
    from features import is_enabled

    return {
        "enabled": is_enabled("laser"),
        "ok": _ok,
        "on": _on if is_enabled("laser") else False,
        "gpio": LASER_GPIO,
    }
