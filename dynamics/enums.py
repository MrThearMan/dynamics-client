from enum import IntEnum


__all__ = [
    "QuoteState",
    "OrderState",
    "TargetFieldType",
    "EntityFilter",
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
    """Describes the type of entity metadata to retrieve."""

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
