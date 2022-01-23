# pylint: disable=W0212
from xml.etree.ElementTree import Element, SubElement, tostring

from .enums import FetchXMLOperator
from .typing import (
    Any,
    FetchXMLAggregateType,
    FetchXMLAttributeType,
    FetchXMLBuildType,
    FetchXMLCondition,
    FetchXMLDateGroupingType,
    FetchXMLEntityType,
    FetchXMLFetchMappingType,
    FetchXMLFilterOperatorType,
    FetchXMLFilterType,
    FetchXMLLinkedEntity,
    FetchXMLOrderType,
    FetchXMLOutputFormat,
    FetchXMLType,
    List,
    Literal,
    LiteralBool,
    Optional,
    Union,
)


__all__ = [
    "FetchXMLBuilder",
]


def _serialize_bool(value: bool) -> LiteralBool:
    return "true" if value else "false"  # type: ignore


class FetchXMLBuilder:
    def __init__(  # pylint: disable=R0912
        self,
        *,
        mapping: Optional[FetchXMLFetchMappingType] = None,
        version: Optional[str] = None,
        page: Optional[int] = None,
        count: Optional[int] = None,
        top: Optional[int] = None,
        aggregate: Optional[bool] = None,
        distinct: Optional[bool] = None,
        paging_cookie: Optional[str] = None,
        utc_offset: Optional[int] = None,
        output_format: Optional[FetchXMLOutputFormat] = None,
        min_active_row_version: Optional[bool] = None,
        return_total_record_count: Optional[bool] = None,
        no_lock: Optional[bool] = None,
    ):
        """A Builder class for building FetchXML queries.

        XML Shema:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/fetchxml-schema

        :param mapping: Should be "logical" for 3rd parties.
        :param version: Version information.
        :param page: When paging a request, this is the page number.
        :param count: Then paging a request, this is the number of items per page.
        :param top: Limit the number of items in the query.
        :param aggregate: Use grouping and aggregation in the query.
        :param distinct: If True, remove duplicate values from the resultset.
        :param paging_cookie: Paging cookie used in paging.
        :param utc_offset: UTC offset.
        :param output_format: Output format
        :param min_active_row_version: Minimum active row version?
        :param return_total_record_count: Return total record count?
        :param no_lock: No lock?
        """

        self._attrs = FetchXMLType()

        if mapping is not None:
            self._attrs["mapping"] = mapping
        if version is not None:
            self._attrs["version"] = version
        if page is not None:
            self._attrs["page"] = str(page)
        if count is not None:
            self._attrs["count"] = str(count)
        if top is not None:
            self._attrs["top"] = str(top)
        if aggregate is not None:
            self._attrs["aggregate"] = _serialize_bool(aggregate)
        if distinct is not None:
            self._attrs["distinct"] = _serialize_bool(distinct)
        if paging_cookie is not None:
            self._attrs["paging-cookie"] = paging_cookie
        if utc_offset is not None:
            self._attrs["utc-offset"] = str(utc_offset)
        if output_format is not None:
            self._attrs["output-format"] = output_format
        if min_active_row_version is not None:
            self._attrs["min-active-row-version"] = _serialize_bool(min_active_row_version)
        if return_total_record_count is not None:
            self._attrs["returntotalrecordcount"] = _serialize_bool(return_total_record_count)
        if no_lock is not None:
            self._attrs["no-lock"] = "true" if no_lock else "false"

        self.__linked_table_count = 0

        self._entity: Optional[_EntityBuilder] = None
        self._order: Optional[FetchXMLOrderType] = None

    @property
    def _linked_table_count(self) -> int:
        return self.__linked_table_count

    @_linked_table_count.setter
    def _linked_table_count(self, value: int) -> None:
        self.__linked_table_count = value

    def add_entity(
        self,
        *,
        name: str,
        enable_prefiltering: Optional[bool] = None,
        prefilter_parameter_name: Optional[str] = None,
    ) -> "_EntityBuilder":
        """What entity the query concerns. Only one entity per query is allowed.

        :param name: Name of the entity table.
        :param enable_prefiltering: Enable pre-filtering.
        :param prefilter_parameter_name: Pre-filtering parameter name.
        :return: A new instance of EntityBuilder
        """

        self._entity = _EntityBuilder(
            self,
            name=name,
            enable_prefiltering=enable_prefiltering,
            prefilter_parameter_name=prefilter_parameter_name,
        )
        return self._entity

    def order(
        self,
        *,
        attribute: str,
        alias: Optional[str] = None,
        descending: Optional[bool] = None,
    ) -> "FetchXMLBuilder":
        """Apply ordering for the view. This is for the Reports view only.

        :param attribute: Attribute to order by.
        :param alias: Attribute alias.
        :param descending: Decending order?
        :return: The current instance of the FetchXMLBuilder.
        """

        self._order = FetchXMLOrderType(attribute=attribute)
        if alias is not None:
            self._order["alias"] = alias
        if descending is not None:
            self._order["descending"] = _serialize_bool(descending)
        return self

    def build(self) -> str:
        """Build the FetchXML query string."""

        fetch = Element("fetch", self._attrs)

        if self._entity is not None:
            entity = SubElement(fetch, "entity", self._entity._attrs)

            for attribute in self._entity._attributes:
                SubElement(entity, "attribute", attribute)

            self._build_filters(self._entity, entity)
            self._build_linked_entities(self._entity, entity)

            if self._entity._order is not None:
                SubElement(entity, "order", self._entity._order)

        if self._order is not None:
            SubElement(fetch, "order", self._order)

        # Save chars by removing spaces before closing slash
        return tostring(element=fetch, encoding="unicode").replace(" />", "/>")

    def _build_filters(
        self,
        parent_builder: Union["_EntityBuilder", "_LinkedEntityBuilder", "_FilterBuilder"],
        parent_element: Element,
    ) -> None:
        for ftr in parent_builder._filters:
            filter_element = SubElement(parent_element, "filter", ftr._attrs)

            self._build_filters(ftr, filter_element)

            for condition in ftr._conditions:
                SubElement(filter_element, "condition", condition)

    def _build_linked_entities(
        self,
        parent_builder: Union["_EntityBuilder", "_LinkedEntityBuilder"],
        parent_element: Element,
    ) -> None:
        for entity in parent_builder._linked_entities:
            linked_entity_element = SubElement(parent_element, "link-entity", entity._attrs)
            for attribute in entity._attributes:
                SubElement(linked_entity_element, "attribute", attribute)

            self._build_filters(entity, linked_entity_element)
            self._build_linked_entities(entity, linked_entity_element)

            if entity._order is not None:
                SubElement(linked_entity_element, "order", entity._order)


