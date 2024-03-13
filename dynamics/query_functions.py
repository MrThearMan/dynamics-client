"""
Creates a helper object `ftr`, which contains convenience functions of all possible filter operations.

Standard Operators API reference:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#standard-filter-operators

Special Operators API reference:
https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions?view=dynamics-ce-odata-9
"""

from typing import Any

from .typing import CompType, FieldType, List, Optional, Tuple
from .utils import is_valid_uuid

__all__ = ["ftr"]


class ftr:  # noqa: N801
    """Convenience functions for creating $filter parameters."""

    # Base operations

    @staticmethod
    def _type(value: FieldType, quotes: bool = False) -> str:
        if value is True:
            return "true"
        if value is False:
            return "false"
        if value is None:
            return "null"

        return f"'{value}'" if quotes else str(value)

    @staticmethod
    def _group(result: str, group: bool) -> str:
        return f"({result})" if group else result

    @staticmethod
    def _listify(values: List[FieldType]) -> str:
        return f"""[{','.join([f"{ftr._type(value, quotes=True)}" for value in values])}]"""

    @staticmethod
    def _get_indicator(indicator: Optional[str]) -> str:
        return f"{indicator}/" if indicator is not None else ""

    @staticmethod
    def _comp_operator(
        param1: str,
        param2: FieldType,
        lambda_indicator: Optional[str],
        operator: str,
        group: bool,
    ) -> str:
        ind = ftr._get_indicator(lambda_indicator)
        quotes = isinstance(param2, str) and not is_valid_uuid(param2)
        result = f"{ind}{param1} {operator} {ftr._type(param2, quotes)}"
        return ftr._group(result, group)

    @staticmethod
    def _join_multiple(*operations: str, **settings: Any) -> str:
        result = f" {settings['operator']} ".join(operations)
        return ftr._group(result, settings["group"])

    @staticmethod
    def _query_operator(
        param1: str,
        param2: FieldType,
        operator: str,
        lambda_indicator: Optional[str],
        group: bool,
    ) -> str:
        ind = ftr._get_indicator(lambda_indicator)
        result = f"{operator}({ind}{ftr._type(param1)},{ftr._type(param2, quotes=True)})"
        return ftr._group(result, group)

    @staticmethod
    def _lambda_operator(  # noqa: PLR0913
        collection: str,
        operator: str,
        indicator: str,
        lambda_indicator: Optional[str],
        operation: Optional[str],
        group: bool,
    ) -> str:
        ind = ftr._get_indicator(lambda_indicator)
        operation = f"{indicator}:{operation}" if operation is not None else ""
        result = f"{ind}{collection}/{operator}({operation})"
        return ftr._group(result, group)

    @staticmethod
    def _special_name_only(
        name: str,
        operator: str,
        lambda_indicator: Optional[str],
        group: bool,
    ) -> str:
        ind = ftr._get_indicator(lambda_indicator)
        result = f"{ind}Microsoft.Dynamics.CRM.{operator}" f"(PropertyName={ftr._type(name, quotes=True)})"
        return ftr._group(result, group)

    @staticmethod
    def _special_single_value(  # noqa: PLR0913
        name: str,
        ref: FieldType,
        operator: str,
        lambda_indicator: Optional[str],
        group: bool,
        ref_quotes: bool = True,
    ) -> str:
        ind = ftr._get_indicator(lambda_indicator)
        result = (
            f"{ind}Microsoft.Dynamics.CRM.{operator}"
            f"(PropertyName={ftr._type(name, quotes=True)},"
            f"PropertyValue={ftr._type(ref, ref_quotes)})"
        )
        return ftr._group(result, group)

    @staticmethod
    def _special_two_values(  # noqa: PLR0913
        name: str,
        ref1: FieldType,
        ref2: FieldType,
        operator: str,
        lambda_indicator: Optional[str],
        group: bool,
        ref1_quotes: bool = True,
        ref2_quotes: bool = True,
    ) -> str:
        ind = ftr._get_indicator(lambda_indicator)
        result = (
            f"{ind}Microsoft.Dynamics.CRM.{operator}"
            f"(PropertyName={ftr._type(name, quotes=True)},"
            f"PropertyValue1={ftr._type(ref1, ref1_quotes)},"
            f"PropertyValue2={ftr._type(ref2, ref2_quotes)})"
        )
        return ftr._group(result, group)

    @staticmethod
    def _special_many_values(
        name: str,
        values: List[FieldType],
        operator: str,
        lambda_indicator: Optional[str],
        group: bool,
    ) -> str:
        ind = ftr._get_indicator(lambda_indicator)
        result = (
            f"{ind}Microsoft.Dynamics.CRM.{operator}"
            f"(PropertyName={ftr._type(name, quotes=True)},"
            f"PropertyValues={ftr._listify(values)})"
        )
        return ftr._group(result, group)

    # Comparison operations

    @staticmethod
    def eq(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the value in the given column is equal to value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should equal to.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._comp_operator(column, value, lambda_indicator, "eq", group)

    @staticmethod
    def ne(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the value in the given column is not equal to value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should not equal to.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._comp_operator(column, value, lambda_indicator, "ne", group)

    @staticmethod
    def gt(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the value in the given column is greater than value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should be greater than.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._comp_operator(column, value, lambda_indicator, "gt", group)

    @staticmethod
    def ge(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the value in the given column is greater than or equal to value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should be greater than or equal to.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._comp_operator(column, value, lambda_indicator, "ge", group)

    @staticmethod
    def lt(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the value in the given column is less than value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should less than.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._comp_operator(column, value, lambda_indicator, "lt", group)

    @staticmethod
    def le(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the value in the given column is less than or equal to value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should less than or equal to.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._comp_operator(column, value, lambda_indicator, "le", group)

    # Logical operations

    @staticmethod
    def and_(*args: str, **kwargs: Any) -> str:
        """
        Evaluate whether all the given operations are true.

        :param args: Other filter operation strings to `and` together.
        :param kwargs: group=True -> Group the operation inside parentheses.
        """
        return ftr._join_multiple(*args, operator="and", group=kwargs.get("group", False))

    @staticmethod
    def or_(*args: str, **kwargs: Any) -> str:
        """
        Evaluate whether any of the given operations are true.

        :param args: Other filter operation strings to `or` together.
        :param kwargs: group=True -> Group the operation inside parentheses.
        """
        return ftr._join_multiple(*args, operator="or", group=kwargs.get("group", False))

    @staticmethod
    def not_(operation: str, group: bool = False) -> str:
        """Invert the evaluation of an operation. Only works on standard operators!"""
        return ftr._group(f"not {operation}", group)

    # Standard query functions

    @staticmethod
    def contains(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the string value in the given column contains value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should contain.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._query_operator(column, value, "contains", lambda_indicator, group)

    @staticmethod
    def endswith(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the string value in the given column ends with value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should end with.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._query_operator(column, value, "endswith", lambda_indicator, group)

    @staticmethod
    def startswith(column: str, value: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """
        Evaluate whether the string value in the given column starts with value.

        :param column: Column to apply the operation to.
        :param value: Value that the column should start with.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._query_operator(column, value, "startswith", lambda_indicator, group)

    # Lambda operations

    @staticmethod
    def any_(
        collection: str,
        indicator: str,
        operation: Optional[str] = None,
        lambda_indicator: Optional[str] = None,
        group: bool = False,
    ) -> str:
        """
        True if the operation given is true for any member of the collection, otherwise false.
        True also if operation is not given, and the collection is not empty.

        :param collection: Name of the collection-valued navigation property for some table,
                           for the members of which the given operation is evaluated.
        :param indicator: Item indicator to use inside the statement, typically a single letter.
                          The same indicator should be given to the operation(s) evaluated inside this operation.
        :param operation: Operation(s) evaluated inside this operation.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._lambda_operator(collection, "any", indicator, lambda_indicator, operation, group)

    @staticmethod
    def all_(
        collection: str,
        indicator: str,
        operation: Optional[str] = None,
        lambda_indicator: Optional[str] = None,
        group: bool = False,
    ) -> str:
        """
        True if the operation given is true for all members of the collection, otherwise false.

        :param collection: Name of the collection-valued navigation property for some table,
                           for the members of which the given operation is evaluated.
        :param indicator: Indicator to use inside the statement, typically a single letter.
                          The same indicator should be given to the operation(s) evaluated inside this operation.
        :param operation: Operation(s) evaluated inside this operation.
        :param lambda_indicator: If this operation is evaluated inside a lambda operation,
                                 provide the lambda operations item indicator here.
        :param group: Group the operation inside parentheses.
        """
        return ftr._lambda_operator(collection, "all", indicator, lambda_indicator, operation, group)

    # Special query functions - value checks

    @staticmethod
    def in_(column: str, values: List[FieldType], lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluate whether the value in the given column exists in a list of values."""
        return ftr._special_many_values(column, values, "In", lambda_indicator, group)

    @staticmethod
    def not_in(
        column: str, values: List[FieldType], lambda_indicator: Optional[str] = None, group: bool = False
    ) -> str:
        """Evaluate whether the value in the given column doesn't exist in a list of values."""
        return ftr._special_many_values(column, values, "NotIn", lambda_indicator, group)

    @staticmethod
    def between(
        column: str, values: Tuple[CompType, CompType], lambda_indicator: Optional[str] = None, group: bool = False
    ) -> str:
        """Evaluate whether the value in the given column is between two values."""
        return ftr._special_many_values(column, list(values), "Between", lambda_indicator, group)

    @staticmethod
    def not_between(
        column: str,
        values: Tuple[CompType, CompType],
        lambda_indicator: Optional[str] = None,
        group: bool = False,
    ) -> str:
        """Evaluate whether the value in the given column is not between two values."""
        return ftr._special_many_values(column, list(values), "NotBetween", lambda_indicator, group)

    @staticmethod
    def contain_values(
        column: str,
        values: List[FieldType],
        lambda_indicator: Optional[str] = None,
        group: bool = False,
    ) -> str:
        """Evaluate whether the value in the given column contains the listed values."""
        return ftr._special_many_values(column, values, "ContainValues", lambda_indicator, group)

    @staticmethod
    def not_contain_values(
        column: str, values: List[FieldType], lambda_indicator: Optional[str] = None, group: bool = False
    ) -> str:
        """Evaluate whether the value in the given column doesn't contain the listed values."""
        return ftr._special_many_values(column, values, "DoesNotContainValues", lambda_indicator, group)

    # Special query functions - hierarchy checks

    @staticmethod
    def above(column: str, ref: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is above ref in the hierarchy."""
        return ftr._special_single_value(column, ref, "Above", lambda_indicator, group)

    @staticmethod
    def above_or_equal(column: str, ref: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is above or equal to ref in the hierarchy."""
        return ftr._special_single_value(column, ref, "AboveOrEqual", lambda_indicator, group)

    @staticmethod
    def under(column: str, ref: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is below ref in the hierarchy."""
        return ftr._special_single_value(column, ref, "Under", lambda_indicator, group)

    @staticmethod
    def under_or_equal(column: str, ref: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in column is under or equal to ref in the hierarchy."""
        return ftr._special_single_value(column, ref, "UnderOrEqual", lambda_indicator, group)

    @staticmethod
    def not_under(column: str, ref: FieldType, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in column is not below ref in the hierarchy."""
        return ftr._special_single_value(column, ref, "NotUnder", lambda_indicator, group)

    # Special query functions - dates

    @staticmethod
    def today(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals today's date."""
        return ftr._special_name_only(column, "Today", lambda_indicator, group)

    @staticmethod
    def tomorrow(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals tomorrow's date."""
        return ftr._special_name_only(column, "Tomorrow", lambda_indicator, group)

    @staticmethod
    def yesterday(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals yesterday's date."""
        return ftr._special_name_only(column, "Yesterday", lambda_indicator, group)

    # Special query functions - dates - on

    @staticmethod
    def on(column: str, date: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is on the specified date."""
        return ftr._special_single_value(column, date, "On", lambda_indicator, group)

    @staticmethod
    def on_or_after(column: str, date: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is on or after the specified date."""
        return ftr._special_single_value(column, date, "OnOrAfter", lambda_indicator, group)

    @staticmethod
    def on_or_before(column: str, date: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is on or before the specified date."""
        return ftr._special_single_value(column, date, "OnOrBefore", lambda_indicator, group)

    # Special query functions - dates - in

    @staticmethod
    def in_fiscal_period(column: str, period: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the specified fiscal period."""
        return ftr._special_single_value(column, period, "InFiscalPeriod", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def in_fiscal_period_and_year(
        column: str,
        period: int,
        year: int,
        lambda_indicator: Optional[str] = None,
        group: bool = False,
    ) -> str:
        """Evaluates whether the date in the given column is within the specified fiscal period and year."""
        return ftr._special_two_values(
            column,
            period,
            year,
            "InFiscalPeriodAndYear",
            lambda_indicator,
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    @staticmethod
    def in_fiscal_year(column: str, year: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the specified fiscal year."""
        return ftr._special_single_value(column, year, "InFiscalYear", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def in_or_after_fiscal_period_and_year(
        column: str, period: int, year: int, lambda_indicator: Optional[str] = None, group: bool = False
    ) -> str:
        """Evaluates whether the date in the given column is within or after the specified fiscal period and year."""
        return ftr._special_two_values(
            column,
            period,
            year,
            "InOrAfterFiscalPeriodAndYear",
            lambda_indicator,
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    @staticmethod
    def in_or_before_fiscal_period_and_year(
        column: str, period: int, year: int, lambda_indicator: Optional[str] = None, group: bool = False
    ) -> str:
        """Evaluates whether the date in the given column is within, or before the specified fiscal period and year."""
        return ftr._special_two_values(
            column,
            period,
            year,
            "InOrBeforeFiscalPeriodAndYear",
            lambda_indicator,
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    # Special query functions - dates - this

    @staticmethod
    def this_fiscal_period(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the current fiscal period."""
        return ftr._special_name_only(column, "ThisFiscalPeriod", lambda_indicator, group)

    @staticmethod
    def this_fiscal_year(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the current fiscal year."""
        return ftr._special_name_only(column, "ThisFiscalYear", lambda_indicator, group)

    @staticmethod
    def this_month(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the current month."""
        return ftr._special_name_only(column, "ThisMonth", lambda_indicator, group)

    @staticmethod
    def this_week(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the current week."""
        return ftr._special_name_only(column, "ThisWeek", lambda_indicator, group)

    @staticmethod
    def this_year(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the current year."""
        return ftr._special_name_only(column, "ThisYear", lambda_indicator, group)

    # Special query functions - dates - last

    @staticmethod
    def last_7_days(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last seven days including today."""
        return ftr._special_name_only(column, "Last7Days", lambda_indicator, group)

    @staticmethod
    def last_fiscal_period(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last fiscal period."""
        return ftr._special_name_only(column, "LastFiscalPeriod", lambda_indicator, group)

    @staticmethod
    def last_fiscal_year(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last fiscal year."""
        return ftr._special_name_only(column, "LastFiscalYear", lambda_indicator, group)

    @staticmethod
    def last_month(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last month."""
        return ftr._special_name_only(column, "LastMonth", lambda_indicator, group)

    @staticmethod
    def last_week(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last week."""
        return ftr._special_name_only(column, "LastWeek", lambda_indicator, group)

    @staticmethod
    def last_year(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last year."""
        return ftr._special_name_only(column, "LastYear", lambda_indicator, group)

    # Special query functions - dates - next

    @staticmethod
    def next_fiscal_period(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is in the next fiscal period."""
        return ftr._special_name_only(column, "NextFiscalPeriod", lambda_indicator, group)

    @staticmethod
    def next_fiscal_year(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is in the next fiscal year."""
        return ftr._special_name_only(column, "NextFiscalYear", lambda_indicator, group)

    @staticmethod
    def next_month(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is in the next month."""
        return ftr._special_name_only(column, "NextMonth", lambda_indicator, group)

    @staticmethod
    def next_week(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is in the next week."""
        return ftr._special_name_only(column, "NextWeek", lambda_indicator, group)

    @staticmethod
    def next_year(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next year."""
        return ftr._special_name_only(column, "NextYear", lambda_indicator, group)

    # Special query functions - dates - last x

    @staticmethod
    def last_x_days(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last X days."""
        return ftr._special_single_value(column, x, "LastXDays", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def last_x_fiscal_periods(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last X fiscal periods."""
        return ftr._special_single_value(column, x, "LastXFiscalPeriods", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def last_x_fiscal_years(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last X fiscal years."""
        return ftr._special_single_value(column, x, "LastXFiscalYears", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def last_x_hours(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last X hours."""
        return ftr._special_single_value(column, x, "LastXHours", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def last_x_months(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last X months."""
        return ftr._special_single_value(column, x, "LastXMonths", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def last_x_weeks(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last X weeks."""
        return ftr._special_single_value(column, x, "LastXWeeks", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def last_x_years(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the last X years."""
        return ftr._special_single_value(column, x, "LastXYears", lambda_indicator, group, ref_quotes=False)

    # Special query functions - dates - next x

    @staticmethod
    def next_x_days(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next X days."""
        return ftr._special_single_value(column, x, "NextXDays", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def next_x_fiscal_periods(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next X fiscal periods."""
        return ftr._special_single_value(column, x, "NextXFiscalPeriods", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def next_x_fiscal_years(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next X fiscal years."""
        return ftr._special_single_value(column, x, "NextXFiscalYears", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def next_x_hours(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next X hours."""
        return ftr._special_single_value(column, x, "NextXHours", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def next_x_months(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next X months."""
        return ftr._special_single_value(column, x, "NextXMonths", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def next_x_weeks(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next X weeks."""
        return ftr._special_single_value(column, x, "NextXWeeks", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def next_x_years(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is within the next X years."""
        return ftr._special_single_value(column, x, "NextXYears", lambda_indicator, group, ref_quotes=False)

    # Special query functions - dates - older than x

    @staticmethod
    def older_than_x_days(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is older than the specified amount of days."""
        return ftr._special_single_value(column, x, "OlderThanXDays", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def older_than_x_hours(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is older than the specified amount of hours."""
        return ftr._special_single_value(column, x, "OlderThanXHours", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def older_than_x_minutes(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is older than the specified amount of minutes."""
        return ftr._special_single_value(column, x, "OlderThanXMinutes", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def older_than_x_months(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is older than the specified amount of moths."""
        return ftr._special_single_value(column, x, "OlderThanXMonths", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def older_than_x_weeks(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is older than the specified amount of weeks."""
        return ftr._special_single_value(column, x, "OlderThanXWeeks", lambda_indicator, group, ref_quotes=False)

    @staticmethod
    def older_than_x_years(column: str, x: int, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the date in the given column is older than the specified amount of years."""
        return ftr._special_single_value(column, x, "OlderThanXYears", lambda_indicator, group, ref_quotes=False)

    # Special query functions - business id checks

    @staticmethod
    def equal_business_id(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is equal to the specified business ID."""
        return ftr._special_name_only(column, "EqualBusinessId", lambda_indicator, group)

    @staticmethod
    def not_business_id(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is not equal to the specified business ID."""
        return ftr._special_name_only(column, "NotBusinessId", lambda_indicator, group)

    # Special query functions - user id checks

    @staticmethod
    def equal_user_id(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is equal to the ID of the user."""
        return ftr._special_name_only(column, "EqualUserId", lambda_indicator, group)

    @staticmethod
    def not_user_id(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is not equal to the ID of the user."""
        return ftr._special_name_only(column, "NotUserId", lambda_indicator, group)

    # Special query functions - misc

    @staticmethod
    def equal_user_language(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column is equal to the language for the user."""
        return ftr._special_name_only(column, "EqualUserLanguage", lambda_indicator, group)

    @staticmethod
    def equal_user_or_user_hierarchy(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals current user or their reporting hierarchy."""
        return ftr._special_name_only(column, "EqualUserOrUserHierarchy", lambda_indicator, group)

    @staticmethod
    def equal_user_or_user_hierarchy_and_teams(
        column: str,
        lambda_indicator: Optional[str] = None,
        group: bool = False,
    ) -> str:
        """
        Evaluates whether the value in the given column equals current user,
        or their reporting hierarchy and teams.
        """
        return ftr._special_name_only(column, "EqualUserOrUserHierarchyAndTeams", lambda_indicator, group)

    @staticmethod
    def equal_user_or_user_teams(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals current user or user teams."""
        return ftr._special_name_only(column, "EqualUserOrUserTeams", lambda_indicator, group)

    @staticmethod
    def equal_user_teams(column: str, lambda_indicator: Optional[str] = None, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals current user teams."""
        return ftr._special_name_only(column, "EqualUserTeams", lambda_indicator, group)
