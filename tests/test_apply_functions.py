import pytest

from dynamics.apply_functions import apl
from dynamics.typing import FilterType


@pytest.mark.parametrize("aggregate", ["fizzbuzz", None])
def test_apply_functions__groupby(aggregate):
    groupby = apl.groupby(columns=["foo", "bar"], aggregate=aggregate)

    if aggregate:
        result = f"groupby((foo,bar),fizzbuzz)"
    else:
        result = f"groupby((foo,bar))"

    assert groupby == result


def test_apply_functions__aggregate():
    groupby = apl.aggregate(col_="foo", with_="average", as_="bar")
    assert groupby == "aggregate(foo with average as bar)"


@pytest.mark.parametrize("values,raises", [[{"foo", "bar"}, False], [["foo", "bar"], False], [dict(), True]])
def test_apply_functions__filter(values: FilterType, raises: bool):
    try:
        groupby = apl.filter(by=values, group_by_columns=["fizzbuzz"])
    except TypeError as error:
        if not raises:
            pytest.fail(f"TypeError raise when not applicable: '{error}'")
        assert error.args[0] == "Filter by must be either a set or a list."
        return

    sepatator = "or" if isinstance(values, set) else "and"
    try:
        assert groupby == f"filter(foo {sepatator} bar)/groupby((fizzbuzz))"
    except AssertionError:
        assert groupby == f"filter(bar {sepatator} foo)/groupby((fizzbuzz))"