class _EntityBuilder:
    def __init__(
        self,
        parent_builder: "FetchXMLBuilder",
        *,
        name: str,
        enable_prefiltering: Optional[bool] = None,
        prefilter_parameter_name: Optional[str] = None,
    ):
        """Sub-builder for the entity level of the FetchXML query.

        :param parent_builder: The builder that constructed this builder.
        :param name: Name of the entity that this builder acts on.
        :param enable_prefiltering: Enable pre-filtering?
        :param prefilter_parameter_name: Pre-filtering parameter name?
        """

        self._parent_builder = parent_builder
        self._attrs = FetchXMLEntityType(name=name)

        if enable_prefiltering is not None:
            self._attrs["enableprefiltering"] = _serialize_bool(enable_prefiltering)
        if prefilter_parameter_name is not None:
            self._attrs["prefilterparametername"] = prefilter_parameter_name

        self._order: Optional[FetchXMLOrderType] = None
        self._all_attributes = False

        self._attributes: List[FetchXMLAttributeType] = []
        self._filters: List[_FilterBuilder] = []

        self._linked_entities: List[_LinkedEntityBuilder] = []

    @property
    def _linked_table_count(self) -> int:
        return self._parent_builder._linked_table_count

    @_linked_table_count.setter
    def _linked_table_count(self, value: int) -> None:
        self._parent_builder._linked_table_count = value

    def with_all_attributes(self) -> "_EntityBuilder":
        """Include all attributes from the main entity to the query.
        Mutually exclusive with adding individual attributes.

        :return: The current intance of the EntityBuilder.
        """

        if self._attributes:
            raise ValueError("Individual attributes defined, cannot add all attributes.")
        self._all_attributes = True
        return self

    def add_attribute(
        self,
        *,
        name: str,
        alias: str = None,
        aggregate: FetchXMLAggregateType = None,
        groupby: Optional[bool] = None,
        distinct: Optional[bool] = None,
        date_grouping: Optional[FetchXMLDateGroupingType] = None,
        user_timezone: Optional[bool] = None,
        added_by: str = None,
        build: FetchXMLBuildType = None,
    ) -> "_EntityBuilder":
        """Add an attribute to the query for the main entity.
        Mutually exclusive with adding all attributes.

        :param name: Name of the attribute to add.
        :param alias: Name to alias the attribute under.
        :param aggregate: Aggregate function to apply to the attrubte.
        :param groupby: Group by this attribute.
        :param distinct: If True, remove duplicate values from the resultset.
        :param date_grouping: How to group dates?
        :param user_timezone: Use user's timezone?
        :param added_by: Added by.
        :param build: Build number.
        :return: The current intance of the EntityBuilder.
        """

        if self._all_attributes:
            raise ValueError("All attributes defined, cannot add individual attributes.")

        attribute = FetchXMLAttributeType(name=name)

        if alias is not None:
            attribute["alias"] = alias
        if aggregate is not None:
            attribute["aggregate"] = aggregate
        if groupby is not None:
            attribute["groupby"] = _serialize_bool(groupby)
        if distinct is not None:
            attribute["distinct"] = _serialize_bool(distinct)
        if date_grouping is not None:
            attribute["dategrouping"] = date_grouping
        if user_timezone is not None:
            attribute["usertimezone"] = _serialize_bool(user_timezone)
        if added_by is not None:
            attribute["addedby"] = added_by
        if build is not None:
            attribute["build"] = build

        self._attributes.append(attribute)
        return self

    def add_linked_entity(
        self,
        *,
        name: str,
        to: str,  # pylint: disable=C0103
        from_: Optional[str] = None,
        alias: Optional[str] = None,
        link_type: Optional[str] = None,
        visible: Optional[bool] = None,
        intersect: Optional[bool] = None,
        enable_prefiltering: Optional[bool] = None,
        prefilter_parameter_name: Optional[str] = None,
    ) -> "_LinkedEntityBuilder":
        """Add a linked entity from the main entity to the query.
        Note that the maximum number of linked entities is 10.

        :param name: Name of the table to link to.
        :param to: Name of the navigation property to link the table with.
        :param from_: Name of the attribute in the linked table to link the table from.
        :param alias: Name to alias the linked entity under.
        :param link_type: How the link should be made, e.g., "outer", "inner", etc.
        :param visible: Visible?
        :param intersect: Intersect?
        :param enable_prefiltering: Enable pre-filtering?
        :param prefilter_parameter_name: Pre-filtering parameter name.
        :return: A new instance of LinkedEntityBuilder.
        """

        linked_entity_builder = _LinkedEntityBuilder(
            self,
            name=name,
            to=to,
            from_=from_,
            alias=alias,
            link_type=link_type,
            visible=visible,
            intersect=intersect,
            enable_prefiltering=enable_prefiltering,
            prefilter_parameter_name=prefilter_parameter_name,
        )
        self._linked_entities.append(linked_entity_builder)
        return linked_entity_builder

    def order(
        self,
        *,
        attribute: str,
        alias: str = None,
        descending: Optional[bool] = None,
    ) -> "_EntityBuilder":
        """Apply ordering for the main entity's attributes.

        :param attribute: Attribute to order by.
        :param alias: Attribute alias.
        :param descending: Decending order?
        :return: The current instance of the EntityBuilder.
        """

        self._order = FetchXMLOrderType(attribute=attribute)
        if alias is not None:
            self._order["alias"] = alias
        if descending is not None:
            self._order["descending"] = _serialize_bool(descending)
        return self

    def filter(
        self,
        *,
        type_: FetchXMLFilterOperatorType = "and",
        is_quick_find_fields: Optional[bool] = None,
        override_quick_find_record_limit_enabled: Optional[bool] = None,
    ) -> "_FilterBuilder":
        """Apply filtering to the main entity's attributes.

        :param type_: Logical operator used when multiple conditions are present.
        :param is_quick_find_fields: If True, the filter is a quick find filter.
        :param override_quick_find_record_limit_enabled: If True, override the 10_000 record quick order limit.
        :return: A new instance of FilterBuilder.
        """

        filter_builder = _FilterBuilder(
            self,
            type_=type_,
            is_quick_find_fields=is_quick_find_fields,
            override_quick_find_record_limit_enabled=override_quick_find_record_limit_enabled,
        )
        self._filters.append(filter_builder)
        return filter_builder

    def build(self) -> str:
        """Build the FetchXML query string."""
        return self._parent_builder.build()


