"""
Dynamics Api Client. API Reference Docs:
https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api

How to use:
1. Init the client:                         client = DynamicsClient(...)
                                            client = DynamicsClient.from_environment()
2. Set the table:                           client.table = "..."

Required for PATCH and DELETE, otherwese optional:
3. Set row:                                 client.row_id = "..."

Optional steps:
4. Set query options:                       client.select = [...], client.expand = {...}, etc.
5. Set headers:                             client.headers = {...} or client[...] = ...

Make a GET request:                         result = client.GET()
Make a POST request:                        result = client.POST(data={...})
Make a PATCH request:                       result = client.PATCH(data={...})
Make a DELETE request:                      result = client.DELETE()

Remember to reset between queries:          client.reset_query()

Author: Matti Lamppu.
Date: April 5th, 2021.
"""

import os
import json
import logging
from functools import wraps
from typing import List, Dict, Optional, Any, Literal, Union, Set, Type, TypedDict

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from . import status
from .api_actions import Actions
from .api_functions import Functions
from .utils import sentinel
from .exceptions import (
    DynamicsException,
    ParseError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
    DuplicateRecordError,
    PayloadTooLarge,
    APILimitsExceeded,
    OperationNotImplemented,
    WebAPIUnavailable,
)

try:
    from django.core.cache import cache
except ImportError:
    from .utils import cache


__all__ = ["DynamicsClient"]


logger = logging.getLogger(__name__)

method_type = Literal["get", "post", "patch", "delete"]
orderby_type = Dict[str, Literal["asc", "desc"]]
filter_type = Union[Set[str], List[str]]


class ExpandType(TypedDict):
    select: List[str]
    filter: filter_type
    top: int
    orderby: orderby_type
    expand: Dict[str, "ExpandType"]


expand_keys = Literal["select", "filter", "top", "orderby", "expand"]
expand_values = Union[List[str], Set[str], int, orderby_type, Dict[str, ExpandType]]
expand_type = Dict[str, Optional[ExpandType]]


def error_simplification_available(func):
    """Errors in the function decorated with this decorator can be simplified to just a
    DynamicsException with default error message using the keyword: 'simplify_errors'.
    This is useful if you want to hide error details from frontend users.

    You can use the 'raise_separately' keyword to list exception types to exclude from this
    simplification, if separate handling is needed.

    :param func: Decorated function.
    """

    @wraps(func)
    def inner(*args, **kwargs):
        simplify_errors: bool = kwargs.pop("simplify_errors", False)
        raise_separately: List[Type[Exception]] = kwargs.pop("raise_separately", [])

        try:
            return func(*args, **kwargs)
        except Exception as error:
            logger.error(error)
            if not simplify_errors or any([isinstance(error, exception) for exception in raise_separately]):
                raise error
            else:
                raise DynamicsException("There was a problem communicating with the server.")

    return inner


