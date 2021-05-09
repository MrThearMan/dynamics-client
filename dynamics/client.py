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

Query with no table nor query options set to get a list of tables in the database.
Use 'fetch_schema' for an xml representation of the relational ascpects of the data.

Author: Matti Lamppu.
Date: May 9th, 2021.
"""

import os
import json
import logging
import xml.etree.ElementTree as ET
from operator import attrgetter
from xml.dom.minidom import parseString as pretty_xml
from typing import List, Dict, Optional, Any, Literal, Union, Set

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from . import status
from .exceptions import (
    DynamicsException,
    DuplicateRecordError,
    PayloadTooLarge,
    APILimitsExceeded,
    OperationNotImplemented,
    WebAPIUnavailable,
    ParseError,
    AuthenticationFailed,
    PermissionDenied,
    NotFound,
    MethodNotAllowed,
)


__all__ = [
    "DynamicsClient",
]


logger = logging.getLogger(__name__)

method_type = Literal["get", "post", "patch", "delete"]
orderby_type = Dict[str, Literal["desc", "asc"]]

# $select takes List[str], $fitler takes List[str] or Set[str],
# $top takes int, and $orderby takes orderby_type.
# Nested $expand takes a dict like defined here
expand_keys = Literal["select", "filter", "top", "orderby", "expand"]
expand_values = Union[List[str], Set[str], int, orderby_type, Dict]
expand_subcommands = Dict[expand_keys, expand_values]


class DynamicsClient:
    """Dynamics client for making queries from a Microsoft Dynamics 365 database."""

    def __init__(self, api_url: str, token_url: str, client_id: str, client_secret: str, scope: List[str]):
        """Establish a Microsoft Dynamics 365 Dataverse API client connection.

        :param api_url: Url in form: 'https://[Organization URI]/api/data/v{api_version}'
        :param token_url: Url in form: 'https://[Dynamics Token URI]/path/to/token'
        :param client_id: Client id (e.g. UUID).
        :param client_secret: Client secret (e.g. OAuth password).
        :param scope: List of urls in form: 'https://[Organization URI]/scope'.
                      Defines the database records that the API connection has access to.
        """

        # [sic] Assure that url ends in forward slash
        self.api_url = api_url.rstrip("/") + "/"

        # [sic] Scope not given here, since we don't have a token yet
        client = BackendApplicationClient(client_id=client_id)
        self.api = OAuth2Session(client=client)

        # Fetch token
        self.api.fetch_token(token_url=token_url, client_id=client_id, client_secret=client_secret, scope=scope)

        # Query options
        self._select = ""
        self._expand = ""
        self._top = ""
        self._filter = ""
        self._orderby = ""
        self._count = ""

        self._table = ""
        self._row_id = ""
        self._add_ref_to_property = ""

        self.headers = {}

    @classmethod
    def from_environment(cls):
        """Create a client from environment variables:

        * DYNAMICS_BASE_URL (api_url): url string
        * DYNAMICS_TOKEN_URL: url string
        * DYNAMICS_CLIENT_ID: client id string
        * DYNAMICS_CLIENT_SECRET: client secret key string
        * DYNAMICS_SCOPE: comma separated list of urls

        :raises KeyError: An environment variable was not configured properly
        """

        base_url = os.environ["DYNAMICS_BASE_URL"]
        token_url = os.environ["DYNAMICS_TOKEN_URL"]
        client_id = os.environ["DYNAMICS_CLIENT_ID"]
        client_secret = os.environ["DYNAMICS_CLIENT_SECRET"]
        scope = os.environ["DYNAMICS_SCOPE"].split(",")

        return cls(base_url, token_url, client_id, client_secret, scope)

    @property
    def current_query(self) -> str:
        """Constructs query from current options, leaving out empty ones."""

        query = self.api_url + self.table

        if self.row_id:
            query += f"({self.row_id})"
        if self.add_ref_to_property:
            query += f"/{self.add_ref_to_property}/$ref"
        if (qo := self.compile_query_options()) and not self.add_ref_to_property:
            query += qo

        return query

    def fetch_schema(self) -> str:
        """Fetches Dynamics schema for observation."""

        def sortchildrenby(parent, attr):
            parent[:] = sorted(parent, key=lambda child: child.get(attr, ""))
            parent[:] = sorted(parent, key=attrgetter("tag"))

        ET.register_namespace("edmx", "http://docs.oasis-open.org/odata/ns/edmx")
        ET.register_namespace("", "http://docs.oasis-open.org/odata/ns/edm")

        request = self.api.get(self.api_url + "$metadata")
        xml_string = pretty_xml(request.text).toprettyxml(indent="  ")

        tree = ET.ElementTree(ET.fromstring(xml_string))
        root = (
            tree.getroot()
            .find("edmx:DataServices", namespaces={"edmx": "http://docs.oasis-open.org/odata/ns/edmx"})
            .find("Schema", namespaces={"": "http://docs.oasis-open.org/odata/ns/edm"})
        )

        sortchildrenby(root, "Name")
        for child in root:
            sortchildrenby(child, "Name")

        xml_prettyfied = pretty_xml(ET.tostring(root)).toprettyxml(indent="  ")
        xml_prettyfied = "\n".join([e for e in xml_prettyfied.split("\n") if e.strip()])

        to_replace = [
            #
            # Namespace
            ("mscrm.", ""),
            #
            # Attributes
            ('Name="', 'name="'),
            ('Type="', 'type="'),
            ('Property="', 'property="'),
            ('Referencedproperty="', 'referenced_property="'),
            ('Nullable="', 'nullable="'),
            ('Unicode="', 'unicode="'),
            ('Scale="', 'scale="'),
            ('Basetype="', 'basetype="'),
            ('Term="', 'term="'),
            ('Path="', 'path="'),
            ('Target="', 'target="'),
            ('Partner="', 'partner="'),
            ('Namespace="', 'namespace="'),
            ('Entitytype="', 'entity_type="'),
            ('Propertypath="', 'property_path="'),
            ('Containstarget="', 'contains_target="'),
            ('IsBound="', 'is_bound="'),
            ('String="', 'string="'),
            ('Alias="', 'alias="'),
            ('AppliesTo="', 'applies_to="'),
            ('IsComposable="', 'is_composable="'),
            ('Opentype="', 'open_type="'),
            ('IsFlags="', 'is_flags="'),
            ('Action="', 'action="'),
            ('Value="', 'value="'),
            #
            # Types
            ("Edm.Guid", "uuid"),
            ("Edm.Int64", "int"),
            ("Edm.Int32", "int"),
            ("Edm.Int16", "int"),
            ("Edm.Decimal", "float"),
            ("Edm.Double", "float"),
            ("Edm.Boolean", "bool"),
            ("Edm.Binary", "bytes"),
            ("Edm.DateTimeOffset", "datetime"),
            ("Edm.Date", "date"),
            ("Edm.String", "str"),
        ]

        for new, old in to_replace:
            xml_prettyfied = xml_prettyfied.replace(new, old)

        return xml_prettyfied

    def reset_query(self):
        """Resets the query options and table selection."""
        self._select = ""
        self._expand = ""
        self._top = ""
        self._filter = ""
        self._orderby = ""
        self._count = ""

        self._table = ""
        self._row_id = ""
        self._add_ref_to_property = ""

        self.headers = {}

    def compile_query_options(self) -> str:
        query_options = "&".join(
            [
                statement
                for statement in [
                    self._expand,
                    self._select,
                    self._filter,
                    self._top,
                    self._count,
                    self._orderby,
                ]
                if statement
            ]
        )

        return f"?{query_options}" if query_options else ""

    def set_default_headers(self, operation: method_type):
        self.headers.setdefault("OData-MaxVersion", "4.0")
        self.headers.setdefault("OData-Version", "4.0")
        self.headers.setdefault("Accept", "application/json; odata.metadata=minimal")

        if operation in ["post", "patch", "delete"]:
            self.headers.setdefault("Content-Type", "application/json; charset=utf-8")

        if operation in ["post", "patch"]:
            self.headers.setdefault("Prefer", "return=representation")
            self.headers.setdefault("MSCRM.SuppressDuplicateDetection", "false")

        if operation in ["patch"]:
            self.headers.setdefault("If-None-Match", "null")
            self.headers.setdefault("If-Match", "*")

    @staticmethod
    def error_handling(status_code: int, error_message: str, method: method_type):
        """Error handling based on these expected error statuses:
        https://docs.microsoft.com/en-us/powerapps/developer/data-platform/webapi/compose-http-requests-handle-errors#identify-status-codes
        """

        if status_code == status.HTTP_400_BAD_REQUEST:
            raise ParseError(message=error_message)
        elif status_code == status.HTTP_401_UNAUTHORIZED:
            raise AuthenticationFailed(message=error_message)
        elif status_code == status.HTTP_403_FORBIDDEN:
            raise PermissionDenied(message=error_message)
        elif status_code == status.HTTP_404_NOT_FOUND:
            raise NotFound(message=error_message)
        elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            raise MethodNotAllowed(method=method, message=error_message)
        elif status_code == status.HTTP_412_PRECONDITION_FAILED:
            raise DuplicateRecordError(message=error_message)
        elif status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            raise PayloadTooLarge(message=error_message)
        elif status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise APILimitsExceeded(message=error_message)
        elif status_code == status.HTTP_501_NOT_IMPLEMENTED:
            raise OperationNotImplemented(message=error_message)
        elif status_code == status.HTTP_503_SERVICE_UNAVAILABLE:
            raise WebAPIUnavailable(message=error_message)
        else:
            raise DynamicsException(message=error_message)

    def GET(self, next_link: Optional[str] = None) -> List[Dict[str, Any]]:
        """Make a request to the Dataverse API with currently added query options.

        :param next_link: Request the next set of records from this link instead.
        :raises ValueError: API fetch failed or no data in request.
        """

        self.set_default_headers("get")

        if next_link is not None:
            response = self.api.get(next_link, headers=self.headers)
        else:
            response = self.api.get(self.current_query, headers=self.headers)

        data = response.json()

        # [sic] Separate cases where 'row_id' is provided,
        # without breaking query_dynamics (which puts everything in self.table)
        entities = [data] if "@odata.etag" in data else data.get("value")
        errors = data.get("error")
        count = data.get("@odata.count", "")

        if not errors and not entities:
            message = "No records matching the given criteria."
            self.error_handling(status.HTTP_404_NOT_FOUND, message, method="get")

        if errors:
            self.error_handling(response.status_code, errors["message"], method="get")

        # Fetch more data if needed
        for i, row in enumerate(entities):
            for column_key in list(row.keys()):
                if "@odata.nextLink" in column_key:

                    # TODO: Remove later?, in UAT there is some bad links(?) which have to be skipped.
                    key = column_key[:-15]
                    if not entities[i][key]:
                        continue

                    # When fetching the next page of results, it can include the last
                    # page of data as well, so we filter those out. Although, This doesn't seem
                    # to be the intended way this should work, based on this:
                    #
                    # https://docs.microsoft.com/en-us/powerapps/developer/data-platform/
                    # webapi/query-data-web-api#limits-on-number-of-entities-returned
                    #
                    extra = self.GET(next_link=row.pop(column_key))
                    id_tags = [value["@odata.etag"] for value in entities[i][key]]
                    extra = [value for value in extra if value["@odata.etag"] not in id_tags]

                    entities[i][key] += extra

        if count:
            entities.insert(0, count)

        return entities

    def POST(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new row in a table.
        Must have 'table' attribute set.
        Use expand and select to reduce returned data.
        """

        self.set_default_headers("post")

        # [sic] POSTing data in dict form doesn't work for some reason...
        data = json.dumps(data).encode()
        response = self.api.post(self.current_query, data=data, headers=self.headers)
        data = response.json()

        if errors := data.get("error"):
            self.error_handling(response.status_code, errors["message"], method="post")

        return data

    def PATCH(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update row in a table.
        Must have 'table' and 'row_id' attributes set.
        Use expand and select to reduce returned data.
        """

        self.set_default_headers("patch")

        data = json.dumps(data).encode()
        response = self.api.patch(self.current_query, data=data, headers=self.headers)
        data = response.json()

        if errors := data.get("error"):
            self.error_handling(response.status_code, errors["message"], method="patch")

        return data

    def DELETE(self):
        """Delete row in a table.
        Must have 'table' and 'row_id' attributes set.
        """

        self.set_default_headers("delete")

        response = self.api.delete(self.current_query, headers=self.headers)

        try:
            data = response.json()

            if errors := data.get("error"):
                self.error_handling(response.status_code, errors["message"], method="delete")

        except json.JSONDecodeError:
            pass  # no errors, no response data

    @property
    def table(self) -> str:
        """Table to search in."""
        return self._table

    @table.setter
    def table(self, value: str):
        self._table = value

    @property
    def row_id(self) -> str:
        """Search only from the row with this id. If the table supports other row id's,
        you can use 'foo=bar' or 'foo=bar,fizz=buzz' to filter by them,
        but using the 'filter' query option is recommended.
        """
        return self._row_id

    @row_id.setter
    def row_id(self, value: str):
        self._row_id = value

    @property
    def add_ref_to_property(self) -> str:
        """Add reference for this navigation property. This indicates,
        that POST data will contain the API url to a matching rowid
        in the table this navigation property is meant to link to,
        like this: "@odata.id": "<API URI>/<table>(<id>)".

        This should only be used to link existing rows. Adding references
        for new rows can be done on create with this in POST data:
        "<nav_property>@odata.bind": "/<table>(<id>)".

        Note that query options cannot be used and will not be added
        to the query if this property is set.
        """
        return self._add_ref_to_property

    @add_ref_to_property.setter
    def add_ref_to_property(self, value: str):
        self._add_ref_to_property = value

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
    def select(self) -> str:
        """Get current $select statement"""
        return self._select

    @select.setter
    def select(self, items: List[str]):
        """Set $select statement. Limits the properties returned from the current entity.
        Use expand to limit properties in related items
        """
        self._select = "$select=" + ",".join([key for key in items])

    @property
    def expand(self) -> str:
        """Get current $expand statement"""
        return self._expand

    def _nested_commands(self, name: expand_keys, values: expand_values) -> str:

        assert name in (
            "expand",
            "select",
            "top",
            "filter",
            "orderby",
        ), f"'{name}' is not a valid command!"

        if name == "select":
            return "$select=" + ",".join([key for key in values])

        elif name == "filter":
            return "$filter=" + " and ".join([key.strip() for key in values])

        elif name == "orderby":
            return f"$orderby=" + ",".join([f"{key} {order}" for key, order in values.items()])

        elif name == "top":
            return f"$top={values}"

        else:  # nested expand
            return self._recursive_expand(values)

    def _recursive_expand(self, items: Dict[str, Optional[expand_subcommands]]) -> str:
        return "$expand=" + ",".join(
            [
                f"{key}(" + ";".join([self._nested_commands(name, values) for name, values in value.items()]) + f")"
                if value
                else f"{key}"
                for key, value in items.items()
            ]
        )

    @expand.setter
    def expand(self, items: Dict[str, Optional[expand_subcommands]]):
        """Set $expand statement, with possible nested statements.
        Controls what data from related entities is returned.

        Keys in 'items' indicate entities to expand.
        Values in 'items' set to None expands to everything *immidiately* under that entity.

        Otherwise, values in 'items' is a dict, which contains the statements inside the expand statement.
        Valid keys for these are 'select', 'filter', 'top', 'orderby', and 'expand'.
        Values under these keys should be constructed in the same manner as they are
        when outside the expand statement, e.g. 'select' takes a List[str], 'top' an int, etc.

        A nested expand statement takes another similar dict to 'items',
        but it has some limitations (WEB API v9.1):

        1. Nested expand statements can *only* be applied to **many-to-one/single-valued** relationships.
        This means nested expands for collections do not work!

        2. Each request can include a maximum of 10 expand statements.
        This applies to non-nested statements as well! There is no limit on the depth of nested
        expand statements, so long as the total is 10.
        """

        self._expand = self._recursive_expand(items)

    @property
    def filter(self) -> str:
        """Get current $filter statement"""
        return self._filter

    @filter.setter
    def filter(self, items: Union[Set[str], List[str]]):
        """Set $filter statement. Sets the criteria for which entities will be returned.

        Input a list-object to 'and' the items. Input a set-object to 'or' the items.

        Below is a list of the standard operators. ":func:`dynamics.ftr`" object can be used to create these,
        and a bunch of special operators. All filter conditions for string values are case insensitive.

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
        """

        if isinstance(items, set):
            self._filter = "$filter=" + " or ".join([key.strip() for key in items])
        elif isinstance(items, list):
            self._filter = "$filter=" + " and ".join([key.strip() for key in items])
        else:
            raise TypeError("Filter items must be either a set or a list.")

    @property
    def top(self) -> str:
        """Get current $top statement"""
        return self._top

    @top.setter
    def top(self, number: int):
        """Set $top statement. Limits the number of results returned.
        Note: You should not use 'top' with 'count'.
        """
        self._top = f"$top={number}"

    @property
    def orderby(self) -> str:
        """Get current $orderby statement"""
        return self._orderby

    @orderby.setter
    def orderby(self, items: orderby_type):
        """Set $orderby statement. Specifies the order in which items are returned."""
        self._orderby = f"$orderby=" + ",".join([f"{key} {order}" for key, order in items.items()])

    @property
    def count(self) -> str:
        """Get current $count statement"""
        return self._count

    @count.setter
    def count(self, value: bool):
        """Set $count statement. Include the count of entities that match the filter criteria in the results.
        Count will be the first item in the list of results.
        Note: You should not use 'count' with 'top'.
        """
        self._count = f"$count=true" if value else ""

    # TODO: apply-statement
    # TODO: Any and all statements
