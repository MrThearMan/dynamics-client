from .enums import FetchXMLOperator


try:
    from typing import (
        TYPE_CHECKING,
        Any,
        Callable,
        Dict,
        Iterator,
        List,
        Literal,
        Optional,
        ParamSpec,
        Sequence,
        Set,
        Tuple,
        Type,
        TypedDict,
        TypeVar,
        Union,
    )
except ImportError:
    from typing import (
        TYPE_CHECKING,
        Any,
        Callable,
        Dict,
        Iterator,
        List,
        Optional,
        Sequence,
        Set,
        Tuple,
        Type,
        TypeVar,
        Union,
    )

    from typing_extensions import Literal, ParamSpec, TypedDict


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
    "TypeVar",
    "ParamSpec",
    "Iterator",
    "TYPE_CHECKING",
    "ResponseType",
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
    "T",
    "P",
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
T = TypeVar("T")  # pylint: disable=C0103
P = ParamSpec("P")  # pylint: disable=C0103
ResponseType = Union[Union[Dict[str, Any], List[Dict[str, Any]]], Exception, None]

LiteralBool = Literal["true", "false"]
FetchXMLOutputFormat = Literal["xml-ado", "xml-auto", "xml-elements", "xml-raw", "xml-platform"]
FetchXMLDateGroupingType = Literal["day", "week", "month", "quarter", "year", "fiscal-period", "fiscal-year"]
FetchXMLAggregateType = Literal["count", "countcolumn", "sum", "avg", "min", "max"]
FetchXMLBuildType = Literal["1.504021", "1.003017"]
FetchXMLFilterOperatorType = Literal["and", "or"]
FetchXMLFetchMappingType = Literal["internal", "logical"]


FetchXMLCondition = TypedDict(
    "FetchXMLCondition",
    {
        "column": str,
        "attribute": str,
        "operator": FetchXMLOperator,
        "value": str,
        "values": List[str],
        "valueof": str,
        "entityname": str,
        "aggregate": FetchXMLAggregateType,
        "rowaggregate": Literal["countchildren"],
        "alias": str,
        "uiname": str,
        "uitype": str,
        "uihidden": Literal["0", "1"],
    },
    total=False,
)


FetchXMLAttributeType = TypedDict(
    "FetchXMLAttributeType",
    {
        "name": str,
        "alias": str,
        "aggregate": FetchXMLAggregateType,
        "groupby": LiteralBool,
        "distinct": LiteralBool,
        "dategrouping": FetchXMLDateGroupingType,
        "usertimezone": LiteralBool,
        "addedby": str,
        "build": FetchXMLBuildType,
    },
    total=False,
)


FetchXMLOrderType = TypedDict(
    "FetchXMLOrderType",
    {
        "attribute": str,
        "alias": str,
        "descending": LiteralBool,
    },
    total=False,
)


FetchXMLType = TypedDict(
    "FetchXMLType",
    {
        "mapping": FetchXMLFetchMappingType,
        "version": str,
        "count": str,
        "page": str,
        "top": str,
        "aggregate": LiteralBool,
        "distinct": LiteralBool,
        "paging-cookie": str,
        "utc-offset": str,
        "output-format": FetchXMLOutputFormat,
        "min-active-row-version": LiteralBool,
        "returntotalrecordcount": LiteralBool,
        "no-lock": str,
    },
    total=False,
)


FetchXMLEntityType = TypedDict(
    "FetchXMLEntityType",
    {
        "name": str,
        "enableprefiltering": LiteralBool,
        "prefilterparametername": str,
    },
    total=False,
)


FetchXMLLinkedEntity = TypedDict(
    "FetchXMLLinkedEntity",
    {
        "name": str,
        "to": str,
        "from": str,
        "alias": str,
        "link-type": str,
        "visible": LiteralBool,
        "intersect": LiteralBool,
        "enableprefiltering": LiteralBool,
        "prefilterparametername": str,
    },
    total=False,
)


FetchXMLFilterType = TypedDict(
    "FetchXMLFilterType",
    {
        "type": FetchXMLFilterOperatorType,
        "isquickfindfields": LiteralBool,
        "overridequickfindrecordlimitenabled": LiteralBool,
    },
    total=False,
)
