"""
The dynamics API can return data in all sorts of formats, so these functions
can be used to pre-process known problematic data points before handing them to the serializer.
Most common case is the separation of non-existing values vs. explicit `null` returned by API.
"""

from datetime import datetime
from typing import Any, Optional

from dynamics.utils import from_dynamics_date_format


__all__ = [
    "as_int",
    "as_float",
    "as_str",
    "as_bool",
]


def as_int(value: Any, default: int = 0) -> int:
    try:
        if isinstance(value, str):
            value = value.replace(",", ".")
        return int(value)
    except (ValueError, TypeError):
        return default


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, str):
            value = value.replace(",", ".")
        return float(value)
    except (ValueError, TypeError):
        return default


def as_str(value: Any, default: str = "") -> str:
    try:
        if value in (True, False, None):
            return default
        return str(value)
    except (ValueError, TypeError):
        return default


def as_bool(value: Any, default: bool = False) -> bool:
    try:
        return bool(value)
    except (ValueError, TypeError):
        return default


def str_as_datetime(value: str, default: Any = None) -> Optional[datetime]:
    try:
        return from_dynamics_date_format(value)
    except Exception:
        return default
