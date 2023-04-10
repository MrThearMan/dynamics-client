import re
import sys

import pytest

from dynamics.enums import FetchXMLOperator
from dynamics.fetchxml import FetchXMLBuilder


def test_fetch_xml__simple():
    fetch_xml = (
        FetchXMLBuilder(mapping="logical")
        .add_entity(name="account")
        .add_attribute(name="accountid")
        .add_attribute(name="name")
        .add_attribute(name="accountnumber")
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = (
        '<fetch mapping="logical">'
        '<entity name="account">'
        '<attribute name="accountid"/>'
        '<attribute name="name"/>'
        '<attribute name="accountnumber"/>'
        "</entity>"
        "</fetch>"
    )

    assert fetch_xml == expected


def test_fetch_xml__all_top_level_options():
    fetch_xml = (
        FetchXMLBuilder(
            mapping="logical",
            version="1.0",
            page=1,
            count=2,
            top=1,
            aggregate=True,
            distinct=True,
            paging_cookie="foo",
            utc_offset=123123,
            output_format="xml-auto",
            min_active_row_version=True,
            return_total_record_count=True,
            no_lock=True,
        )
        .order(attribute="name")
        .add_entity(name="account")
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = (
        '<fetch mapping="logical" version="1.0" page="1" count="2" top="1" '
        'aggregate="true" distinct="true" paging-cookie="foo" utc-offset="123123" '
        'output-format="xml-auto" min-active-row-version="true" '
        'returntotalrecordcount="true" no-lock="true"><entity name="account"/><order '
        'attribute="name"/></fetch>'
    )

    assert fetch_xml == expected


def test_fetch_xml__all_entity_options():
    fetch_xml = (
        FetchXMLBuilder()
        .add_entity(name="account", enable_prefiltering=True, prefilter_parameter_name="foo")
        .add_attribute(
            name="accountid",
            alias="pizza",
            aggregate="count",
            groupby=True,
            distinct=True,
            date_grouping="day",
            user_timezone=True,
            added_by="me",
            build="1.003017",
        )
        .order(attribute="name", alias="x", descending=True)
        .filter(type_="or", is_quick_find_fields=True, override_quick_find_record_limit_enabled=True)
        .add_linked_entity(
            name="systemuser",
            to="owninguser",
            from_="y",
            alias="foobar",
            link_type="outer",
            visible=True,
            intersect=True,
            enable_prefiltering=True,
            prefilter_parameter_name="xyz",
        )
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = (
        '<fetch><entity name="account" enableprefiltering="true" '
        'prefilterparametername="foo"><attribute name="accountid" alias="pizza" '
        'aggregate="count" groupby="true" distinct="true" dategrouping="day" '
        'usertimezone="true" addedby="me" build="1.003017"/><filter type="or" '
        'isquickfindfields="true" '
        'overridequickfindrecordlimitenabled="true"/><link-entity name="systemuser" '
        'to="owninguser" from="y" alias="foobar" link-type="outer" visible="true" '
        'intersect="true" enableprefiltering="true" '
        'prefilterparametername="xyz"/><order attribute="name" alias="x" '
        'descending="true"/></entity></fetch>'
    )

    assert fetch_xml == expected


def test_fetch_xml__all_linked_entity_options():
    fetch_xml = (
        FetchXMLBuilder()
        .add_entity(name="account")
        .add_linked_entity(
            name="systemuser",
            to="owninguser",
            from_="y",
            alias="foobar",
            link_type="outer",
            visible=True,
            intersect=True,
            enable_prefiltering=True,
            prefilter_parameter_name="xyz",
        )
        .add_attribute(
            name="accountid",
            alias="pizza",
            aggregate="count",
            groupby=True,
            distinct=True,
            date_grouping="day",
            user_timezone=True,
            added_by="me",
            build="1.003017",
        )
        .order(attribute="name", alias="x", descending=True)
        .filter(type_="or", is_quick_find_fields=True, override_quick_find_record_limit_enabled=True)
        .add_linked_entity(
            name="systemuser",
            to="owninguser",
            from_="y",
            alias="foobar",
            link_type="outer",
            visible=True,
            intersect=True,
            enable_prefiltering=True,
            prefilter_parameter_name="xyz",
        )
        .add_nested_linked_entity(
            name="systemuser-nested",
            to="owninguser-nested",
            from_="y",
            alias="foobar",
            link_type="outer",
            visible=True,
            intersect=True,
            enable_prefiltering=True,
            prefilter_parameter_name="xyz",
        )
        .add_linked_entity(
            name="systemuser-nested2",
            to="owninguser-nested2",
            from_="y",
            alias="foobar",
            link_type="outer",
            visible=True,
            intersect=True,
            enable_prefiltering=True,
            prefilter_parameter_name="xyz",
        )
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = (
        '<fetch><entity name="account"><link-entity name="systemuser" to="owninguser" '
        'from="y" alias="foobar" link-type="outer" visible="true" intersect="true" '
        'enableprefiltering="true" prefilterparametername="xyz"><attribute '
        'name="accountid" alias="pizza" aggregate="count" groupby="true" '
        'distinct="true" dategrouping="day" usertimezone="true" addedby="me" '
        'build="1.003017"/><filter type="or" isquickfindfields="true" '
        'overridequickfindrecordlimitenabled="true"/><order attribute="name" '
        'alias="x" descending="true"/></link-entity><link-entity name="systemuser" '
        'to="owninguser" from="y" alias="foobar" link-type="outer" visible="true" '
        'intersect="true" enableprefiltering="true" '
        'prefilterparametername="xyz"><link-entity name="systemuser-nested" '
        'to="owninguser-nested" from="y" alias="foobar" link-type="outer" '
        'visible="true" intersect="true" enableprefiltering="true" '
        'prefilterparametername="xyz"/><link-entity name="systemuser-nested2" '
        'to="owninguser-nested2" from="y" alias="foobar" link-type="outer" '
        'visible="true" intersect="true" enableprefiltering="true" '
        'prefilterparametername="xyz"/></link-entity></entity></fetch>'
    )

    assert fetch_xml == expected


def test_fetch_xml__all_filter_options():
    fetch_xml = (
        FetchXMLBuilder()
        .add_entity(name="account")
        .filter(type_="or", is_quick_find_fields=True, override_quick_find_record_limit_enabled=True)
        .add_condition(
            attribute="foo",
            operator="eq",
            value=1,
            values=["foo", "bar"],
            value_of="xxx",
            column="xyz",
            entity_name="account",
            aggregate="count",
            row_aggregate="countchildren",
            alias="python",
            uiname="what",
            uitype="is",
            uihidden=True,
        )
        .add_linked_entity(name="systemuser", to="owninguser")
        .filter(type_="or", is_quick_find_fields=True, override_quick_find_record_limit_enabled=True)
        .filter(type_="and", is_quick_find_fields=True, override_quick_find_record_limit_enabled=True)
        .nested_filter(type_="or", is_quick_find_fields=True, override_quick_find_record_limit_enabled=True)
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = (
        '<fetch><entity name="account"><filter type="or" isquickfindfields="true" '
        'overridequickfindrecordlimitenabled="true"><condition attribute="foo" '
        'operator="eq" value="1" values="[\'foo\', \'bar\']" valueof="xxx" '
        'column="xyz" entityname="account" aggregate="count" '
        'rowaggregate="countchildren" alias="python" uiname="what" uitype="is" '
        'uihidden="1"/></filter><link-entity name="systemuser" '
        'to="owninguser"><filter type="or" isquickfindfields="true" '
        'overridequickfindrecordlimitenabled="true"/><filter type="and" '
        'isquickfindfields="true" overridequickfindrecordlimitenabled="true"><filter '
        'type="or" isquickfindfields="true" '
        'overridequickfindrecordlimitenabled="true"/></filter></link-entity></entity></fetch>'
    )

    assert fetch_xml == expected


def test_fetch_xml__adding_linked_entities_after_filter():
    fetch_xml = (
        FetchXMLBuilder()
        .add_entity(name="account")
        .filter(type_="or", is_quick_find_fields=True, override_quick_find_record_limit_enabled=True)
        .add_condition(attribute="1", operator="ne")
        .add_linked_entity(name="x", to="y")
        .filter(type_="and", is_quick_find_fields=False, override_quick_find_record_limit_enabled=True)
        .add_condition(attribute="1", operator="eq")
        .nested_filter(type_="or", is_quick_find_fields=True, override_quick_find_record_limit_enabled=False)
        .add_condition(attribute="1", operator=FetchXMLOperator.LT)
        .add_linked_entity(name="foo", to="bar")
        .filter(type_="or", is_quick_find_fields=False, override_quick_find_record_limit_enabled=False)
        .add_condition(attribute="1", operator=FetchXMLOperator.GT)
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = (
        '<fetch><entity name="account"><filter type="or" isquickfindfields="true" '
        'overridequickfindrecordlimitenabled="true"><condition attribute="1" '
        'operator="ne"/></filter><link-entity name="x" to="y"><filter type="and" '
        'isquickfindfields="false" overridequickfindrecordlimitenabled="true"><filter '
        'type="or" isquickfindfields="true" '
        'overridequickfindrecordlimitenabled="false"><condition attribute="1" '
        'operator="lt"/></filter><condition attribute="1" '
        'operator="eq"/></filter></link-entity><link-entity name="foo" '
        'to="bar"><filter type="or" isquickfindfields="false" '
        'overridequickfindrecordlimitenabled="false"><condition attribute="1" '
        'operator="gt"/></filter></link-entity></entity></fetch>'
    )

    assert fetch_xml == expected


def test_fetch_xml__all_order_options():
    fetch_xml = (
        FetchXMLBuilder()
        .order(attribute="foo", alias="bar", descending=True)
        .add_entity(name="account")
        .order(attribute="foo", alias="bar", descending=False)
        .add_linked_entity(name="x", to="y")
        .order(attribute="foo", alias="bar", descending=True)
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = (
        '<fetch><entity name="account"><link-entity name="x" to="y"><order '
        'attribute="foo" alias="bar" descending="true"/></link-entity><order '
        'attribute="foo" alias="bar" descending="false"/></entity><order '
        'attribute="foo" alias="bar" descending="true"/></fetch>'
    )

    assert fetch_xml == expected


def test_fetch_xml__with_all_atributes():
    fetch_xml = (
        FetchXMLBuilder()
        .add_entity(name="foo")
        .with_all_attributes()
        .add_linked_entity(name="bar", to="baz")
        .with_all_attributes()
        .build()
    )

    # xml.etree.ElementTree.tostring doesn't preserve attribute order,
    # so we can't do the comparison below
    if sys.version_info < (3, 8):
        return

    expected = '<fetch><entity name="foo"><link-entity name="bar" to="baz"/></entity></fetch>'

    assert fetch_xml == expected


def test_fetch_xml__with_all_atributes_and_individual_attributes_mutually_exclusive():
    builder1 = FetchXMLBuilder().add_entity(name="foo").with_all_attributes()
    builder2 = FetchXMLBuilder().add_entity(name="foo").add_attribute(name="foo")

    with pytest.raises(ValueError, match="All attributes defined, cannot add individual attributes."):
        builder1.add_attribute(name="foo")

    with pytest.raises(ValueError, match="Individual attributes defined, cannot add all attributes."):
        builder2.with_all_attributes()

    builder3 = builder1.add_linked_entity(name="x", to="1").with_all_attributes()
    builder4 = builder1.add_linked_entity(name="x", to="1").add_attribute(name="foo")

    with pytest.raises(ValueError, match="All attributes defined, cannot add individual attributes."):
        builder3.add_attribute(name="foo")

    with pytest.raises(ValueError, match="Individual attributes defined, cannot add all attributes."):
        builder4.with_all_attributes()


def test_fetch_xml__too_many_linked_entities():
    builder = FetchXMLBuilder().add_entity(name="foo")

    for i in range(10):
        builder = builder.add_linked_entity(name=str(i), to=str(i))

    with pytest.raises(RuntimeError, match=re.escape("Too many linked tables (>10)")):
        builder.add_linked_entity(name="x", to="y")


def test_fetch_xml__too_many_linked_entities__nested():
    builder = FetchXMLBuilder().add_entity(name="foo").add_linked_entity(name="x", to="y")

    for i in range(9):
        builder = builder.add_nested_linked_entity(name=str(i), to=str(i))

    with pytest.raises(RuntimeError, match=re.escape("Too many linked tables (>10)")):
        builder.add_nested_linked_entity(name="x", to="y")


def test_fetch_xml__too_many_filter_conditions():
    builder = FetchXMLBuilder().add_entity(name="foo").filter()

    for i in range(500):
        builder = builder.add_condition(attribute=str(i), operator="eq")

    with pytest.raises(RuntimeError, match=re.escape("Too many conditions (>500)")):
        builder.add_condition(attribute="x", operator="eq")
