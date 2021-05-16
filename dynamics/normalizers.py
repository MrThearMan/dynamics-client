"""
The dynamics API can return data in all sorts of formats, so these functions
can be used to pre-process known problematic data points before handing them to the serializer.
Most common case is the separation of non-existing values vs. explicit `null` returned by API.
"""


__all__ = [
    "as_int",
    "as_float",
    "as_str",
    "as_bool",
]


def as_int(value, default: int = 0) -> int:
    if not value:
        return default
    return int(value)


def as_float(value, default: float = 0.0) -> float:
    if not value:
        return default
    return float(str(value).replace(",", "."))


def as_str(value, default: str = "") -> str:
    if not value:
        return default
    return str(value)


def as_bool(value, default: bool = False) -> bool:
    if value is not True and value is not False:
        return default
    return bool(value)
