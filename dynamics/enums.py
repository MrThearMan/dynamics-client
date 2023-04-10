from enum import Enum, IntEnum

__all__ = [
    "QuoteState",
    "OrderState",
    "TargetFieldType",
    "EntityFilter",
    "FetchXMLOperator",
]


class QuoteState(IntEnum):
    DRAFT = 0
    ACTIVE = 1
    WON = 2
    CLOSED = 3


class OrderState(IntEnum):
    ACTIVE = 0
    SUBMITTED = 1
    CANCELED = 2
    FULFILLED = 3
    INVOICED = 4


class TargetFieldType(IntEnum):
    """Indicates the attribute type for the target of the InitializeFromRequest message."""

    ALL = 0
    """All possible attribute values."""
    CREATE = 1
    """Attribute values that are valid for create."""
    UPDATE = 2
    """Attribute values that are valid for update."""
    READ = 3
    """Attribute values that are valid for read."""


class EntityFilter(IntEnum):
    """Describes the entity metadata to retrieve."""

    ENTITY = 1
    """Use this to retrieve only entity information."""
    ATTRIBUTES = 2
    """Use this to retrieve entity information plus attributes for the entity."""
    PRIVILEGES = 4
    """Use this to retrieve entity information plus privileges for the entity."""
    RELATIONSHIPS = 8
    """Use this to retrieve entity information plus entity relationships for the entity."""
    ALL = 16
    """Use this to retrieve all data for an entity."""


# TODO: More enumerations


class FetchXMLOperator(str, Enum):
    EQ = "eq"
    NEQ = "neq"
    NE = "ne"
    GT = "gt"
    GE = "ge"
    LE = "le"
    LT = "lt"
    LIKE = "like"
    NOT_LIKE = "not-like"
    IN_ = "in"
    NOT_IN = "not-in"
    BETWEEN = "between"
    NOT_BETWEEN = "not-between"
    NULL = "null"
    NOT_NULL = "not-null"
    YESTERDAY = "yesterday"
    TODAY = "today"
    TOMORROW = "tomorrow"
    LAST_SEVEN_DAYS = "last-seven-days"
    NEXT_SEVEN_DAYS = "next-seven-days"
    LAST_WEEK = "last-week"
    THIS_WEEK = "this-week"
    NEXT_WEEK = "next-week"
    LAST_MONTH = "last-month"
    THIS_MONTH = "this-month"
    NEXT_MONTH = "next-month"
    ON = "on"
    ON_OR_BEFORE = "on-or-before"
    ON_OR_AFTER = "on-or-after"
    LAST_YEAR = "last-year"
    THIS_YEAR = "this-year"
    NEXT_YEAR = "next-year"
    LAST_X_HOURS = "last-x-hours"
    NEXT_X_HOURS = "next-x-hours"
    LAST_X_DAYS = "last-x-days"
    NEXT_X_DAYS = "next-x-days"
    LAST_X_WEEKS = "last-x-weeks"
    NEXT_X_WEEKS = "next-x-weeks"
    LAST_X_MONTHS = "last-x-months"
    NEXT_X_MONTHS = "next-x-months"
    OLDERTHAN_X_MONTHS = "olderthan-x-months"
    OLDERTHAN_X_YEARS = "olderthan-x-years"
    OLDERTHAN_X_WEEKS = "olderthan-x-weeks"
    OLDERTHAN_X_DAYS = "olderthan-x-days"
    OLDERTHAN_X_HOURS = "olderthan-x-hours"
    OLDERTHAN_X_MINUTES = "olderthan-x-minutes"
    LAST_X_YEARS = "last-x-years"
    NEXT_X_YEARS = "next-x-years"
    EQ_USERID = "eq-userid"
    NE_USERID = "ne-userid"
    EQ_USERTEAMS = "eq-userteams"
    EQ_USERORUSERTEAMS = "eq-useroruserteams"
    EQ_USERORUSERHIERARCHY = "eq-useroruserhierarchy"
    EQ_USERORUSERHIERARCHYANDTEAMS = "eq-useroruserhierarchyandteams"
    EQ_BUSINESSID = "eq-businessid"
    NE_BUSINESSID = "ne-businessid"
    EQ_USERLANGUAGE = "eq-userlanguage"
    THIS_FISCAL_YEAR = "this-fiscal-year"
    THIS_FISCAL_PERIOD = "this-fiscal-period"
    NEXT_FISCAL_YEAR = "next-fiscal-year"
    NEXT_FISCAL_PERIOD = "next-fiscal-period"
    LAST_FISCAL_YEAR = "last-fiscal-year"
    LAST_FISCAL_PERIOD = "last-fiscal-period"
    LAST_X_FISCAL_YEARS = "last-x-fiscal-years"
    LAST_X_FISCAL_PERIODS = "last-x-fiscal-periods"
    NEXT_X_FISCAL_YEARS = "next-x-fiscal-years"
    NEXT_X_FISCAL_PERIODS = "next-x-fiscal-periods"
    IN_FISCAL_YEAR = "in-fiscal-year"
    IN_FISCAL_PERIOD = "in-fiscal-period"
    IN_FISCAL_YEAR_AND_YEAR = "in-fiscal-period-and-year"
    IN_OR_BEFORE_FISCAL_PERIOD_AND_YEAR = "in-or-before-fiscal-period-and-year"
    IN_OR_AFTER_FISCAL_PERIOD_AND_YEAR = "in-or-after-fiscal-period-and-year"
    BEGINS_WITH = "begins-with"
    NOT_BEGINS_WITH = "not-begin-with"
    ENDS_WITH = "ends-with"
    NOT_ENDS_WITH = "not-end-with"
    UNDER = "under"
    EQ_OR_UNDER = "eq-or-under"
    NOT_UNDER = "not-under"
    ABOVE = "above"
    EQ_OR_ABOVE = "eq-or-above"
    CONTAIN_VALUES = "contain-values"
    NOT_CONTAIN_VALUES = "not-contain-values"
