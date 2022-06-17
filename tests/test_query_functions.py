import pytest

from dynamics.query_functions import ftr
from dynamics.typing import Any


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "foo eq 'bar'"],
        ["fizzbuzz", True, "(fizzbuzz/foo eq 'bar')"],
    ],
)
def test_query_functions__eq(ind: str, group: bool, result: str):
    assert ftr.eq("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "foo ne 'bar'"],
        ["fizzbuzz", True, "(fizzbuzz/foo ne 'bar')"],
    ],
)
def test_query_functions__ne(ind: str, group: bool, result: str):
    assert ftr.ne("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "foo gt 'bar'"],
        ["fizzbuzz", True, "(fizzbuzz/foo gt 'bar')"],
    ],
)
def test_query_functions__gt(ind: str, group: bool, result: str):
    assert ftr.gt("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "foo ge 'bar'"],
        ["fizzbuzz", True, "(fizzbuzz/foo ge 'bar')"],
    ],
)
def test_query_functions__ge(ind: str, group: bool, result: str):
    assert ftr.ge("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "foo lt 'bar'"],
        ["fizzbuzz", True, "(fizzbuzz/foo lt 'bar')"],
    ],
)
def test_query_functions__lt(ind: str, group: bool, result: str):
    assert ftr.lt("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "foo le 'bar'"],
        ["fizzbuzz", True, "(fizzbuzz/foo le 'bar')"],
    ],
)
def test_query_functions__le(ind: str, group: bool, result: str):
    assert ftr.le("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "group,result",
    [
        [False, "foo and bar"],
        [True, "(foo and bar)"],
    ],
)
def test_query_functions__and(group: bool, result: str):
    assert ftr.and_("foo", "bar", group=group) == result


@pytest.mark.parametrize(
    "group,result",
    [
        [False, "foo or bar"],
        [True, "(foo or bar)"],
    ],
)
def test_query_functions__or(group: bool, result: str):
    assert ftr.or_("foo", "bar", group=group) == result


@pytest.mark.parametrize(
    "group,result",
    [
        [False, "not foo"],
        [True, "(not foo)"],
    ],
)
def test_query_functions__not(group: bool, result: str):
    assert ftr.not_("foo", group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "contains(foo,'bar')"],
        ["fizzbuzz", True, "(contains(fizzbuzz/foo,'bar'))"],
    ],
)
def test_query_functions__contains(ind: str, group: bool, result: str):
    assert ftr.contains("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "endswith(foo,'bar')"],
        ["fizzbuzz", True, "(endswith(fizzbuzz/foo,'bar'))"],
    ],
)
def test_query_functions__endswith(ind: str, group: bool, result: str):
    assert ftr.endswith("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "startswith(foo,'bar')"],
        ["fizzbuzz", True, "(startswith(fizzbuzz/foo,'bar'))"],
    ],
)
def test_query_functions__startswith(ind: str, group: bool, result: str):
    assert ftr.startswith("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "operation,ind,group,result",
    [
        [None, None, False, "foo/any()"],
        ["eq", "fizzbuzz", True, "(fizzbuzz/foo/any(bar:eq))"],
    ],
)
def test_query_functions__any(operation: str, ind: str, group: bool, result: str):
    assert ftr.any_("foo", "bar", operation, ind, group) == result


