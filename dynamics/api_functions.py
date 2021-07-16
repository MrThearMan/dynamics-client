"""
Functions available in the web API. Reference:
https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/functions
"""

from typing import List, Dict, Any, TYPE_CHECKING
from .enums import TargetFieldType, EntityFilter

if TYPE_CHECKING:
    from .client import DynamicsClient


__all__ = ["Functions"]


class Functions:
    """Predefined Dynamics API functions."""

    def __init__(self, client: "DynamicsClient"):
        self.client = client

    def expand_calendar(self, start: str, end: str, **kwargs) -> List[Dict[str, Any]]:
        """Converts the calendar rules to an array of available time blocks for the specified period."""

        self.client.reset_query()
        self.client.action = f"ExpandCalendar(Start='{start}',End='{end}')"

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def format_address(
        self, line_1: str, city: str, state: str, postal_code: str, country: str, **kwargs
    ) -> List[Dict[str, Any]]:
        """Builds the full address according to country/regional format specific requirements."""

        self.client.reset_query()
        self.client.action = (
            f"FormatAddress(Line1='{line_1}',City='{city}',"
            f"StateOrProvince='{state}',PostalCode='{postal_code}',Country='{country}')"
        )

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def get_default_price_level(self, **kwargs) -> List[Dict[str, Any]]:
        """Retrieves the default price level (price list) for the current user
        based on the user’s territory relationship with the price level.
        """

        self.client.reset_query()
        self.client.action = f"GetDefaultPriceLevel()"

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def get_valid_many_to_many(self, **kwargs) -> List[Dict[str, Any]]:
        """Retrieves a list of all the entities that can participate in a Many-to-Many entity relationship."""


        self.client.reset_query()
        self.client.action = f"GetValidManyToMany()"

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def get_valid_referenced_entities(self, name: str, **kwargs) -> List[Dict[str, Any]]:
        """Retrieves a list of entity logical names that are valid as
        the primary entity (one) from the specified entity in a one-to-many relationship."""


        self.client.reset_query()
        self.client.action = f"GetValidReferencedEntities(ReferencingEntityName='{name}')"

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def get_valid_referencing_entities(self, name: str, **kwargs) -> List[Dict[str, Any]]:
        """Retrieves the set of entities that are valid as
        the related entity (many) to the specified entity in a one-to-many relationship.
        """

        self.client.reset_query()
        self.client.action = f"GetValidReferencingEntities(ReferencingEntityName='{name}')"

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def initialize_from(
        self, table: str, row_id: str, entity_name: str, field_type: TargetFieldType, **kwargs
    ) -> List[Dict[str, Any]]:
        """Initializes a new record from an existing record."""

        self.client.reset_query()
        self.client.action = (
            f"InitializeFrom(EntityMoniker=@tid,TargetEntityName='{entity_name}',"
            + f"TargetFieldType={field_type.value})"
            + f"?@tid={{'@odata.id':'{table}({row_id})'}}"
        )

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def retrieve_all_entities(
        self, entity_filter: EntityFilter, as_if_published: bool = False, **kwargs
    ) -> List[Dict[str, Any]]:
        """Retrieves metadata information about all the entities.

        :param entity_filter: Filter to control how much data for each entity is retrieved.
        :param as_if_published: Whether to retrieve the metadata that has not been published.
        """

        self.client.reset_query()
        self.client.action = (
            f"RetrieveAllEntities(EntityFilters={entity_filter.values}"
            f"RetrieveAsIfPublished={'true' if as_if_published else 'false'})"
        )

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def retrieve_entity(
        self, row_id: str, name: str, entity_filter: EntityFilter, as_if_published: bool = False, **kwargs
    ) -> List[Dict[str, Any]]:
        """Retrieves entity metadata.

        :param row_id: Primary key of the entity.
        :param name: The logical name of the target entity.
        :param entity_filter: Filter to control how much data for each entity is retrieved.
        :param as_if_published: Whether to retrieve the metadata that has not been published.
        """

        self.client.reset_query()
        self.client.action = (
            f"RetrieveEntity("
            f"EntityFilters={entity_filter.values},"
            f"LogicalName='{name}',"
            f"MetadataId={row_id},"
            f"RetrieveAsIfPublished={'true' if as_if_published else 'false'})"
        )

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def retrieve_duplicates(self, table: str, row_id: str, entity_name: str, **kwargs) -> List[Dict[str, Any]]:
        """Detects and retrieves duplicates for a specified record."""

        self.client.reset_query()
        self.client.action = (
            f"RetrieveDuplicates(BusinessEntity=@tid,MatchingEntityName='{entity_name}',"
            + f"?@tid={{'@odata.id':'{table}({row_id})'}}"
        )

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )

    def whoami(self, **kwargs) -> List[Dict[str, Any]]:
        """Retrieves the system user ID for the currently logged on user
        or the user under whose context the code is running."""

        self.client.reset_query()
        self.client.action = "WhoAmI()"

        return self.client.GET(
            simplify_errors=kwargs.pop("simplify_errors", False),
            raise_separately=kwargs.pop("raise_separately", []),
        )
