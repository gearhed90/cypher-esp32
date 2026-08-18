"""
Cypher feature flags (IMU, hall sensors, laser).

Persisted to feature_flags.json next to this module.
All features default OFF so missing hardware cannot break boot or motors.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from typing import Any, Dict

logger = logging.getLogger("cypher-features")

_FLAGS_PATH = os.path.join(os.path.dirname(__file__), "feature_flags.json")
_lock = threading.Lock()

DEFAULTS: Dict[str, bool] = {
    "imu": False,
    "hall_left": False,
    "hall_right": False,
    "laser": False,
}

_KNOWN = set(DEFAULTS.keys())


def _read_file() -> Dict[str, bool]:
    flags = dict(DEFAULTS)
    if not os.path.exists(_FLAGS_PATH):
        return flags
    try:
        with open(_FLAGS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            for k in _KNOWN:
                if k in data:
                    flags[k] = bool(data[k])
    except Exception as e:
        logger.warning("Could not read feature_flags.json: %s", e)
    return flags


def _write_file(flags: Dict[str, bool]) -> bool:
    try:
        tmp = _FLAGS_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(flags, f, indent=2)
            f.write("\n")
        os.replace(tmp, _FLAGS_PATH)
        return True
    except Exception as e:
        logger.warning("Could not write feature_flags.json: %s", e)
        return False


def get_flags() -> Dict[str, bool]:
    with _lock:
        return _read_file()


def is_enabled(name: str) -> bool:
    return bool(get_flags().get(name, False))


def set_flags(updates: Dict[str, Any]) -> Dict[str, bool]:
    """Merge updates for known keys; returns full flag dict."""
    with _lock:
        flags = _read_file()
        for k, v in updates.items():
            if k in _KNOWN:
                flags[k] = bool(v)
        _write_file(flags)
        return dict(flags)