@pytest.mark.parametrize(
    "operation,ind,group,result",
    [
        [None, None, False, "foo/all()"],
        ["eq", "fizzbuzz", True, "(fizzbuzz/foo/all(bar:eq))"],
    ],
)
def test_query_functions__all(operation: str, ind: str, group: bool, result: str):
    assert ftr.all_("foo", "bar", operation, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.In(PropertyName='foo',PropertyValues=['bar'])"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.In(PropertyName='foo',PropertyValues=['bar']))"],
    ],
)
def test_query_functions__in(ind: str, group: bool, result: str):
    assert ftr.in_("foo", ["bar"], ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NotIn(PropertyName='foo',PropertyValues=['bar'])"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NotIn(PropertyName='foo',PropertyValues=['bar']))"],
    ],
)
def test_query_functions__not_in(ind: str, group: bool, result: str):
    assert ftr.not_in("foo", ["bar"], ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.Between(PropertyName='foo',PropertyValues=['bar','baz'])"],
        [
            "fizzbuzz",
            True,
            "(fizzbuzz/Microsoft.Dynamics.CRM.Between(PropertyName='foo',PropertyValues=['bar','baz']))",
        ],
    ],
)
def test_query_functions__between(ind: str, group: bool, result: str):
    assert ftr.between("foo", ("bar", "baz"), ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [
            None,
            False,
            "Microsoft.Dynamics.CRM.NotBetween(PropertyName='foo',PropertyValues=['bar','baz'])",
        ],
        [
            "fizzbuzz",
            True,
            "(fizzbuzz/Microsoft.Dynamics.CRM.NotBetween(PropertyName='foo',PropertyValues=['bar','baz']))",
        ],
    ],
)
def test_query_functions__not_between(ind: str, group: bool, result: str):
    assert ftr.not_between("foo", ("bar", "baz"), ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [
            None,
            False,
            "Microsoft.Dynamics.CRM.ContainValues(PropertyName='foo',PropertyValues=['bar'])",
        ],
        [
            "fizzbuzz",
            True,
            "(fizzbuzz/Microsoft.Dynamics.CRM.ContainValues(PropertyName='foo',PropertyValues=['bar']))",
        ],
    ],
)
def test_query_functions__contain_values(ind: str, group: bool, result: str):
    assert ftr.contain_values("foo", ["bar"], ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [
            None,
            False,
            "Microsoft.Dynamics.CRM.DoesNotContainValues(PropertyName='foo',PropertyValues=['bar'])",
        ],
        [
            "fizzbuzz",
            True,
            "(fizzbuzz/Microsoft.Dynamics.CRM.DoesNotContainValues(PropertyName='foo',PropertyValues=['bar']))",
        ],
    ],
)
def test_query_functions__not_contain_values(ind: str, group: bool, result: str):
    assert ftr.not_contain_values("foo", ["bar"], ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.Above(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.Above(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__above(ind: str, group: bool, result: str):
    assert ftr.above("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.AboveOrEqual(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.AboveOrEqual(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__above_or_equal(ind: str, group: bool, result: str):
    assert ftr.above_or_equal("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.Under(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.Under(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__under(ind: str, group: bool, result: str):
    assert ftr.under("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.UnderOrEqual(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.UnderOrEqual(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__under_or_equal(ind: str, group: bool, result: str):
    assert ftr.under_or_equal("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NotUnder(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NotUnder(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__not_under(ind: str, group: bool, result: str):
    assert ftr.not_under("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.Today(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.Today(PropertyName='foo'))"],
    ],
)
def test_query_functions__today(ind: str, group: bool, result: str):
    assert ftr.today("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.Tomorrow(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.Tomorrow(PropertyName='foo'))"],
    ],
)
def test_query_functions__tomorrow(ind: str, group: bool, result: str):
    assert ftr.tomorrow("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.Yesterday(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.Yesterday(PropertyName='foo'))"],
    ],
)
def test_query_functions__yesterday(ind: str, group: bool, result: str):
    assert ftr.yesterday("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.On(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.On(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__on(ind: str, group: bool, result: str):
    assert ftr.on("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OnOrAfter(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OnOrAfter(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__on_or_after(ind: str, group: bool, result: str):
    assert ftr.on_or_after("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OnOrBefore(PropertyName='foo',PropertyValue='bar')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OnOrBefore(PropertyName='foo',PropertyValue='bar'))"],
    ],
)
def test_query_functions__on_or_before(ind: str, group: bool, result: str):
    assert ftr.on_or_before("foo", "bar", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.InFiscalPeriod(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.InFiscalPeriod(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__in_fiscal_period(ind: str, group: bool, result: str):
    assert ftr.in_fiscal_period("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [
            None,
            False,
            "Microsoft.Dynamics.CRM.InFiscalPeriodAndYear(PropertyName='foo',PropertyValue1=1,PropertyValue2=2)",
        ],
        [
            "fizzbuzz",
            True,
            (
                "(fizzbuzz/Microsoft.Dynamics.CRM.InFiscalPeriodAndYear"
                "(PropertyName='foo',PropertyValue1=1,PropertyValue2=2))"
            ),
        ],
    ],
)
def test_query_functions__in_fiscal_period_and_year(ind: str, group: bool, result: str):
    assert ftr.in_fiscal_period_and_year("foo", 1, 2, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.InFiscalYear(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.InFiscalYear(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__in_fiscal_year(ind: str, group: bool, result: str):
    assert ftr.in_fiscal_year("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [
            None,
            False,
            "Microsoft.Dynamics.CRM.InOrAfterFiscalPeriodAndYear(PropertyName='foo',PropertyValue1=1,PropertyValue2=2)",
        ],
        [
            "fizzbuzz",
            True,
            (
                "(fizzbuzz/Microsoft.Dynamics.CRM.InOrAfterFiscalPeriodAndYear"
                "(PropertyName='foo',PropertyValue1=1,PropertyValue2=2))"
            ),
        ],
    ],
)
def test_query_functions__in_or_after_fiscal_period_and_year(ind: str, group: bool, result: str):
    assert ftr.in_or_after_fiscal_period_and_year("foo", 1, 2, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [
            None,
            False,
            (
                "Microsoft.Dynamics.CRM.InOrBeforeFiscalPeriodAndYear"
                "(PropertyName='foo',PropertyValue1=1,PropertyValue2=2)"
            ),
        ],
        [
            "fizzbuzz",
            True,
            (
                "(fizzbuzz/Microsoft.Dynamics.CRM.InOrBeforeFiscalPeriodAndYear"
                "(PropertyName='foo',PropertyValue1=1,PropertyValue2=2))"
            ),
        ],
    ],
)
def test_query_functions__in_or_before_fiscal_period_and_year(ind: str, group: bool, result: str):
    assert ftr.in_or_before_fiscal_period_and_year("foo", 1, 2, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.ThisFiscalPeriod(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.ThisFiscalPeriod(PropertyName='foo'))"],
    ],
)
def test_query_functions__this_fiscal_period(ind: str, group: bool, result: str):
    assert ftr.this_fiscal_period("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.ThisFiscalYear(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.ThisFiscalYear(PropertyName='foo'))"],
    ],
)
def test_query_functions__this_fiscal_year(ind: str, group: bool, result: str):
    assert ftr.this_fiscal_year("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.ThisMonth(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.ThisMonth(PropertyName='foo'))"],
    ],
)
def test_query_functions__this_month(ind: str, group: bool, result: str):
    assert ftr.this_month("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.ThisWeek(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.ThisWeek(PropertyName='foo'))"],
    ],
)
def test_query_functions__this_week(ind: str, group: bool, result: str):
    assert ftr.this_week("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.ThisYear(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.ThisYear(PropertyName='foo'))"],
    ],
)
def test_query_functions__this_year(ind: str, group: bool, result: str):
    assert ftr.this_year("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.Last7Days(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.Last7Days(PropertyName='foo'))"],
    ],
)
def test_query_functions__last_7_days(ind: str, group: bool, result: str):
    assert ftr.last_7_days("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastFiscalPeriod(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastFiscalPeriod(PropertyName='foo'))"],
    ],
)
def test_query_functions__last_fiscal_period(ind: str, group: bool, result: str):
    assert ftr.last_fiscal_period("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastFiscalYear(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastFiscalYear(PropertyName='foo'))"],
    ],
)
def test_query_functions__last_fiscal_year(ind: str, group: bool, result: str):
    assert ftr.last_fiscal_year("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastMonth(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastMonth(PropertyName='foo'))"],
    ],
)
def test_query_functions__last_month(ind: str, group: bool, result: str):
    assert ftr.last_month("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastWeek(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastWeek(PropertyName='foo'))"],
    ],
)
def test_query_functions__last_week(ind: str, group: bool, result: str):
    assert ftr.last_week("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastYear(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastYear(PropertyName='foo'))"],
    ],
)
def test_query_functions__last_year(ind: str, group: bool, result: str):
    assert ftr.last_year("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastYear(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastYear(PropertyName='foo'))"],
    ],
)
def test_query_functions__last_year(ind: str, group: bool, result: str):
    assert ftr.last_year("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextFiscalPeriod(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextFiscalPeriod(PropertyName='foo'))"],
    ],
)
def test_query_functions__next_fiscal_period(ind: str, group: bool, result: str):
    assert ftr.next_fiscal_period("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextFiscalYear(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextFiscalYear(PropertyName='foo'))"],
    ],
)
def test_query_functions__next_fiscal_year(ind: str, group: bool, result: str):
    assert ftr.next_fiscal_year("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextMonth(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextMonth(PropertyName='foo'))"],
    ],
)
def test_query_functions__next_month(ind: str, group: bool, result: str):
    assert ftr.next_month("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextWeek(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextWeek(PropertyName='foo'))"],
    ],
)
def test_query_functions__next_week(ind: str, group: bool, result: str):
    assert ftr.next_week("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextYear(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextYear(PropertyName='foo'))"],
    ],
)
def test_query_functions__next_year(ind: str, group: bool, result: str):
    assert ftr.next_year("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastXDays(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastXDays(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__last_x_days(ind: str, group: bool, result: str):
    assert ftr.last_x_days("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastXFiscalPeriods(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastXFiscalPeriods(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__last_x_fiscal_periods(ind: str, group: bool, result: str):
    assert ftr.last_x_fiscal_periods("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastXFiscalYears(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastXFiscalYears(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__last_x_fiscal_years(ind: str, group: bool, result: str):
    assert ftr.last_x_fiscal_years("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastXHours(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastXHours(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__last_x_hours(ind: str, group: bool, result: str):
    assert ftr.last_x_hours("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastXMonths(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastXMonths(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__last_x_months(ind: str, group: bool, result: str):
    assert ftr.last_x_months("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastXWeeks(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastXWeeks(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__last_x_weeks(ind: str, group: bool, result: str):
    assert ftr.last_x_weeks("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.LastXYears(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.LastXYears(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__last_x_years(ind: str, group: bool, result: str):
    assert ftr.last_x_years("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextXDays(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextXDays(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__next_x_days(ind: str, group: bool, result: str):
    assert ftr.next_x_days("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextXFiscalPeriods(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextXFiscalPeriods(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__next_x_fiscal_periods(ind: str, group: bool, result: str):
    assert ftr.next_x_fiscal_periods("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextXFiscalYears(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextXFiscalYears(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__next_x_fiscal_years(ind: str, group: bool, result: str):
    assert ftr.next_x_fiscal_years("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextXHours(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextXHours(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__next_x_hours(ind: str, group: bool, result: str):
    assert ftr.next_x_hours("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextXMonths(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextXMonths(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__next_x_months(ind: str, group: bool, result: str):
    assert ftr.next_x_months("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextXWeeks(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextXWeeks(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__next_x_weeks(ind: str, group: bool, result: str):
    assert ftr.next_x_weeks("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NextXYears(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NextXYears(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__next_x_years(ind: str, group: bool, result: str):
    assert ftr.next_x_years("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OlderThanXDays(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OlderThanXDays(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__older_than_x_days(ind: str, group: bool, result: str):
    assert ftr.older_than_x_days("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OlderThanXHours(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OlderThanXHours(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__older_than_x_hours(ind: str, group: bool, result: str):
    assert ftr.older_than_x_hours("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OlderThanXMinutes(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OlderThanXMinutes(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__older_than_x_minutes(ind: str, group: bool, result: str):
    assert ftr.older_than_x_minutes("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OlderThanXMonths(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OlderThanXMonths(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__older_than_x_months(ind: str, group: bool, result: str):
    assert ftr.older_than_x_months("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OlderThanXWeeks(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OlderThanXWeeks(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__older_than_x_weeks(ind: str, group: bool, result: str):
    assert ftr.older_than_x_weeks("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.OlderThanXYears(PropertyName='foo',PropertyValue=1)"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.OlderThanXYears(PropertyName='foo',PropertyValue=1))"],
    ],
)
def test_query_functions__older_than_x_years(ind: str, group: bool, result: str):
    assert ftr.older_than_x_years("foo", 1, ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.EqualBusinessId(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.EqualBusinessId(PropertyName='foo'))"],
    ],
)
def test_query_functions__equal_business_id(ind: str, group: bool, result: str):
    assert ftr.equal_business_id("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NotBusinessId(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NotBusinessId(PropertyName='foo'))"],
    ],
)
def test_query_functions__not_business_id(ind: str, group: bool, result: str):
    assert ftr.not_business_id("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.EqualUserId(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.EqualUserId(PropertyName='foo'))"],
    ],
)
def test_query_functions__equal_user_id(ind: str, group: bool, result: str):
    assert ftr.equal_user_id("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.NotUserId(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.NotUserId(PropertyName='foo'))"],
    ],
)
def test_query_functions__not_user_id(ind: str, group: bool, result: str):
    assert ftr.not_user_id("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.EqualUserLanguage(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.EqualUserLanguage(PropertyName='foo'))"],
    ],
)
def test_query_functions__equal_user_language(ind: str, group: bool, result: str):
    assert ftr.equal_user_language("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.EqualUserOrUserHierarchy(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.EqualUserOrUserHierarchy(PropertyName='foo'))"],
    ],
)
def test_query_functions__equal_user_or_user_hierarchy(ind: str, group: bool, result: str):
    assert ftr.equal_user_or_user_hierarchy("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.EqualUserOrUserHierarchyAndTeams(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.EqualUserOrUserHierarchyAndTeams(PropertyName='foo'))"],
    ],
)
def test_query_functions__equal_user_or_user_hierarchy_and_teams(ind: str, group: bool, result: str):
    assert ftr.equal_user_or_user_hierarchy_and_teams("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.EqualUserOrUserTeams(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.EqualUserOrUserTeams(PropertyName='foo'))"],
    ],
)
def test_query_functions__equal_user_or_user_teams(ind: str, group: bool, result: str):
    assert ftr.equal_user_or_user_teams("foo", ind, group) == result


@pytest.mark.parametrize(
    "ind,group,result",
    [
        [None, False, "Microsoft.Dynamics.CRM.EqualUserTeams(PropertyName='foo')"],
        ["fizzbuzz", True, "(fizzbuzz/Microsoft.Dynamics.CRM.EqualUserTeams(PropertyName='foo'))"],
    ],
)
def test_query_functions__equal_user_teams(ind: str, group: bool, result: str):
    assert ftr.equal_user_teams("foo", ind, group) == result


@pytest.mark.parametrize(
    "value,quotes,result",
    [
        [None, False, "null"],
        [False, False, "false"],
        [True, False, "true"],
        ["foo", False, "foo"],
        ["foo", True, "'foo'"],
    ],
)
def test_query_functions__type(value: Any, quotes: bool, result: str):
    assert ftr._type(value, quotes) == result
