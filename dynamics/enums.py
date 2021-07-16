"""Dynamics Standard Enumerations."""

from enum import IntEnum


__all__ = [
    "QuoteState",
    "OrderState",
    "TargetFieldType",
    "EntityFilter",
]


class QuoteState(IntEnum):
    Draft = 0
    Active = 1
    Won = 2
    Closed = 3


class OrderState(IntEnum):
    Active = 0
    Submitted = 1
    Canceled = 2
    Fulfilled = 3
    Invoiced = 4


class TargetFieldType(IntEnum):
    """Indicates the attribute type for the target of the InitializeFromRequest message."""

    all = 0
    """All possible attribute values."""
    create = 1
    """Attribute values that are valid for create."""
    update = 2
    """Attribute values that are valid for update."""
    read = 3
    """Attribute values that are valid for read."""


class EntityFilter(IntEnum):
    """Describes the type of entity metadata to retrieve."""

    entity = 1
    """Use this to retrieve only entity information."""
    attributes = 2
    """Use this to retrieve entity information plus attributes for the entity."""
    privileges = 4
    """Use this to retrieve entity information plus privileges for the entity."""
    relationships = 8
    """Use this to retrieve entity information plus entity relationships for the entity."""
    all = 16
    """Use this to retrieve all data for an entity."""


# TODO: More enumerations
