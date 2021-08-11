"""
Aggregate and grouping results:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#aggregate-and-grouping-results

FetchXML aggregation documentation:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-aggregation
"""

from typing import List, Literal, Set, Union


__all__ = ["apl"]

filter_type = Union[Set[str], List[str]]


class APL:
    """Convenience functions for creating $apply parameters."""

    @staticmethod
    def groupby(columns: List[str], aggregate: str = None) -> str:
        """Group results by columns, optionally aggregate.

        :param columns: Columns to group by.
        :param aggregate: Aggregate grouped results by this function. Use `apl.aggregate(...)` to construct this.
        """
        aggregate = f",{aggregate}" if aggregate is not None else ""
        return f"groupby(({','.join(columns)}){aggregate})"

    @staticmethod
    def aggregate(*, col_: str, with_: Literal["average", "sum", "min", "max", "count"], as_: str) -> str:
        """Aggregate column with some aggregation function, and alias the result under some name.

        :param col_: Column to aggregate over.
        :param with_: How to aggregate the columns.
        :param as_: Aggregate result alias.
        """
        return f"aggregate({col_} with {with_} as {as_})"

    @staticmethod
    def filter(by: filter_type, group_by_columns: List[str]):
        """Group filtered values by columns.

        :param by: Filter results by this filter string before applying grouping. Use `ftr` to construct this.
        :param group_by_columns: Columns to group by.
        """
        return f"filter({APL._compile_filter(by).removeprefix('$filter=')})/" + APL.groupby(group_by_columns)

    @staticmethod
    def _compile_filter(values: filter_type):
        if isinstance(values, set):
            return "$filter=" + " or ".join([value.strip() for value in values])
        elif isinstance(values, list):
            return "$filter=" + " and ".join([value.strip() for value in values])


apl = APL()