class _LinkedEntityBuilder:  # pylint: disable=R0902
    def __init__(
        self,
        parent_builder: Union["_EntityBuilder", "_LinkedEntityBuilder"],
        *,
        name: str,
        to: str,  # pylint: disable=C0103
        from_: Optional[str] = None,
        alias: Optional[str] = None,
        link_type: Optional[str] = None,
        visible: Optional[bool] = None,
        intersect: Optional[bool] = None,
        enable_prefiltering: Optional[bool] = None,
        prefilter_parameter_name: Optional[str] = None,
    ):
        """Sub-builder for the linked entity level of the FetchXML query.

        :param parent_builder: The builder that constructed this builder.
        :param name: Name of this linked entity's table.
        :param to: Name of the navigation property this linked entity was linked with.
        :param from_: Name of the attribute this linked entity was linked from.
        :param alias: Name to alias the linked entity was given by the parent entity.
        :param link_type: How the entity link was made, e.g., "outer", "inner", etc.
        :param visible: Visible?
        :param intersect: Intersect?
        :param enable_prefiltering: Enable pre-filtering?
        :param prefilter_parameter_name: Pre-filtering parameter name.
        """

        # needs to be set before incrementing '_linked_table_count'
        self._parent_builder = parent_builder

        self._linked_table_count += 1
        if self._linked_table_count > 10:
            raise RuntimeError("Too many linked tables (>10)")

        self._attrs = FetchXMLLinkedEntity(name=name, to=to)

        if from_ is not None:
            self._attrs["from"] = from_
        if alias is not None:
            self._attrs["alias"] = alias
        if link_type is not None:
            self._attrs["link-type"] = link_type
        if visible is not None:
            self._attrs["visible"] = _serialize_bool(visible)
        if intersect is not None:
            self._attrs["intersect"] = _serialize_bool(intersect)
        if enable_prefiltering is not None:
            self._attrs["enableprefiltering"] = _serialize_bool(enable_prefiltering)
        if prefilter_parameter_name is not None:
            self._attrs["prefilterparametername"] = prefilter_parameter_name

        self._order: Optional[FetchXMLOrderType] = None
        self._all_attributes = False

        self._attributes: List[FetchXMLAttributeType] = []
        self._filters: List[_FilterBuilder] = []

        self._linked_entities: List[_LinkedEntityBuilder] = []

    @property
    def _linked_table_count(self) -> int:
        return self._parent_builder._linked_table_count

    @_linked_table_count.setter
    def _linked_table_count(self, value: int) -> None:
        self._parent_builder._linked_table_count = value

    def with_all_attributes(self) -> "_LinkedEntityBuilder":
        """Include all attributes from this linked entity to the query.
        Mutually exclusive with adding individual attributes.

        :return: The current intance of the EntityBuilder.
        """

        if self._attributes:
            raise ValueError("Individual attributes defined, cannot add all attributes.")
        self._all_attributes = True
        return self

    def add_attribute(
        self,
        *,
        name: str,
        alias: Optional[str] = None,
        aggregate: Optional[FetchXMLAggregateType] = None,
        groupby: Optional[bool] = None,
        distinct: Optional[bool] = None,
        date_grouping: Optional[FetchXMLDateGroupingType] = None,
        user_timezone: Optional[bool] = None,
        added_by: Optional[str] = None,
        build: Optional[FetchXMLBuildType] = None,
    ) -> "_LinkedEntityBuilder":
        """Add an attribute to the query for this linked entity.
        Mutually exclusive with adding all attributes.

        :param name: Name of the attribute to add.
        :param alias: Name to alias the attribute under.
        :param aggregate: Aggregate function to apply to the attrubte.
        :param groupby: Group by this attribute.
        :param distinct: If True, remove duplicate values from the resultset.
        :param date_grouping: How to group dates?
        :param user_timezone: Use user's timezone?
        :param added_by: Added by.
        :param build: Build number.
        :return: The current intance of the LinkedEntityBuilder.
        """

        if self._all_attributes:
            raise ValueError("All attributes defined, cannot add individual attributes.")

        attribute = FetchXMLAttributeType(name=name)

        if alias is not None:
            attribute["alias"] = alias
        if aggregate is not None:
            attribute["aggregate"] = aggregate
        if groupby is not None:
            attribute["groupby"] = _serialize_bool(groupby)
        if distinct is not None:
            attribute["distinct"] = _serialize_bool(distinct)
        if date_grouping is not None:
            attribute["dategrouping"] = date_grouping
        if user_timezone is not None:
            attribute["usertimezone"] = _serialize_bool(user_timezone)
        if added_by is not None:
            attribute["addedby"] = added_by
        if build is not None:
            attribute["build"] = build

        self._attributes.append(attribute)
        return self

    def add_nested_linked_entity(
        self,
        *,
        name: str,
        to: str,  # pylint: disable=C0103
        from_: Optional[str] = None,
        alias: Optional[str] = None,
        link_type: Optional[str] = None,
        visible: Optional[bool] = None,
        intersect: Optional[bool] = None,
        enable_prefiltering: Optional[bool] = None,
        prefilter_parameter_name: Optional[str] = None,
    ) -> "_LinkedEntityBuilder":
        """Add a nested linked entity to this linked entity.
        Note that the maximum number of linked entities is 10.

        :param name: Name of the table to link to.
        :param to: Name of the navigation property to link the table with.
        :param from_: Name of the attribute in the linked table to link the table from.
        :param alias: Name to alias the linked entity under.
        :param link_type: How the link should be made, e.g., "outer", "inner", etc.
        :param visible: Visible?
        :param intersect: Intersect?
        :param enable_prefiltering: Enable pre-filtering?
        :param prefilter_parameter_name: Pre-filtering parameter name.
        :return: A new instance of LinkedEntityBuilder.
        """

        nested_linked_entity_builder = _LinkedEntityBuilder(
            self,
            name=name,
            to=to,
            from_=from_,
            alias=alias,
            link_type=link_type,
            visible=visible,
            intersect=intersect,
            enable_prefiltering=enable_prefiltering,
            prefilter_parameter_name=prefilter_parameter_name,
        )
        self._linked_entities.append(nested_linked_entity_builder)
        return nested_linked_entity_builder

    def add_linked_entity(
        self,
        *,
        name: str,
        to: str,  # pylint: disable=C0103
        from_: Optional[str] = None,
        alias: Optional[str] = None,
        link_type: Optional[str] = None,
        visible: Optional[bool] = None,
        intersect: Optional[bool] = None,
        enable_prefiltering: Optional[bool] = None,
        prefilter_parameter_name: Optional[str] = None,
    ) -> "_LinkedEntityBuilder":
        """Add a linked entity from the parent entity of this linked entity.
        Note that the maximum number of linked entities is 10.

        :param name: Name of the table to link to.
        :param to: Name of the navigation property to link the table with.
        :param from_: Name of the attribute in the linked table to link the table from.
        :param alias: Name to alias the linked entity under.
        :param link_type: How the link should be made, e.g., "outer", "inner", etc.
        :param visible: Visible?
        :param intersect: Intersect?
        :param enable_prefiltering: Enable pre-filtering?
        :param prefilter_parameter_name: Pre-filtering parameter name.
        :return: A new instance of LinkedEntityBuilder.
        """

        if isinstance(self._parent_builder, _EntityBuilder):
            return self._parent_builder.add_linked_entity(
                name=name,
                to=to,
                from_=from_,
                alias=alias,
                link_type=link_type,
                visible=visible,
                intersect=intersect,
                enable_prefiltering=enable_prefiltering,
                prefilter_parameter_name=prefilter_parameter_name,
            )
        return self._parent_builder.add_nested_linked_entity(
            name=name,
            to=to,
            from_=from_,
            alias=alias,
            link_type=link_type,
            visible=visible,
            intersect=intersect,
            enable_prefiltering=enable_prefiltering,
            prefilter_parameter_name=prefilter_parameter_name,
        )

    def order(
        self,
        *,
        attribute: str,
        alias: Optional[str] = None,
        descending: Optional[bool] = None,
    ) -> "_LinkedEntityBuilder":
        """Apply ordering for the linked entity's attributes.

        :param attribute: Attribute to order by.
        :param alias: Attribute alias.
        :param descending: Decending order?
        :return: The current instance of the LinkedEntityBuilder.
        """

        self._order = FetchXMLOrderType(attribute=attribute)
        if alias is not None:
            self._order["alias"] = alias
        if descending is not None:
            self._order["descending"] = _serialize_bool(descending)
        return self

    def filter(
        self,
        type_: FetchXMLFilterOperatorType = "and",
        is_quick_find_fields: Optional[bool] = None,
        override_quick_find_record_limit_enabled: Optional[bool] = None,
    ) -> "_FilterBuilder":
        """Apply filtering to the linked entity's attributes.

        :param type_: Logical operator used when multiple conditions are present.
        :param is_quick_find_fields: If True, the filter is a quick find filter.
        :param override_quick_find_record_limit_enabled: If True, override the 10_000 record quick order limit.
        :return: A new instance of FilterBuilder.
        """

        filter_builder = _FilterBuilder(
            self,
            type_=type_,
            is_quick_find_fields=is_quick_find_fields,
            override_quick_find_record_limit_enabled=override_quick_find_record_limit_enabled,
        )
        self._filters.append(filter_builder)
        return filter_builder

    def build(self) -> str:
        """Build the FetchXML query string."""
        return self._parent_builder.build()


