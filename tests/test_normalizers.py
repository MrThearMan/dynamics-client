from datetime import datetime

import pytest

from dynamics.normalizers import as_bool, as_float, as_int, as_str, str_as_datetime
from dynamics.typing import Any


class Failer:
    def __str__(self):
        return object()

    def __bool__(self):
        return ""


@pytest.mark.parametrize(
    "value,default,result",
    [
        [1, 0, 1],
        [1.123, 0, 1],
        ["1", 0, 1],
        ["1.123", 0, 1],
        ["1,123", 0, 1],
        [None, 0, 0],
        [None, 1, 1],
    ],
)
def test_normalizer__as_int(value: Any, default: int, result: int):
    assert as_int(value, default) == result


@pytest.mark.parametrize(
    "value,default,result",
    [
        [1, 0, 1.0],
        [1.123, 0, 1.123],
        ["1", 0, 1.0],
        ["1.123", 0, 1.123],
        ["1,123", 0, 1.123],
        [None, 0, 0.0],
        [None, 1, 1.0],
    ],
)
def test_normalizer__as_float(value: Any, default: int, result: float):
    assert as_float(value, default) == result


@pytest.mark.parametrize(
    "value,default,result",
    [
        [1, "0", "1"],
        [1.123, "0", "1.123"],
        ["foo", "0", "foo"],
        [["foo"], "0", "['foo']"],
        [{"foo"}, "0", "{'foo'}"],
        [{"foo": "bar"}, "0", "{'foo': 'bar'}"],
        [None, "foo", "foo"],
        [True, "foo", "foo"],
        [False, "foo", "foo"],
        [None, "bar", "bar"],
        [Failer(), "bar", "bar"],
    ],
)
def test_normalizer__as_str(value: Any, default: str, result: str):
    assert as_str(value, default) == result


@pytest.mark.parametrize(
    "value,default,result",
    [
        [1, False, True],
        [0, True, False],
        ["foo", False, True],
        ["", True, False],
        [Failer(), None, None],
    ],
)
def test_normalizer__as_bool(value: Any, default: bool, result: bool):
    assert as_bool(value, default) == result


@pytest.mark.parametrize(
    "value,default,result",
    [
        ["2021-01-01T00:00:00Z", "foo", datetime(2021, 1, 1)],
        ["2021-01-01T00:00:00", "foo", datetime(2021, 1, 1)],
        ["2021-01-0100:00:00Z", "foo", "foo"],
        [None, "foo", "foo"],
    ],
)
def test_normalizer__str_as_datetime(value: Any, default: Any, result: Any):
    assert str_as_datetime(value, default) == result
