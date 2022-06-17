import re
from itertools import chain

import pytest

from dynamics.api_functions import Functions
from dynamics.enums import EntityFilter, TargetFieldType
from dynamics.test import MockClient


def test_api_functions__expand_calendar(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.expand_calendar(start="foo", end="bar")
    assert dynamics_client.action == "ExpandCalendar(Start='foo',End='bar')"


def test_api_functions__format_address(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.format_address(
        line_1="address", city="city", state="state", postal_code="postal_code", country="county"
    )
    assert dynamics_client.action == (
        "FormatAddress(Line1='address',City='city',"
        "StateOrProvince='state',PostalCode='postal_code',Country='county')"
    )


def test_api_functions__get_default_price_level(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.get_default_price_level()
    assert dynamics_client.action == "GetDefaultPriceLevel()"


def test_api_functions__get_valid_many_to_many(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.get_valid_many_to_many()
    assert dynamics_client.action == "GetValidManyToMany()"


def test_api_functions__get_valid_referenced_entities(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.get_valid_referenced_entities(name="name")
    assert dynamics_client.action == "GetValidReferencedEntities(ReferencingEntityName='name')"


def test_api_functions__get_valid_referencing_entities(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.get_valid_referencing_entities(name="name")
    assert dynamics_client.action == "GetValidReferencingEntities(ReferencingEntityName='name')"


@pytest.mark.parametrize("field_type", TargetFieldType)
def test_api_functions__initialize_from(dynamics_client, field_type: TargetFieldType):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.initialize_from(table="table", row_id="row_id", entity_name="name", field_type=field_type)
    assert dynamics_client.action == (
        f"InitializeFrom(EntityMoniker=@tid,TargetEntityName='name',TargetFieldType={field_type.value})"
        f"?@tid={{'@odata.id':'table(row_id)'}}"
    )


@pytest.mark.parametrize(
    "entity_filter,as_if_published",
    chain(zip(EntityFilter, [False] * len(EntityFilter)), zip(EntityFilter, [True] * len(EntityFilter))),
)
def test_api_functions__retrieve_all_entities(dynamics_client, entity_filter: EntityFilter, as_if_published: bool):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.retrieve_all_entities(entity_filter=entity_filter, as_if_published=as_if_published)
    assert dynamics_client.action == (
        f"RetrieveAllEntities(EntityFilters={entity_filter.value},"
        f"RetrieveAsIfPublished={'true' if as_if_published else 'false'})"
    )


@pytest.mark.parametrize(
    "entity_filter,as_if_published",
    chain(zip(EntityFilter, [False] * len(EntityFilter)), zip(EntityFilter, [True] * len(EntityFilter))),
)
def test_api_functions__retrieve_entity(dynamics_client, entity_filter: EntityFilter, as_if_published: bool):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.retrieve_entity(
        row_id="row_id", name="name", entity_filter=entity_filter, as_if_published=as_if_published
    )
    assert dynamics_client.action == (
        f"RetrieveEntity("
        f"EntityFilters={entity_filter.value},"
        f"LogicalName='name',"
        f"MetadataId=row_id,"
        f"RetrieveAsIfPublished={'true' if as_if_published else 'false'})"
    )


def test_api_functions__retrieve_duplicates(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.retrieve_duplicates(table="table", row_id="row_id", entity_name="entity_name")
    assert dynamics_client.action == (
        f"RetrieveDuplicates(BusinessEntity=@tid,MatchingEntityName='entity_name',"
        f"?@tid={{'@odata.id':'table(row_id)'}}"
    )


def test_api_functions__whoami(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}).with_status_codes(200)
    dynamics_client.functions.whoami()
    assert dynamics_client.action == "WhoAmI()"


def test_api_cations__called_on_class():
    with pytest.raises(RuntimeError, match=re.escape("Functions can only be used on DynamicsClient instances.")):
        MockClient.functions.whoami()