class _FilterBuilder:
    def __init__(
        self,
        parent_builder: Union["_EntityBuilder", "_LinkedEntityBuilder", "_FilterBuilder"],
        *,
        type_: FetchXMLFilterOperatorType = "and",
        is_quick_find_fields: Optional[bool] = None,
        override_quick_find_record_limit_enabled: Optional[bool] = None,
    ):
        """Sub-builder for the filtering level of the FetchXML query.

        :param parent_builder: The builder that constructed this builder.
        :param type_: Logical operator used when multiple conditions are present.
        :param is_quick_find_fields: If True, this filter is a quick find filter.
        :param override_quick_find_record_limit_enabled: If True, override the 10_000 record quick order limit.
        """

        self._parent_builder = parent_builder
        self._attrs = FetchXMLFilterType(type=type_)

        if is_quick_find_fields is not None:
            self._attrs["isquickfindfields"] = _serialize_bool(is_quick_find_fields)
        if override_quick_find_record_limit_enabled is not None:
            self._attrs["overridequickfindrecordlimitenabled"] = _serialize_bool(
                override_quick_find_record_limit_enabled
            )

        self._conditions: List[FetchXMLCondition] = []
        self._filters: List[_FilterBuilder] = []

    def add_condition(  # pylint: disable=R0912
        self,
        *,
        attribute: str,
        operator: Union[str, FetchXMLOperator],
        value: Optional[Any] = None,
        values: Optional[List[Any]] = None,
        value_of: Optional[str] = None,
        column: Optional[str] = None,
        entity_name: Optional[str] = None,
        aggregate: Optional[FetchXMLAggregateType] = None,
        row_aggregate: Optional[Literal["countchildren"]] = None,
        alias: Optional[str] = None,
        uiname: Optional[str] = None,
        uitype: Optional[str] = None,
        uihidden: Optional[bool] = None,
    ) -> "_FilterBuilder":
        """Add a filtering condition to the filter.

        :param attribute: Attribute to filter.
        :param operator: Operator to use in the filter.
        :param value: If the filter requires a single value (e.g. `eq`), input the value here.
        :param values: If the filter requires multiple values (e.g. `in`), input the values here.
        :param value_of: Column to compare the selected attribute against using the selected operator.
        :param column: Filtering column.
        :param entity_name: Entity name.
        :param aggregate: Aggregation.
        :param row_aggregate: Row aggregation.
        :param alias: Alias.
        :param uiname: UI name.
        :param uitype: UI type.
        :param uihidden: UI Hidden?
        :return: The current instance of FilterBuilder.
        """

        if len(self._conditions) == 500:
            raise RuntimeError("Too many conditions (>500)")

        # Convert string to operators, raises TypeError if not valid
        if type(operator) == str:  # pylint: disable=C0123
            operator = FetchXMLOperator(operator)

        condition = FetchXMLCondition(attribute=attribute, operator=operator.value)
        if value is not None:
            condition["value"] = str(value)
        if values is not None:
            condition["values"] = [str(v) for v in values]
        if value_of is not None:
            condition["valueof"] = value_of
        if column is not None:
            condition["column"] = column
        if entity_name is not None:
            condition["entityname"] = entity_name
        if aggregate is not None:
            condition["aggregate"] = aggregate
        if row_aggregate is not None:
            condition["rowaggregate"] = row_aggregate
        if alias is not None:
            condition["alias"] = alias
        if uiname is not None:
            condition["uiname"] = uiname
        if uitype is not None:
            condition["uitype"] = uitype
        if uihidden is not None:
            condition["uihidden"] = "1" if uihidden else "0"  # type: ignore

        self._conditions.append(condition)
        return self

    def add_linked_entity(
        self,
        *,
        name: str,
        to: str,  # pylint: disable=C0103
        from_: Optional[str] = None,
        alias: Optional[str] = None,
        link_type: Optional[str] = None,
        visible: Optional[bool] = None,
        intersect: Optional[bool] = None,
        enable_prefiltering: Optional[bool] = None,
        prefilter_parameter_name: Optional[str] = None,
    ) -> Union["_EntityBuilder", "_LinkedEntityBuilder"]:
        """Add a linked entity from the first entity builder parent.
        Recurses up to the first parent that is either an EntityBuilder or LinkedEntityBuilder.
        Note that the maximum number of linked entities is 10.

        :param name: Name of the table to link to.
        :param to: Name of the navigation property to link the table with.
        :param from_: Name of the attribute in the linked table to link the table from.
        :param alias: Name to alias the linked entity under.
        :param link_type: How the link should be made, e.g., "outer", "inner", etc.
        :param visible: Visible?
        :param intersect: Intersect?
        :param enable_prefiltering: Enable pre-filtering?
        :param prefilter_parameter_name: Pre-filtering parameter name.
        :return: The parent instance of EntityBuilder or LinkedEntityBuilder.
        """

        return self._parent_builder.add_linked_entity(
            name=name,
            to=to,
            from_=from_,
            alias=alias,
            link_type=link_type,
            visible=visible,
            intersect=intersect,
            enable_prefiltering=enable_prefiltering,
            prefilter_parameter_name=prefilter_parameter_name,
        )

    def nested_filter(
        self,
        type_: FetchXMLFilterOperatorType = "and",
        is_quick_find_fields: Optional[bool] = None,
        override_quick_find_record_limit_enabled: Optional[bool] = None,
    ) -> "_FilterBuilder":
        """Nest another filter inside this filter Useful if different logical
        operator is needed to group certain conditions.

        :param type_: Logical operator used when multiple conditions are present.
        :param is_quick_find_fields: If True, the filter is a quick find filter.
        :param override_quick_find_record_limit_enabled: If True, override the 10_000 record quick order limit.
        :return: A new instance of FilterBuilder.
        """

        filter_builder = _FilterBuilder(
            self,
            type_=type_,
            is_quick_find_fields=is_quick_find_fields,
            override_quick_find_record_limit_enabled=override_quick_find_record_limit_enabled,
        )
        self._filters.append(filter_builder)
        return filter_builder

    def filter(
        self,
        type_: FetchXMLFilterOperatorType = "and",
        is_quick_find_fields: Optional[bool] = None,
        override_quick_find_record_limit_enabled: Optional[bool] = None,
    ) -> "_FilterBuilder":
        """Apply filtering to the parent entity's attributes.

        :param type_: Logical operator used when multiple conditions are present.
        :param is_quick_find_fields: If True, the filter is a quick find filter.
        :param override_quick_find_record_limit_enabled: If True, override the 10_000 record quick order limit.
        :return: A new instance of FilterBuilder.
        """

        filter_builder = _FilterBuilder(
            self,
            type_=type_,
            is_quick_find_fields=is_quick_find_fields,
            override_quick_find_record_limit_enabled=override_quick_find_record_limit_enabled,
        )
        self._parent_builder._filters.append(filter_builder)
        return filter_builder

    def build(self) -> str:
        """Build the FetchXML query string."""
        return self._parent_builder.build()
