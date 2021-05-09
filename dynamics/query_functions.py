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
        entity_quotes: bool = True,
        values_quotes: bool = True,
    ) -> str:

        result = (
            f"Microsoft.Dynamics.CRM.{operator}"
            f"(PropertyName={OPS._type(name, entity_quotes)},"
            f"PropertyValues={OPS._listify(values, values_quotes)})"
        )
        return OPS._group(result, group)

    # Comparison operations

    @staticmethod
    def eq(key: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        return OPS._comp_operator(key, value, "eq", group, quotes)

    @staticmethod
    def ne(key: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        return OPS._comp_operator(key, value, "ne", group, quotes)

    @staticmethod
    def gt(key: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        return OPS._comp_operator(key, value, "gt", group, quotes)

    @staticmethod
    def ge(key: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        return OPS._comp_operator(key, value, "ge", group, quotes)

    @staticmethod
    def lt(key: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        return OPS._comp_operator(key, value, "lt", group, quotes)

    @staticmethod
    def le(key: str, value: field_type, group: bool = False, quotes: bool = False) -> str:
        return OPS._comp_operator(key, value, "le", group, quotes)

    # Logical operations

    @staticmethod
    def and_(op1: str, op2: str, group: bool = False) -> str:
        return OPS._comp_operator(op1, op2, "and", group)

    @staticmethod
    def or_(op1: str, op2: str, group: bool = False) -> str:
        return OPS._comp_operator(op1, op2, "or", group)

    @staticmethod
    def not_(operation: str, group: bool = False) -> str:
        """Note: Only works on Standard Operators!"""
        result = f"not {operation}"
        return OPS._group(result, group)

    # Standard query functions

    @staticmethod
    def contains(name: str, value: field_type, group: bool = False) -> str:
        return OPS._query_operator(name, value, "contains", group)

    @staticmethod
    def endswith(name: str, value: field_type, group: bool = False) -> str:
        return OPS._query_operator(name, value, "endswith", group)

    @staticmethod
    def startswith(name: str, value: field_type, group: bool = False) -> str:
        return OPS._query_operator(name, value, "startswith", group)

    # Special query functions - value checks

    @staticmethod
    def in_(entity: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value of 'entity' exists in a list of values."""
        return OPS._special_many_values(entity, values, "In", group)

    @staticmethod
    def not_in(entity: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value of 'entity' doesn't exists in a list of values."""
        return OPS._special_many_values(entity, values, "NotIn", group)

    @staticmethod
    def between(entity: str, values: Tuple[comp_type, comp_type], group: bool = False) -> str:
        """Evaluate whether the value of 'entity' is between two values."""
        return OPS._special_many_values(entity, list(values), "Between", group)

    @staticmethod
    def not_between(entity: str, values: Tuple[comp_type, comp_type], group: bool = False) -> str:
        """Evaluate whether the value of 'entity' is not between two values."""
        return OPS._special_many_values(entity, list(values), "NotBetween", group)

    @staticmethod
    def contain_values(entity: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value of 'entity' contains the listed values."""
        return OPS._special_many_values(entity, values, "ContainValues", group)

    @staticmethod
    def not_contain_values(entity: str, values: List[field_type], group: bool = False) -> str:
        """Evaluate whether the value of 'entity' doesn't contain the listed values."""
        return OPS._special_many_values(entity, values, "DoesNotContainValues", group)

    # Special query functions - hierarchy checks

    @staticmethod
    def above(entity: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the entity is above the referenced entity in the hierarchy."""
        return OPS._special_single_value(entity, ref, "Above", group)

    @staticmethod
    def above_or_equal(entity: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the entity is above or equal to the referenced entity in the hierarchy."""
        return OPS._special_single_value(entity, ref, "AboveOrEqual", group)

    @staticmethod
    def under(entity: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the entity is below the referenced record in the hierarchy."""
        return OPS._special_single_value(entity, ref, "Under", group)

    @staticmethod
    def under_or_equal(entity: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the entity is under or equal to the referenced entity in the hierarchy."""
        return OPS._special_single_value(entity, ref, "UnderOrEqual", group)

    @staticmethod
    def not_under(entity: str, ref: field_type, group: bool = False) -> str:
        """Evaluates whether the entity is not below the referenced record in the hierarchy."""
        return OPS._special_single_value(entity, ref, "NotUnder", group)

    # Special query functions - dates

    @staticmethod
    def today(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' equals today’s date."""
        return OPS._special_name_only(entity, "Today", group)

    @staticmethod
    def tomorrow(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' equals tomorrow’s date."""
        return OPS._special_name_only(entity, "Tomorrow", group)

    @staticmethod
    def yesterday(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' equals yesterday’s date."""
        return OPS._special_name_only(entity, "Yesterday", group)

    # Special query functions - dates - on

    @staticmethod
    def on(entity: str, ref: comp_type, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is on the specified date."""
        return OPS._special_single_value(entity, ref, "On", group)

    @staticmethod
    def on_or_after(entity: str, ref: comp_type, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is on or after the specified date."""
        return OPS._special_single_value(entity, ref, "OnOrAfter", group)

    @staticmethod
    def on_or_before(entity: str, ref: comp_type, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is on or before the specified date."""
        return OPS._special_single_value(entity, ref, "OnOrBefore", group)

    # Special query functions - dates - in

    @staticmethod
    def in_fiscal_period(entity: str, ref: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the specified fiscal period."""
        return OPS._special_single_value(entity, ref, "InFiscalPeriod", group, ref_quotes=False)

    @staticmethod
    def in_fiscal_period_and_year(entity: str, ref1: int, ref2: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the specified fiscal period and year."""
        return OPS._special_two_values(
            entity,
            ref1,
            ref2,
            "InFiscalPeriodAndYear",
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    @staticmethod
    def in_fiscal_year(entity: str, ref: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the specified fiscal year."""
        return OPS._special_single_value(entity, ref, "InFiscalYear", group, ref_quotes=False)

    @staticmethod
    def in_or_after_fiscal_period_and_year(entity: str, ref1: int, ref2: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within or after the specified fiscal period and year."""
        return OPS._special_two_values(
            entity,
            ref1,
            ref2,
            "InOrAfterFiscalPeriodAndYear",
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    @staticmethod
    def in_or_before_fiscal_period_and_year(entity: str, ref1: int, ref2: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within or before the specified fiscal period and year."""
        return OPS._special_two_values(
            entity,
            ref1,
            ref2,
            "InOrBeforeFiscalPeriodAndYear ",
            group,
            ref1_quotes=False,
            ref2_quotes=False,
        )

    # Special query functions - dates - this

    @staticmethod
    def this_fiscal_period(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the current fiscal period."""
        return OPS._special_name_only(entity, "ThisFiscalPeriod", group)

    @staticmethod
    def this_fiscal_year(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the current fiscal year."""
        return OPS._special_name_only(entity, "ThisFiscalYear", group)

    @staticmethod
    def this_month(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the current month."""
        return OPS._special_name_only(entity, "ThisMonth", group)

    @staticmethod
    def this_week(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the current week."""
        return OPS._special_name_only(entity, "ThisWeek", group)

    @staticmethod
    def this_year(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the current year."""
        return OPS._special_name_only(entity, "ThisYear", group)

    # Special query functions - dates - last

    @staticmethod
    def last_7_days(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last seven days including today."""
        return OPS._special_name_only(entity, "Last7Days", group)

    @staticmethod
    def last_fiscal_period(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last fiscal period."""
        return OPS._special_name_only(entity, "LastFiscalPeriod", group)

    @staticmethod
    def last_fiscal_year(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last fiscal year."""
        return OPS._special_name_only(entity, "LastFiscalYear", group)

    @staticmethod
    def last_month(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last month."""
        return OPS._special_name_only(entity, "LastMonth", group)

    @staticmethod
    def last_week(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last week."""
        return OPS._special_name_only(entity, "LastWeek", group)

    @staticmethod
    def last_year(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last year."""
        return OPS._special_name_only(entity, "LastYear", group)

    # Special query functions - dates - next

    @staticmethod
    def next_fiscal_period(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is in the next fiscal period."""
        return OPS._special_name_only(entity, "NextFiscalPeriod", group)

    @staticmethod
    def next_fiscal_year(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is in the next fiscal year."""
        return OPS._special_name_only(entity, "NextFiscalYear", group)

    @staticmethod
    def next_month(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is in the next month."""
        return OPS._special_name_only(entity, "NextMonth", group)

    @staticmethod
    def next_week(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is in the next week."""
        return OPS._special_name_only(entity, "NextWeek", group)

    @staticmethod
    def next_year(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next year."""
        return OPS._special_name_only(entity, "NextYear", group)

    # Special query functions - dates - last x

    @staticmethod
    def last_x_days(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last X days."""
        return OPS._special_single_value(entity, x, "LastXDays", group, ref_quotes=False)

    @staticmethod
    def last_x_fiscal_periods(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last X fiscal periods."""
        return OPS._special_single_value(entity, x, "LastXFiscalPeriods", group, ref_quotes=False)

    @staticmethod
    def last_x_fiscal_years(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last X fiscal years."""
        return OPS._special_single_value(entity, x, "LastXFiscalYears", group, ref_quotes=False)

    @staticmethod
    def last_x_hours(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last X hours."""
        return OPS._special_single_value(entity, x, "LastXHours", group, ref_quotes=False)

    @staticmethod
    def last_x_months(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last X months."""
        return OPS._special_single_value(entity, x, "LastXMonths", group, ref_quotes=False)

    @staticmethod
    def last_x_weeks(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last X weeks."""
        return OPS._special_single_value(entity, x, "LastXWeeks", group, ref_quotes=False)

    @staticmethod
    def last_x_years(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the last X years."""
        return OPS._special_single_value(entity, x, "LastXYears", group, ref_quotes=False)

    # Special query functions - dates - next x

    @staticmethod
    def next_x_days(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next X days."""
        return OPS._special_single_value(entity, x, "NextXDays", group, ref_quotes=False)

    @staticmethod
    def next_x_fiscal_periods(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next X fiscal periods."""
        return OPS._special_single_value(entity, x, "NextXFiscalPeriods", group, ref_quotes=False)

    @staticmethod
    def next_x_fiscal_years(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next X fiscal years."""
        return OPS._special_single_value(entity, x, "NextXFiscalYears", group, ref_quotes=False)

    @staticmethod
    def next_x_hours(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next X hours."""
        return OPS._special_single_value(entity, x, "NextXHours", group, ref_quotes=False)

    @staticmethod
    def next_x_months(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next X months."""
        return OPS._special_single_value(entity, x, "NextXMonths", group, ref_quotes=False)

    @staticmethod
    def next_x_weeks(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next X weeks."""
        return OPS._special_single_value(entity, x, "NextXWeeks", group, ref_quotes=False)

    @staticmethod
    def next_x_years(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is within the next X years."""
        return OPS._special_single_value(entity, x, "NextXYears", group, ref_quotes=False)

    # Special query functions - dates - older than x

    @staticmethod
    def older_than_x_days(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is older than the specified amount of days."""
        return OPS._special_single_value(entity, x, "OlderThanXDays", group, ref_quotes=False)

    @staticmethod
    def older_than_x_hours(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is older than the specified amount of hours."""
        return OPS._special_single_value(entity, x, "OlderThanXHours", group, ref_quotes=False)

    @staticmethod
    def older_than_x_minutes(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is older than the specified amount of minutes."""
        return OPS._special_single_value(entity, x, "OlderThanXMinutes", group, ref_quotes=False)

    @staticmethod
    def older_than_x_months(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is older than the specified amount of moths."""
        return OPS._special_single_value(entity, x, "OlderThanXMonths", group, ref_quotes=False)

    @staticmethod
    def older_than_x_weeks(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is older than the specified amount of weeks."""
        return OPS._special_single_value(entity, x, "OlderThanXWeeks", group, ref_quotes=False)

    @staticmethod
    def older_than_x_years(entity: str, x: int, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is older than the specified amount of years."""
        return OPS._special_single_value(entity, x, "OlderThanXYears", group, ref_quotes=False)

    # Special query functions - business id checks

    @staticmethod
    def equal_business_id(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is equal to the specified business ID."""
        return OPS._special_name_only(entity, "EqualBusinessId", group)

    @staticmethod
    def not_business_id(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is not equal to the specified business ID."""
        return OPS._special_name_only(entity, "NotBusinessId", group)

    # Special query functions - user id checks

    @staticmethod
    def equal_user_id(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is equal to the ID of the user."""
        return OPS._special_name_only(entity, "EqualUserId", group)

    @staticmethod
    def not_user_id(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is not equal to the ID of the user."""
        return OPS._special_name_only(entity, "NotUserId", group)

    # Special query functions - misc

    @staticmethod
    def equal_user_language(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' is equal to the language for the user."""
        return OPS._special_name_only(entity, "EqualUserLanguage", group)

    @staticmethod
    def equal_user_or_user_hierarchy(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' equals current user or their reporting hierarchy."""
        return OPS._special_name_only(entity, "EqualUserOrUserHierarchy", group)

    @staticmethod
    def equal_user_or_user_hierarchy_and_teams(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' equals current user or their reporting hierarchy and teams."""
        return OPS._special_name_only(entity, "EqualUserOrUserHierarchyAndTeams", group)

    @staticmethod
    def equal_user_or_user_teams(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' equals current user or user teams."""
        return OPS._special_name_only(entity, "EqualUserOrUserTeams", group)

    @staticmethod
    def equal_user_teams(entity: str, group: bool = False) -> str:
        """Evaluates whether the value of 'entity' equals current user teams."""
        return OPS._special_name_only(entity, "EqualUserTeams", group)


ftr = OPS()
"""Convenience functions for creating $filter parameters."""