class DynamicsClient:
    """Dynamics client for making queries from a Microsoft Dynamics 365 database."""

    request_counter: int = 0
    error_dict = {
        status.HTTP_400_BAD_REQUEST: ParseError,
        status.HTTP_401_UNAUTHORIZED: AuthenticationFailed,
        status.HTTP_403_FORBIDDEN: PermissionDenied,
        status.HTTP_404_NOT_FOUND: NotFound,
        status.HTTP_405_METHOD_NOT_ALLOWED: MethodNotAllowed,
        status.HTTP_412_PRECONDITION_FAILED: DuplicateRecordError,
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: PayloadTooLarge,
        status.HTTP_429_TOO_MANY_REQUESTS: APILimitsExceeded,
        status.HTTP_501_NOT_IMPLEMENTED: OperationNotImplemented,
        status.HTTP_503_SERVICE_UNAVAILABLE: WebAPIUnavailable,
    }

    def __init__(self, api_url: str, token_url: str, client_id: str, client_secret: str, scope: List[str]):
        """Establish a Microsoft Dynamics 365 Dataverse API client connection
        using OAuth 2.0 Client Credentials Flow. Client Credentials require an application user to be
        created in Dynamics, and granting it an appropriate security role.

        :param api_url: API root URL. Format: https://[Organization URI]/api/data/v{api_version}
        :param token_url: URL to the Dynamics/Azure token endpoint.
                          Format: https://[Dynamics Token URI]/path/to/token
        :param client_id: Dynamics User ID.
        :param client_secret: Dynamics User Secret that proves its identity when password is required.
        :param scope: List of urls that define the database records that the API connection has access to.
                      Most likely in this format: https://[Organization URI]/.default
        """

        self._api_url = api_url.rstrip("/") + "/"
        self._session = OAuth2Session(client=BackendApplicationClient(client_id=client_id))
        token = cache.get("dynamics-client-token", None)
        if token is None:
            token = self._session.fetch_token(token_url=token_url, client_secret=client_secret, scope=scope)
            cache.set("dynamics-client-token", token, int(token.get("expires_in", 3599)) - 60)
        else:
            self._session.token = token

        self.actions = Actions(client=self)
        """Predefined dynamics API actions. Used to make certain changes to data."""
        self.functions = Functions(client=self)
        """Predefined dynamics API functions. Used to fetch certain types of data."""

        self._select: List[str] = []
        self._expand: expand_type = {}
        self._filter: filter_type = []
        self._orderby: orderby_type = {}
        self._top: int = 0
        self._count: bool = False

        self._table = ""
        self._action = ""
        self._row_id = ""
        self._add_ref_to_property = ""
        self._pre_expand = ""
        self._apply = ""

        self._headers: Dict[str, str] = {}
        self._pagesize: int = 5000

    def __getitem__(self, key):
        return self.headers[key]

    def __setitem__(self, key, value):
        self.headers[key] = value

    @classmethod
    def from_environment(cls):
        """Create a client from environment variables:

        * DYNAMICS_API_URL: url string
        * DYNAMICS_TOKEN_URL: url string
        * DYNAMICS_CLIENT_ID: client id string
        * DYNAMICS_CLIENT_SECRET: client secret key string
        * DYNAMICS_SCOPE: comma separated list of urls

        :raises KeyError: An environment variable was not configured properly
        """

        base_url = os.environ["DYNAMICS_API_URL"]
        token_url = os.environ["DYNAMICS_TOKEN_URL"]
        client_id = os.environ["DYNAMICS_CLIENT_ID"]
        client_secret = os.environ["DYNAMICS_CLIENT_SECRET"]
        scope = os.environ["DYNAMICS_SCOPE"].split(",")

        return cls(base_url, token_url, client_id, client_secret, scope)

    @property
    def current_query(self) -> str:
        """Constructs query from current options, leaving out empty ones."""

        query = self._api_url + self.table

        if self.row_id:
            query += f"({self.row_id})"
        if self.pre_expand:
            query += f"/{self.pre_expand}"
        if self.action:
            if query[-1] != "/":
                query += "/"
            query += self.action
        if self.add_ref_to_property:
            query += f"/{self.add_ref_to_property}/$ref"
        if qo := self._compile_query_options():
            query += qo

        return query

    def _compile_query_options(self) -> str:
        query_options = "&".join(
            [
                statement
                for statement in [
                    self._compile_expand(),
                    self._compile_apply(),
                    self._compile_select(),
                    self._compile_filter(),
                    self._compile_top(),
                    self._compile_count(),
                    self._compile_orderby(),
                ]
                if statement
            ]
        )

        return f"?{query_options}" if query_options else ""

    @property
    def headers(self) -> Dict[str, str]:
        """HTTP request headers."""
        return self._headers

    def reset_query(self):
        """Resets all client options and headers."""
        self._select: List[str] = []
        self._expand: expand_type = {}
        self._filter: filter_type = []
        self._orderby: orderby_type = {}
        self._top: int = 0
        self._count: bool = False

        self._table = ""
        self._action = ""
        self._row_id = ""
        self._add_ref_to_property = ""
        self._pre_expand = ""
        self._apply = ""

        self._headers: Dict[str, str] = {}

    def set_default_headers(self, method: method_type):
        """Sets per method default headers. Does not override user added headers."""

        self.headers.setdefault("OData-MaxVersion", "4.0")
        self.headers.setdefault("OData-Version", "4.0")
        self.headers.setdefault("Accept", "application/json; odata.metadata=minimal")

        if method in ["post", "patch", "delete"]:
            self.headers.setdefault("Content-Type", "application/json; charset=utf-8")

        if method in ["post", "patch"]:
            self.headers.setdefault("Prefer", "return=representation")
            self.headers.setdefault("MSCRM.SuppressDuplicateDetection", "false")

        if method in ["patch"]:
            self.headers.setdefault("If-None-Match", "null")
            self.headers.setdefault("If-Match", "*")

        self.headers.setdefault("Prefer", f"odata.maxpagesize={self.pagesize}")

    def _error_handling(self, status_code: int, error_message: str, method: method_type):
        """Error handling based on these expected error statuses:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/compose-http-requests-handle-errors#identify-status-codes

        :param status_code: Error status from dynamics
        :param error_message: Error message from dynamics.
        :param method: HTTP method in question.
        """

        logger.error(f"Dynamics client query {self.current_query} failed with status {status_code}: {error_message}")
        error = self.error_dict.get(status_code, DynamicsException)
        raise error(method=method, detail=error_message)

    @error_simplification_available
    def GET(self, not_found_ok: bool = False, next_link: Optional[str] = None) -> List[Dict[str, Any]]:
        """Make a request to the Dataverse API with currently added query options.

        Please also read the decorator's documentation!

        :param not_found_ok: No entities returned should not raise NotFound error, but return empty list instead.
        :param next_link: Request the next set of records from this link instead.
        """

        self.request_counter += 1
        self.set_default_headers("get")

        if next_link is not None:
            response = self._session.get(next_link, headers=self.headers)
        else:
            response = self._session.get(self.current_query, headers=self.headers)

        data = response.json()

        # Always returns a list, even if only one row is selected
        entities = data.get("value", [data])
        errors = data.get("error", {})
        count = data.get("@odata.count", "")

        if errors:
            self._error_handling(status_code=response.status_code, error_message=errors.get("message"), method="get")
        elif not entities:
            if not_found_ok:
                return []
            message = "No records matching the given criteria."
            self._error_handling(status_code=status.HTTP_404_NOT_FOUND, error_message=message, method="get")

        # Fetch more data if needed
        for i, row in enumerate(entities):
            for column_key in list(row.keys()):
                if "@odata.nextLink" in column_key:

                    # Sometimes @odata.next links will appear even if all items were fetched.
                    # We know how many items should be fetched from odata.maxpagesize header,
                    # therefore, if the @odata.next link appears before that, we can ignore it.
                    #
                    key = column_key[:-15]
                    if len(entities[i][key]) < self.pagesize:
                        row.pop(column_key)
                        continue

                    # When fetching the next page of results, it can include the last
                    # page of data as well, so we filter those out. Although, This doesn't seem
                    # to be the intended way this should work, based on this:
                    #
                    # https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#retrieve-related-tables-by-expanding-navigation-properties
                    #
                    extra = self.GET(not_found_ok=not_found_ok, next_link=row.pop(column_key))
                    id_tags = [value["@odata.etag"] for value in entities[i][key]]
                    extra = [value for value in extra if value["@odata.etag"] not in id_tags]

                    entities[i][key] += extra

        if count:
            entities.insert(0, count)

        return entities

    @error_simplification_available
    def POST(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new row in a table. Must have 'table' attribute set. Use expand and select to reduce returned data.

        Please also read the decorator's documentation!

        :param data: POST data.
        """

        self.request_counter += 1
        self.set_default_headers("post")

        data = json.dumps(data).encode()
        response = self._session.post(self.current_query, data=data, headers=self.headers)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return {}

        data = response.json()

        if errors := data.get("error"):
            self._error_handling(status_code=response.status_code, error_message=errors["message"], method="post")

        return data

    @error_simplification_available
    def PATCH(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update row in a table. Must have 'table' and 'row_id' attributes set.
        Use expand and select to reduce returned data.

        Please also read the decorator's documentation!

        :param data: PATCH data.
        """

        self.request_counter += 1
        self.set_default_headers("patch")

        data = json.dumps(data).encode()
        response = self._session.patch(self.current_query, data=data, headers=self.headers)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return {}

        data = response.json()

        if errors := data.get("error"):
            self._error_handling(status_code=response.status_code, error_message=errors["message"], method="patch")

        return data

    @error_simplification_available
    def DELETE(self) -> None:
        """Delete row in a table. Must have 'table' and 'row_id' attributes set.

        Please also read the decorator's documentation!
        """

        self.request_counter += 1
        self.set_default_headers("delete")

        response = self._session.delete(self.current_query, headers=self.headers)

        if response.status_code == status.HTTP_204_NO_CONTENT:
            return

        data = response.json()

        if errors := data.get("error"):
            self._error_handling(status_code=response.status_code, error_message=errors["message"], method="delete")

    @property
    def table(self) -> str:
        """Table to search in."""
        return self._table

    @table.setter
    def table(self, value: str):
        self._table = value

    @property
    def action(self) -> str:
        """Set the Dynamics Web API action or function to use.

        It is recommended to read the API Function Reference:
        https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/functions

        ...and how to Use Web API Functions:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-functions

        ...as well as the API Action Reference
        https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/actions

        ...and how to Use Web API Actions:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/use-web-api-actions.

        Most of the time you don't need to set this, since you can use the .actions and .functions attributes
        to make these queries.
        """
        return self._action

    @action.setter
    def action(self, value: str):
        self._action = value

    @property
    def row_id(self) -> str:
        """Search only from the row with this id.
        If the table has an alternate key defined, you can use
        'foo=bar' or 'foo=bar,fizz=buzz' to retrive a single row:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/retrieve-entity-using-web-api#retrieve-using-an-alternate-key
        Alternate keys are not enabled by default in Dynamics, so those might not work at all.
        """
        return self._row_id

    @row_id.setter
    def row_id(self, value: str):
        self._row_id = value

    @property
    def add_ref_to_property(self) -> str:
        """Add reference for this navigation property. This indicates,
        that POST data will contain the API url to a matching row id
        in the table this navigation property is meant to link to,
        like this: "@odata.id": "<API URI>/<table>(<id>)".

        This should only be used to link existing rows. Adding references
        for new rows can be done on create with this in POST data:
        "<nav_property>@odata.bind": "/<table>(<id>)".
        """
        return self._add_ref_to_property

    @add_ref_to_property.setter
    def add_ref_to_property(self, value: str):
        self._add_ref_to_property = value

    @property
    def pre_expand(self) -> str:
        """Expand/navigate to some linked table in this table
        before taking any queryoptions into account.
        This will save you having to use the expand statement itself,
        if all you are looking for is under this table anyway.
        """
        return self._pre_expand

    @pre_expand.setter
    def pre_expand(self, value: str):
        self._pre_expand = value

    @property
    def show_annotations(self) -> bool:
        """Show annotations for returned data, e.g. enum values, GUID names, etc.
        Helpful for development and debugging.
        https://docs.microsoft.com/en-us/odata/webapi/include-annotations
        """
        return self.headers.get("Prefer") == 'odata.include-annotations="*"'

    @show_annotations.setter
    def show_annotations(self, value: bool):
        if value:
            self.headers["Prefer"] = 'odata.include-annotations="*"'
        elif self.headers.get("Prefer") == 'odata.include-annotations="*"':
            self.headers.pop("Prefer")

    @property
    def select(self) -> List[str]:
        """Get current $select statement."""
        return self._select

    @select.setter
    def select(self, items: List[str]):
        """Set $select statement. Select which columns are returned from the table."""
        self._select = items

    def _compile_select(self, values: List[str] = sentinel) -> str:
        if values is sentinel:
            values = self._select

        return "$select=" + ",".join([key for key in values]) if values else ""

    @property
    def expand(self) -> expand_type:
        """Get current $expand statement."""
        return self._expand

    @expand.setter
    def expand(self, items: expand_type):
        """Set $expand statement, with possible nested statements.
        Controls what data from related entities is returned.

        Nested expand statement limitations (WEB API v9.1):

        1. Nested expand statements can *only* be applied to **many-to-one/single-valued** relationships.
        This means nested expands for collections do not work!

        2. Each request can include a maximum of 10 expand statements.
        This applies to non-nested statements as well! There is no limit on the depth of nested
        expand statements, so long as the total is 10.

        :param items: What linked tables (a.k.a. naviagation properties) to expand and
                      what statements to apply inside the expanded tables.
                      If items-dict value is set to an empty dict, no query options are used.
                      Otherwise, valid keys for the items-dict are 'select', 'filter', 'top', 'orderby', and 'expand'.
                      Values under these keys should be constructed in the same manner as they are
                      when outside the expand statement, e.g. 'select' takes a List[str], 'top' an int, etc.
        """

        self._expand = items

    def _compile_expand(self, items: expand_type = sentinel) -> str:
        if items is sentinel:
            items = self._expand

        if not items:
            return ""

        return "$expand=" + ",".join(
            [
                f"{key}(" + ";".join([self._expand_commands(name, values) for name, values in value.items()]) + f")"
                if value
                else f"{key}"
                for key, value in items.items()
            ]
        )

    def _expand_commands(self, name: expand_keys, values: expand_values) -> str:
        """Compile commands inside an expand statement."""

        if name == "select":
            return self._compile_select(values)
        elif name == "filter":
            return self._compile_filter(values)
        elif name == "orderby":
            return self._compile_orderby(values)
        elif name == "top":
            return self._compile_top(values)
        elif name == "expand":
            return self._compile_expand(values)
        else:
            raise KeyError(f"'{name}' is not a valid query inside expand statement!")

    @property
    def filter(self) -> filter_type:
        """Get current $filter statement"""
        return self._filter

    @filter.setter
    def filter(self, items: filter_type):
        """Set $filter statement. Sets the criteria for which entities will be returned.

        It is recommended to read the API Query Function Reference:
        https://docs.microsoft.com/en-us/dynamics365/customer-engagement/web-api/queryfunctions

        ...and how to Query data using the Web API:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api.

        You can input the filters as strings, or use the included `ftr`-object to construct them.

        Below is a list of the standard operators:

        - **eq** = Equal: 'foo *eq* bar'
        - **ne** = Not Equal: 'foo *ne* bar'
        - **gt** = Greater than: 'foo *gt* bar'
        - **ge** = Greater than or equal: 'foo *ge* bar'
        - **lt** = Less than: 'foo *lt* bar'
        - **le** = Less than or equal: 'foo *le* bar'
        - **and** = Logical and: 'foo lt bar *and* foo gt baz'
        - **or** = Logical or: 'foo lt bar *or* foo gt baz'
        - **not** = Logical negation: '*not* foo lt bar'
        - **()** = Precedence grouping '(foo lt bar) or (foo gt baz)'
        - **contains(key,'value')** = Key contains string: '*contains(foo,'bar')*'
        - **endswith(key,'value')** = Key ends with string: '*endswith(foo,'bar')*'
        - **startswith(key,'value')** = Key starts with string: '*startswith(foo,'bar')*'

        :param items: If a list-object, 'and' the items. If a set-object, 'or' the items.
        """

        if not isinstance(items, (set, list)):
            raise TypeError("Filter items must be either a set or a list.")
        elif not items:
            raise ValueError("Filter list cannot be empty.")

        self._filter = items

    def _compile_filter(self, values: filter_type = sentinel):
        if values is sentinel:
            values = self._filter

        if not values:
            return ""

        if isinstance(values, set):
            return "$filter=" + " or ".join([value.strip() for value in values])
        elif isinstance(values, list):
            return "$filter=" + " and ".join([value.strip() for value in values])

    @property
    def apply(self):
        """Current apply statement."""
        return self._apply

    @apply.setter
    def apply(self, statement: str):
        """Set the $apply statement. Aggregates or groups results.

        It is recommended to read how to aggregate and grouping results:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/query-data-web-api#aggregate-and-grouping-results

        ...and the FetchXML aggregation documentation:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/use-fetchxml-aggregation

        You can input the apply-statement as a string, or use the included `apl`-object to construct it.

        :param statement: aggregate, groupby, or filter apply-string.
        """

        self._apply = statement

    def _compile_apply(self, statement: str = sentinel):
        if statement is sentinel:
            statement = self._apply

        return f"$apply={statement}" if statement else ""

    @property
    def top(self) -> int:
        """Get current $top statement"""
        return self._top

    @top.setter
    def top(self, number: int):
        """Set $top statement. Limits the number of results returned.
        Note: You should not use 'top' and 'count' in the same query.
        """
        self._top = number

    def _compile_top(self, number: int = sentinel) -> str:
        if number is sentinel:
            number = self._top

        return f"$top={number}" if number != 0 else ""

    @property
    def orderby(self) -> orderby_type:
        """Get current $orderby statement"""
        return self._orderby

    @orderby.setter
    def orderby(self, items: orderby_type):
        """Set $orderby statement. Specifies the order in which items are returned."""

        if isinstance(items, dict):
            raise TypeError("Orderby items must be a dict.")
        elif not items:
            raise ValueError("Orderby dict must not be empty.")

        self._orderby = items

    def _compile_orderby(self, values: orderby_type = sentinel) -> str:
        if values is sentinel:
            values = self._orderby

        if not values:
            return ""

        return f"$orderby=" + ",".join([f"{key} {order}" for key, order in values.items()])

    @property
    def count(self) -> bool:
        """Get current $count statement"""
        return self._count

    @count.setter
    def count(self, value: bool):
        """Set $count statement. Include the count of entities that match the filter criteria in the results.
        Count will be the first item in the list of results.
        Note: You should not use 'count' and 'top' in the same query.
        """
        self._count = value

    def _compile_count(self, value: bool = sentinel) -> str:
        if value is sentinel:
            value = self._count

        return f"$count=true" if value else ""

    @property
    def pagesize(self) -> int:
        """Return currently set pagesize."""
        return self._pagesize

    @pagesize.setter
    def pagesize(self, value: int):
        """Specify the number of tables to return in a page."""

        if value < 1:
            ValueError(f"Value must be bigger than 0. Got {value}.")
        elif value > 5000:
            ValueError(f"Max pagesize is 5000. Got {value}.")

        self._pagesize = value
