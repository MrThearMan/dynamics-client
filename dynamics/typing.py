from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    ClassVar,
    Coroutine,
    Dict,
    Generator,
    Iterator,
    List,
    Literal,
    NamedTuple,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    TypedDict,
    TypeVar,
    Union,
)

# New in version 3.10
try:
    from typing import ParamSpec, TypeAlias, TypeGuard
except ImportError:
    from typing_extensions import ParamSpec, TypeAlias, TypeGuard

# New in version 3.11
try:
    from typing import NotRequired, Required
except ImportError:
    from typing_extensions import NotRequired, Required


from .enums import FetchXMLOperator

__all__ = [
    "Any",
    "Awaitable",
    "Callable",
    "ClassVar",
    "CompType",
    "Coroutine",
    "Coroutine",
    "Dict",
    "DynamicsClientGetResponse",
    "DynamicsClientPatchResponse",
    "DynamicsClientPostResponse",
    "ExpandDict",
    "ExpandKeys",
    "ExpandType",
    "ExpandValues",
    "ExpandValues",
    "FetchXMLAggregateType",
    "FetchXMLAttributeType",
    "FetchXMLBuildType",
    "FetchXMLCondition",
    "FetchXMLDateGroupingType",
    "FetchXMLEntityType",
    "FetchXMLFetchMappingType",
    "FetchXMLFilterOperatorType",
    "FetchXMLFilterType",
    "FetchXMLLinkedEntity",
    "FetchXMLOrderType",
    "FetchXMLOutputFormat",
    "FetchXMLType",
    "FieldType",
    "FilterType",
    "Generator",
    "Iterator",
    "List",
    "Literal",
    "LiteralBool",
    "MethodType",
    "NotRequired",
    "Optional",
    "OrderbyType",
    "P",
    "PaginationRules",
    "ParamSpec",
    "Required",
    "ResponseType",
    "Sequence",
    "Set",
    "T",
    "Tuple",
    "Type",
    "TYPE_CHECKING",
    "TypeAlias",
    "TypedDict",
    "TypeGuard",
    "TypeVar",
    "Union",
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


ExpandKeys: TypeAlias = Literal["select", "filter", "top", "orderby", "expand"]
ExpandValues: TypeAlias = Union[List[str], Set[str], int, OrderbyType, Dict[str, ExpandType]]
ExpandDict: TypeAlias = Dict[str, Optional[ExpandType]]
FieldType: TypeAlias = Union[str, int, float, bool, None]
CompType: TypeAlias = Union[str, int, float]
T = TypeVar("T")
P = ParamSpec("P")
ResponseType: TypeAlias = Union[Union[Dict[str, Any], List[Dict[str, Any]]], Exception, None]


DynamicsOKResponse = TypedDict(
    "DynamicsOKResponse",
    {
        "value": List[Dict[str, Any]],
        "@odata.context": str,
        "@odata.nextLink": NotRequired[str],
        "@odata.count": NotRequired[int],
    },
)


# https://learn.microsoft.com/en-us/power-apps/developer/data-platform/webapi/compose-http-requests-handle-errors#include-more-details-with-errors
DynamicsErrorResponseData = TypedDict(
    "DynamicsErrorResponseData",
    {
        "code": Required[str],
        "message": Required[str],
        "@Microsoft.PowerApps.CDS.ErrorDetails.OperationStatus": str,
        "@Microsoft.PowerApps.CDS.ErrorDetails.SubErrorCode": str,
        "@Microsoft.PowerApps.CDS.HelpLink": str,
        "@Microsoft.PowerApps.CDS.TraceText": str,
        "@Microsoft.PowerApps.CDS.InnerError.Message": str,
    },
    total=False,
)


class DynamicsErrorResponse(TypedDict):
    error: DynamicsErrorResponseData


DynamicsResponse: TypeAlias = Union[DynamicsOKResponse, DynamicsErrorResponse]


class DynamicsClientGetResponse(TypedDict):
    data: List[Dict[str, Any]]
    count: Optional[int]
    next_link: Optional[str]


class DynamicsClientPostResponse(TypedDict):
    data: Dict[str, Any]


class DynamicsClientPatchResponse(TypedDict):
    data: Dict[str, Any]


class PaginationRules(TypedDict):
    pages: int
    children: NotRequired[Dict[str, PaginationRules]]


class PaginationData(NamedTuple):
    index: int
    key: str
    query: str
    rules: PaginationRules


LiteralBool: TypeAlias = Literal["true", "false"]
FetchXMLOutputFormat: TypeAlias = Literal["xml-ado", "xml-auto", "xml-elements", "xml-raw", "xml-platform"]
FetchXMLDateGroupingType: TypeAlias = Literal["day", "week", "month", "quarter", "year", "fiscal-period", "fiscal-year"]
FetchXMLAggregateType: TypeAlias = Literal["count", "countcolumn", "sum", "avg", "min", "max"]
FetchXMLBuildType: TypeAlias = Literal["1.504021", "1.003017"]
FetchXMLFilterOperatorType: TypeAlias = Literal["and", "or"]
FetchXMLFetchMappingType: TypeAlias = Literal["internal", "logical"]


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
