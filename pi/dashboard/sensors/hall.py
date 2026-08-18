"""
Hall-effect wheel / track sensor stubs.

Flags: hall_left, hall_right.
Provisional GPIOs via env (BCM):
  CYPHER_HALL_LEFT_GPIO  (default 5)
  CYPHER_HALL_RIGHT_GPIO (default 6)

When disabled, counts stay zero and GPIO is not claimed.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

logger = logging.getLogger("cypher-hall")

LEFT_GPIO = int(os.environ.get("CYPHER_HALL_LEFT_GPIO", "5"))
RIGHT_GPIO = int(os.environ.get("CYPHER_HALL_RIGHT_GPIO", "6"))

_count_left = 0
_count_right = 0
_ok_left = False
_ok_right = False
_started = False


def start() -> bool:
    global _started, _ok_left, _ok_right
    from features import is_enabled

    want_l = is_enabled("hall_left")
    want_r = is_enabled("hall_right")
    if not want_l and not want_r:
        _ok_left = _ok_right = False
        return False

    if _started:
        return _ok_left or _ok_right
    _started = True

    # TODO: gpiozero Button/LineSensor edge callbacks to increment counts
    if want_l:
        logger.info("Hall left enabled (stub) GPIO %d", LEFT_GPIO)
        _ok_left = True
    if want_r:
        logger.info("Hall right enabled (stub) GPIO %d", RIGHT_GPIO)
        _ok_right = True
    return _ok_left or _ok_right


def reset_counts() -> None:
    global _count_left, _count_right
    _count_left = 0
    _count_right = 0


def read() -> Dict[str, Any]:
    from features import is_enabled

    if not _started and (is_enabled("hall_left") or is_enabled("hall_right")):
        start()
    return {
        "left": {
            "enabled": is_enabled("hall_left"),
            "ok": _ok_left,
            "gpio": LEFT_GPIO,
            "count": _count_left if is_enabled("hall_left") else 0,
        },
        "right": {
            "enabled": is_enabled("hall_right"),
            "ok": _ok_right,
            "gpio": RIGHT_GPIO,
            "count": _count_right if is_enabled("hall_right") else 0,
        },
    }
