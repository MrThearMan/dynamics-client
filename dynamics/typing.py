from .enums import FetchXMLOperator


try:
    from typing import (
        TYPE_CHECKING,
        Any,
        Callable,
        Dict,
        List,
        Literal,
        Optional,
        Sequence,
        Set,
        Tuple,
        Type,
        TypedDict,
        Union,
    )
except ImportError:
    from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, Sequence, Set, Tuple, Type, Union

    from typing_extensions import Literal, TypedDict


__all__ = [
    "List",
    "Dict",
    "Optional",
    "Any",
    "Literal",
    "Union",
    "Set",
    "Sequence",
    "Type",
    "Tuple",
    "TypedDict",
    "TYPE_CHECKING",
    "MethodType",
    "OrderbyType",
    "FilterType",
    "ExpandType",
    "ExpandKeys",
    "ExpandValues",
    "ExpandValues",
    "ExpandDict",
    "Callable",
    "CompType",
    "FieldType",
    "LiteralBool",
    "FetchXMLCondition",
    "FetchXMLAttributeType",
    "FetchXMLOrderType",
    "FetchXMLType",
    "FetchXMLEntityType",
    "FetchXMLLinkedEntity",
    "FetchXMLFilterType",
    "FetchXMLAggregateType",
    "FetchXMLOutputFormat",
    "FetchXMLDateGroupingType",
    "FetchXMLBuildType",
    "FetchXMLFetchMappingType",
    "FetchXMLFilterOperatorType",
]


MethodType = Literal["get", "post", "patch", "delete"]
OrderbyType = Dict[str, Literal["asc", "desc"]]
FilterType = Union[Set[str], List[str]]


class ExpandType(TypedDict):
    select: List[str]
    filter: FilterType
    top: int
    orderby: OrderbyType
    expand: Dict[str, "ExpandType"]


ExpandKeys = Literal["select", "filter", "top", "orderby", "expand"]
ExpandValues = Union[List[str], Set[str], int, OrderbyType, Dict[str, ExpandType]]
ExpandDict = Dict[str, Optional[ExpandType]]
FieldType = Union[str, int, float, bool, None]
CompType = Union[str, int, float]

LiteralBool = Literal["true", "false"]
FetchXMLOutputFormat = Literal["xml-ado", "xml-auto", "xml-elements", "xml-raw", "xml-platform"]
FetchXMLDateGroupingType = Literal["day", "week", "month", "quarter", "year", "fiscal-period", "fiscal-year"]
FetchXMLAggregateType = Literal["count", "countcolumn", "sum", "avg", "min", "max"]
FetchXMLBuildType = Literal["1.504021", "1.003017"]
FetchXMLFilterOperatorType = Literal["and", "or"]
FetchXMLFetchMappingType = Literal["internal", "logical"]


class FetchXMLCondition(TypedDict, total=False):
    column: str
    attribute: str
    operator: FetchXMLOperator
    value: str
    values: List[str]
    value_of: str
    entity_name: str
    aggregate: FetchXMLAggregateType
    row_aggregate: Literal["countchildren"]
    alias: str
    uiname: str
    uitype: str
    uihidden: Literal["0", "1"]


class FetchXMLAttributeType(TypedDict, total=False):
    name: str
    alias: str
    aggregate: FetchXMLAggregateType
    groupby: LiteralBool
    distinct: LiteralBool
    date_grouping: FetchXMLDateGroupingType
    user_timezone: LiteralBool
    added_by: str
    build: FetchXMLBuildType


class FetchXMLOrderType(TypedDict, total=False):
    attribute: str
    alias: str
    descending: LiteralBool


class FetchXMLType(TypedDict, total=False):
    mapping: FetchXMLFetchMappingType
    version: str
    count: str
    page: str
    top: str
    aggregate: LiteralBool
    distinct: LiteralBool
    paging_cookie: str
    utc_offset: str
    output_format: FetchXMLOutputFormat
    min_active_row_version: LiteralBool
    return_total_record_count: LiteralBool
    no_lock: str


class FetchXMLEntityType(TypedDict, total=False):
    name: str
    enable_prefiltering: LiteralBool
    prefilter_parameter_name: str


_LEB = TypedDict("_LEB", {"from": str}, total=False)


class FetchXMLLinkedEntity(_LEB, total=False):
    name: str
    to: str
    alias: str
    link_type: str
    visible: LiteralBool
    intersect: LiteralBool
    enable_prefiltering: LiteralBool
    prefilter_parameter_name: str


class FetchXMLFilterType(TypedDict, total=False):
    type: FetchXMLFilterOperatorType
    is_quick_find_fields: LiteralBool
    override_quick_find_record_limit_enabled: LiteralBool
