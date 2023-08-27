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
    from typing import ParamSpec, TypeGuard
except ImportError:
    from typing_extensions import ParamSpec, TypeGuard

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
    "ParamSpec",
    "Required",
    "ResponseType",
    "Sequence",
    "Set",
    "T",
    "Tuple",
    "Type",
    "TYPE_CHECKING",
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


ExpandKeys = Literal["select", "filter", "top", "orderby", "expand"]
ExpandValues = Union[List[str], Set[str], int, OrderbyType, Dict[str, ExpandType]]
ExpandDict = Dict[str, Optional[ExpandType]]
FieldType = Union[str, int, float, bool, None]
CompType = Union[str, int, float]
T = TypeVar("T")
P = ParamSpec("P")
ResponseType = Union[Union[Dict[str, Any], List[Dict[str, Any]]], Exception, None]


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


DynamicsResponse = Union[DynamicsOKResponse, DynamicsErrorResponse]


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
