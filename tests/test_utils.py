from datetime import datetime
from time import sleep

import pytest

from dynamics.utils import from_dynamics_date_format, is_valid_uuid, to_dynamics_date_format


@pytest.mark.parametrize(
    "value,result",
    [
        ["08177f42-ea48-414e-9ee9-41a838b09237", True],
        ["08177f42-ea48-414e-41a838b09237", False],
        ["", False],
        [None, False],
    ],
)
def test_utils__is_valid_uuid(value: str, result: bool):
    assert is_valid_uuid(value) == result


@pytest.mark.parametrize(
    "value,from_timezone,result",
    [
        [datetime(2021, 1, 1), None, "2021-01-01T00:00:00Z"],
        [datetime(2021, 1, 1), "UTC", "2021-01-01T00:00:00Z"],
        [datetime(2021, 1, 1), "Europe/Helsinki", "2020-12-31T22:00:00Z"],
        [datetime(2021, 6, 6), "Europe/Helsinki", "2021-06-05T21:00:00Z"],
    ],
)
def test_utils__to_dynamics_date_format(value: datetime, from_timezone: str, result: str):
    assert to_dynamics_date_format(value, from_timezone) == result


@pytest.mark.parametrize(
    "value,from_timezone,result",
    [
        ["2021-01-01T00:00:00Z", "UTC", datetime(2021, 1, 1)],
        ["2020-12-31T22:00:00Z", "Europe/Helsinki", datetime(2021, 1, 1)],
        ["2021-06-05T21:00:00Z", "Europe/Helsinki", datetime(2021, 6, 6)],
    ],
)
def test_utils__from_dynamics_date_format(value: str, from_timezone: str, result: datetime):
    assert from_dynamics_date_format(value, from_timezone) == result


def test_utils__cache(dynamics_cache):
    dynamics_cache.set("foo", "bar", 0.5)
    assert dynamics_cache.get("foo") == "bar"
    sleep(0.5)
    assert dynamics_cache.get("foo") is None

    with pytest.raises(AttributeError):
        dynamics_cache.set("foo", lambda x: 100, 0.5)
