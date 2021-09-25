from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Set, Tuple, Type, TypedDict, Union


__all__ = [
    "List",
    "Dict",
    "Optional",
    "Any",
    "Literal",
    "Union",
    "Set",
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
