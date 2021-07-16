"""

Creates a helper object `ftr`, which contains convenience functions of all possible filter operations.

Standard Operators API reference:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#standard-filter-operators

Special Operators API reference:
https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions?view=dynamics-ce-odata-9

"""

from typing import List, Union, Tuple


__all__ = [
    "ftr",
]


field_type = Union[str, int, float, bool, None]
comp_type = Union[str, int, float]


class OPS:
    """Convenience functions for creating $filter parameters."""

    # Base operations

    @staticmethod
    def _type(value: field_type, quotes: bool = False) -> str:
        if isinstance(value, bool):
            if value:
                return "'true'" if quotes else "true"
            else:
                return "'false'" if quotes else "false"
        elif value is None:
            return "'null'" if quotes else "null"
        else:
            return f"'{value}'" if quotes else str(value)

    @staticmethod
    def _group(result: str, group: bool) -> str:
        return f"({result})" if group else result

    @staticmethod
    def _listify(values: List[field_type], quotes: bool = True) -> str:
        return f"""[{','.join([f"{OPS._type(value, quotes)}" for value in values])}]"""

    @staticmethod
    def _comp_operator(param1: str, param2: field_type, operator: str, group: bool, quotes: bool = True) -> str:
        result = f"{param1} {operator} {OPS._type(param2, quotes)}"
        return OPS._group(result, group)

    @staticmethod
    def _join_multiple(*operations: str, **settings) -> str:
        result = f" {settings['operator']} ".join(operations)
        return OPS._group(result, settings["group"])

    @staticmethod
    def _query_operator(param1: str, param2: field_type, operator: str, group: bool) -> str:
        result = f"{operator}({OPS._type(param1)},{OPS._type(param2, quotes=True)})"
        return OPS._group(result, group)

    @staticmethod
    def _special_name_only(name: str, operator: str, group: bool, quotes: bool = True) -> str:
        result = f"Microsoft.Dynamics.CRM.{operator}" f"(PropertyName={OPS._type(name, quotes)})"
        return OPS._group(result, group)

    @staticmethod
    def _special_single_value(
        name: str,
        ref: field_type,
        operator: str,
        group: bool,
        name_quotes: bool = True,
        ref_quotes: bool = True,
    ) -> str:

        result = (
            f"Microsoft.Dynamics.CRM.{operator}"
            f"(PropertyName={OPS._type(name, name_quotes)},"
            f"PropertyValue={OPS._type(ref, ref_quotes)})"
        )
        return OPS._group(result, group)

    @staticmethod
    def _special_two_values(
        name: str,
        ref1: field_type,
        ref2: field_type,
        operator: str,
        group: bool,
        name_quotes: bool = True,
        ref1_quotes: bool = True,
        ref2_quotes: bool = True,
    ) -> str:

        result = (
            f"Microsoft.Dynamics.CRM.{operator}"
            f"(PropertyName={OPS._type(name, name_quotes)},"
            f"PropertyValue1={OPS._type(ref1, ref1_quotes)},"
            f"PropertyValue2={OPS._type(ref2, ref2_quotes)})"
        )
        return OPS._group(result, group)

    @staticmethod
    def _special_many_values(
        name: str,
        values: List[field_type],
        operator: str,
        group: bool,
        column_quotes: bool = True,
        values_quotes: bool = True,
    ) -> str:

        result = (
            f"Microsoft.Dynamics.CRM.{operator}"
            f"(PropertyName={OPS._type(name, column_quotes)},"
            f"PropertyValues={OPS._listify(values, values_quotes)})"
        )
        return OPS._group(result, group)

    # Comparison operations

    @staticmethod
    def eq(column: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        """Evaluate whether the value in the given column is equal to value."""
        return OPS._comp_operator(column, value, "eq", group, quotes)

    @staticmethod
    def ne(column: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        """Evaluate whether the value in the given column is not equal to value."""
        return OPS._comp_operator(column, value, "ne", group, quotes)

    @staticmethod
    def gt(column: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        """Evaluate whether the value in the given column is greater than value."""
        return OPS._comp_operator(column, value, "gt", group, quotes)

    @staticmethod
    def ge(column: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        """Evaluate whether the value in the given column is greater than or equal to value."""
        return OPS._comp_operator(column, value, "ge", group, quotes)

    @staticmethod
    def lt(column: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        """Evaluate whether the value in the given column is less than value."""
        return OPS._comp_operator(column, value, "lt", group, quotes)

    @staticmethod
    def le(column: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        """Evaluate whether the value in the given column is less than or equel to value."""
        return OPS._comp_operator(column, value, "le", group, quotes)

    # Logical operations

    @staticmethod
    def and_(*operations: str, **settings) -> str:
        """Evaluate whether all of the given operations are true."""
        return OPS._join_multiple(operator="and", group=settings.get("group", False), *operations)

    @staticmethod
    def or_(*operations: str, **settings) -> str:
        """Evaluate whether any of the given operations are true."""
        return OPS._join_multiple(operator="or", group=settings.get("group", False), *operations)

    @staticmethod
    def not_(operation: str, group: bool = False) -> str:
        """Invert the evaluation of an operation. Only works on standard operators!"""
        return OPS._group(f"not {operation}", group)

    # Standard query functions

    @staticmethod
    def contains(column: str, value: field_type, group: bool = False) -> str:
        """Evaluate whether the string value in the given column contains value."""
        return OPS._query_operator(column, value, "contains", group)

    @staticmethod
    def endswith(column: str, value: field_type, group: bool = False) -> str:
        """Evaluate whether the string value in the given column ends with value."""
        return OPS._query_operator(column, value, "endswith", group)

    @staticmethod
    def startswith(column: str, value: field_type, group: bool = False) -> str:
        """Evaluate whether the string value in the given column starts with value."""
        return OPS._query_operator(column, value, "startswith", group)

    # Special query functions - value checks

    @staticmethod
    def in_(column: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value in the given column exists in a list of values."""
        return OPS._special_many_values(column, values, "In", group)

    @staticmethod
    def not_in(column: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value in the given column doesn't exists in a list of values."""
        return OPS._special_many_values(column, values, "NotIn", group)

    @staticmethod
    def between(column: str, values: Tuple[comp_type, comp_type], group: bool = False) -> str:
        """Evaluate whether the value in the given column is between two values."""
        return OPS._special_many_values(column, list(values), "Between", group)

    @staticmethod
    def not_between(column: str, values: Tuple[comp_type, comp_type], group: bool = False) -> str:
        """Evaluate whether the value in the given column is not between two values."""
        return OPS._special_many_values(column, list(values), "NotBetween", group)

    @staticmethod
    def contain_values(column: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value in the given column contains the listed values."""
        return OPS._special_many_values(column, values, "ContainValues", group)

    @staticmethod
    def not_contain_values(column: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value in the given column doesn't contain the listed values."""
        return OPS._special_many_values(column, values, "DoesNotContainValues", group)

    # Special query functions - hierarchy checks

    @staticmethod
    def above(column: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the value in the given column is above ref in the hierarchy."""
        return OPS._special_single_value(column, ref, "Above", group)

    @staticmethod
    def above_or_equal(column: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the value in the given column is above or equal to ref in the hierarchy."""
        return OPS._special_single_value(column, ref, "AboveOrEqual", group)

    @staticmethod
    def under(column: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the value in the given column is below ref in the hierarchy."""
        return OPS._special_single_value(column, ref, "Under", group)

    @staticmethod
    def under_or_equal(column: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the value in column is under or equal to ref in the hierarchy."""
        return OPS._special_single_value(column, ref, "UnderOrEqual", group)

    @staticmethod
    def not_under(column: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the value in column is not below ref in the hierarchy."""
        return OPS._special_single_value(column, ref, "NotUnder", group)

    # Special query functions - dates

    @staticmethod
    def today(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals today’s date."""
        return OPS._special_name_only(column, "Today", group)

    @staticmethod
    def tomorrow(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals tomorrow’s date."""
        return OPS._special_name_only(column, "Tomorrow", group)

    @staticmethod
    def yesterday(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals yesterday’s date."""
        return OPS._special_name_only(column, "Yesterday", group)

    # Special query functions - dates - on

    @staticmethod
    def on(column: str, date: comp_type, group: bool = False) -> str:
        """Evaluates whether the value in the given column is on the specified date."""
        return OPS._special_single_value(column, date, "On", group)

    @staticmethod
    def on_or_after(column: str, date: comp_type, group: bool = False) -> str:
        """Evaluates whether the value in the given column is on or after the specified date."""
        return OPS._special_single_value(column, date, "OnOrAfter", group)

    @staticmethod
    def on_or_before(column: str, date: comp_type, group: bool = False) -> str:
        """Evaluates whether the value in the given column is on or before the specified date."""
        return OPS._special_single_value(column, date, "OnOrBefore", group)

    # Special query functions - dates - in

    @staticmethod
    def in_fiscal_period(column: str, period: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the specified fiscal period."""
        return OPS._special_single_value(column, period, "InFiscalPeriod", group, ref_quotes=False)

    @staticmethod
    def in_fiscal_period_and_year(column: str, period: int, year: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the specified fiscal period and year."""
        return OPS._special_two_values(
            column,
            period,
            year,
            "InFiscalPeriodAndYear",
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    @staticmethod
    def in_fiscal_year(column: str, year: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the specified fiscal year."""
        return OPS._special_single_value(column, year, "InFiscalYear", group, ref_quotes=False)

    @staticmethod
    def in_or_after_fiscal_period_and_year(column: str, period: int, year: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within or after the specified fiscal period and year."""
        return OPS._special_two_values(
            column,
            period,
            year,
            "InOrAfterFiscalPeriodAndYear",
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    @staticmethod
    def in_or_before_fiscal_period_and_year(column: str, period: int, year: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within, or before the specified fiscal period and year."""
        return OPS._special_two_values(
            column,
            period,
            year,
            "InOrBeforeFiscalPeriodAndYear ",
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    # Special query functions - dates - this

    @staticmethod
    def this_fiscal_period(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the current fiscal period."""
        return OPS._special_name_only(column, "ThisFiscalPeriod", group)

    @staticmethod
    def this_fiscal_year(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the current fiscal year."""
        return OPS._special_name_only(column, "ThisFiscalYear", group)

    @staticmethod
    def this_month(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the current month."""
        return OPS._special_name_only(column, "ThisMonth", group)

    @staticmethod
    def this_week(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the current week."""
        return OPS._special_name_only(column, "ThisWeek", group)

    @staticmethod
    def this_year(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the current year."""
        return OPS._special_name_only(column, "ThisYear", group)

    # Special query functions - dates - last

    @staticmethod
    def last_7_days(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last seven days including today."""
        return OPS._special_name_only(column, "Last7Days", group)

    @staticmethod
    def last_fiscal_period(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last fiscal period."""
        return OPS._special_name_only(column, "LastFiscalPeriod", group)

    @staticmethod
    def last_fiscal_year(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last fiscal year."""
        return OPS._special_name_only(column, "LastFiscalYear", group)

    @staticmethod
    def last_month(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last month."""
        return OPS._special_name_only(column, "LastMonth", group)

    @staticmethod
    def last_week(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last week."""
        return OPS._special_name_only(column, "LastWeek", group)

    @staticmethod
    def last_year(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last year."""
        return OPS._special_name_only(column, "LastYear", group)

    # Special query functions - dates - next

    @staticmethod
    def next_fiscal_period(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is in the next fiscal period."""
        return OPS._special_name_only(column, "NextFiscalPeriod", group)

    @staticmethod
    def next_fiscal_year(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is in the next fiscal year."""
        return OPS._special_name_only(column, "NextFiscalYear", group)

    @staticmethod
    def next_month(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is in the next month."""
        return OPS._special_name_only(column, "NextMonth", group)

    @staticmethod
    def next_week(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is in the next week."""
        return OPS._special_name_only(column, "NextWeek", group)

    @staticmethod
    def next_year(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next year."""
        return OPS._special_name_only(column, "NextYear", group)

    # Special query functions - dates - last x

    @staticmethod
    def last_x_days(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last X days."""
        return OPS._special_single_value(column, x, "LastXDays", group, ref_quotes=False)

    @staticmethod
    def last_x_fiscal_periods(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last X fiscal periods."""
        return OPS._special_single_value(column, x, "LastXFiscalPeriods", group, ref_quotes=False)

    @staticmethod
    def last_x_fiscal_years(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last X fiscal years."""
        return OPS._special_single_value(column, x, "LastXFiscalYears", group, ref_quotes=False)

    @staticmethod
    def last_x_hours(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last X hours."""
        return OPS._special_single_value(column, x, "LastXHours", group, ref_quotes=False)

    @staticmethod
    def last_x_months(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last X months."""
        return OPS._special_single_value(column, x, "LastXMonths", group, ref_quotes=False)

    @staticmethod
    def last_x_weeks(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last X weeks."""
        return OPS._special_single_value(column, x, "LastXWeeks", group, ref_quotes=False)

    @staticmethod
    def last_x_years(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the last X years."""
        return OPS._special_single_value(column, x, "LastXYears", group, ref_quotes=False)

    # Special query functions - dates - next x

    @staticmethod
    def next_x_days(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next X days."""
        return OPS._special_single_value(column, x, "NextXDays", group, ref_quotes=False)

    @staticmethod
    def next_x_fiscal_periods(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next X fiscal periods."""
        return OPS._special_single_value(column, x, "NextXFiscalPeriods", group, ref_quotes=False)

    @staticmethod
    def next_x_fiscal_years(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next X fiscal years."""
        return OPS._special_single_value(column, x, "NextXFiscalYears", group, ref_quotes=False)

    @staticmethod
    def next_x_hours(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next X hours."""
        return OPS._special_single_value(column, x, "NextXHours", group, ref_quotes=False)

    @staticmethod
    def next_x_months(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next X months."""
        return OPS._special_single_value(column, x, "NextXMonths", group, ref_quotes=False)

    @staticmethod
    def next_x_weeks(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next X weeks."""
        return OPS._special_single_value(column, x, "NextXWeeks", group, ref_quotes=False)

    @staticmethod
    def next_x_years(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is within the next X years."""
        return OPS._special_single_value(column, x, "NextXYears", group, ref_quotes=False)

    # Special query functions - dates - older than x

    @staticmethod
    def older_than_x_days(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is older than the specified amount of days."""
        return OPS._special_single_value(column, x, "OlderThanXDays", group, ref_quotes=False)

    @staticmethod
    def older_than_x_hours(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is older than the specified amount of hours."""
        return OPS._special_single_value(column, x, "OlderThanXHours", group, ref_quotes=False)

    @staticmethod
    def older_than_x_minutes(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is older than the specified amount of minutes."""
        return OPS._special_single_value(column, x, "OlderThanXMinutes", group, ref_quotes=False)

    @staticmethod
    def older_than_x_months(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is older than the specified amount of moths."""
        return OPS._special_single_value(column, x, "OlderThanXMonths", group, ref_quotes=False)

    @staticmethod
    def older_than_x_weeks(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is older than the specified amount of weeks."""
        return OPS._special_single_value(column, x, "OlderThanXWeeks", group, ref_quotes=False)

    @staticmethod
    def older_than_x_years(column: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value in the given column is older than the specified amount of years."""
        return OPS._special_single_value(column, x, "OlderThanXYears", group, ref_quotes=False)

    # Special query functions - business id checks

    @staticmethod
    def equal_business_id(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is equal to the specified business ID."""
        return OPS._special_name_only(column, "EqualBusinessId", group)

    @staticmethod
    def not_business_id(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is not equal to the specified business ID."""
        return OPS._special_name_only(column, "NotBusinessId", group)

    # Special query functions - user id checks

    @staticmethod
    def equal_user_id(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is equal to the ID of the user."""
        return OPS._special_name_only(column, "EqualUserId", group)

    @staticmethod
    def not_user_id(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is not equal to the ID of the user."""
        return OPS._special_name_only(column, "NotUserId", group)

    # Special query functions - misc

    @staticmethod
    def equal_user_language(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column is equal to the language for the user."""
        return OPS._special_name_only(column, "EqualUserLanguage", group)

    @staticmethod
    def equal_user_or_user_hierarchy(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals current user or their reporting hierarchy."""
        return OPS._special_name_only(column, "EqualUserOrUserHierarchy", group)

    @staticmethod
    def equal_user_or_user_hierarchy_and_teams(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals current user,
        or their reporting hierarchy and teams."""
        return OPS._special_name_only(column, "EqualUserOrUserHierarchyAndTeams", group)

    @staticmethod
    def equal_user_or_user_teams(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals current user or user teams."""
        return OPS._special_name_only(column, "EqualUserOrUserTeams", group)

    @staticmethod
    def equal_user_teams(column: str, group: bool = False) -> str:
        """Evaluates whether the value in the given column equals current user teams."""
        return OPS._special_name_only(column, "EqualUserTeams", group)


ftr = OPS()
"""Convenience functions for creating $filter parameters."""
