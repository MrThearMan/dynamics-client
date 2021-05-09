"""

Functions available in the web API.

Reference:
https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/functions

"""

from typing import Literal
from enum import IntEnum


__all__ = [
    "fnc",
]


target_field_type = Literal["all", "create", "update", "read"]
entity_filter_type = Literal["entity", "attributes", "privileges", "relationships", "all"]


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


class EntityFilters(IntEnum):
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


class OPS:
    """"""

    @staticmethod
    def expand_calendar(start: str, end: str):
        """Converts the calendar rules to an array of available time blocks for the specified period."""
        return f"ExpandCalendar(Start='{start}',End='{end}')"

    @staticmethod
    def format_address(line_1: str, city: str, state: str, postal_code: str, country: str):
        """Builds the full address according to country/regional format specific requirements."""
        return (
            f"FormatAddress(Line1='{line_1}',City='{city}',"
            f"StateOrProvince='{state}',PostalCode='{postal_code}',Country='{country}')"
        )

    @staticmethod
    def get_default_price_level():
        """Retrieves the default price level (price list) for the current user
        based on the user’s territory relationship with the price level."""
        return f"GetDefaultPriceLevel()"

    @staticmethod
    def get_valid_many_to_many():
        """Retrieves a list of all the entities that can participate in a Many-to-Many entity relationship."""
        return f"GetValidManyToMany()"

    @staticmethod
    def get_valid_referenced_entities(name: str):
        """Retrieves a list of entity logical names that are valid as
        the primary entity (one) from the specified entity in a one-to-many relationship."""
        return f"GetValidReferencedEntities(ReferencingEntityName='{name}')"

    @staticmethod
    def get_valid_referencing_entities(name: str):
        """Retrieves the set of entities that are valid as
        the related entity (many) to the specified entity in a one-to-many relationship."""
        return f"GetValidReferencingEntities(ReferencingEntityName='{name}')"

    @staticmethod
    def initialize_from(table: str, row_id: str, entity_name: str, field_type: target_field_type):
        """Initializes a new record from an existing record."""
        return (
            f"InitializeFrom(EntityMoniker=@tid,TargetEntityName='{entity_name}',"
            + f"TargetFieldType={TargetFieldType[field_type].value})"
            + f"?@tid={{'@odata.id':'{table}({row_id})'}}"
        )

    @staticmethod
    def retrieve_all_entities(filters: entity_filter_type, as_if_published: bool = False):
        """Retrieves metadata information about all the entities.

        :param filters: Filter to control how much data for each entity is retrieved.
        :param as_if_published: Whether to retrieve the metadata that has not been published.
        """
        return (
            f"RetrieveAllEntities(EntityFilters={EntityFilters[filters].values}"
            f"RetrieveAsIfPublished={'true' if as_if_published else 'false'})"
        )

    @staticmethod
    def retrieve_entity(row_id: str, name: str, filters: entity_filter_type, as_if_published: bool = False):
        """Retrieves entity metadata.

        :param row_id: Primary key of the entity.
        :param name: The logical name of the target entity.
        :param filters: Filter to control how much data for each entity is retrieved.
        :param as_if_published: Whether to retrieve the metadata that has not been published.
        """
        return (
            f"RetrieveEntity("
            f"EntityFilters={EntityFilters[filters].values},"
            f"LogicalName='{name}',"
            f"MetadataId={row_id},"
            f"RetrieveAsIfPublished={'true' if as_if_published else 'false'})"
        )

    @staticmethod
    def retrieve_duplicates(table: str, row_id: str, entity_name: str):
        """Detects and retrieves duplicates for a specified record."""
        return (
            f"RetrieveDuplicates(BusinessEntity=@tid,MatchingEntityName='{entity_name}',"
            + f"?@tid={{'@odata.id':'{table}({row_id})'}}"
        )


fnc = OPS()
