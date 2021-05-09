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


def as_int(value) -> int:
    if not value:
        return 0
    return int(value)


def as_float(value) -> float:
    if not value:
        return 0.0
    return float(str(value).replace(",", "."))


def as_str(value) -> str:
    if not value:
        return ""
    return str(value)


def as_bool(value) -> bool:
    if value is not True and value is not False:
        return False
    return bool(value)
