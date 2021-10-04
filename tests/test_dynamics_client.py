import os
from unittest import mock

import pytest

from dynamics.client import DynamicsClient
from dynamics.exceptions import (
    APILimitsExceeded,
    AuthenticationFailed,
    DuplicateRecordError,
    MethodNotAllowed,
    NotFound,
    OperationNotImplemented,
    ParseError,
    PayloadTooLarge,
    PermissionDenied,
    WebAPIUnavailable,
)
from dynamics.typing import MethodType
from dynamics.utils import cache

from .conftest import ClientResponse, dynamics_client_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"foo": "bar", "one": 2},
            method="get",
            response=[{"foo": "bar", "one": 2}],
            status_code=200,
        ),
        ClientResponse(
            request={"value": []},
            method="get",
            response=[],
            status_code=204,
        ),
        ClientResponse(
            request={"value": [{"foo": "bar"}, {"one": 2}]},
            method="get",
            response=[{"foo": "bar"}, {"one": 2}],
            status_code=204,
        ),
    ],
    indirect=True,
)
def test_client_get_request(dynamics_client):
    assert dynamics_client.get(not_found_ok=True) == dynamics_client.expected_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"value": []},
            method="get",
            response=NotFound,
            status_code=404,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a ParseError"}},
            method="get",
            response=ParseError,
            status_code=400,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a AuthenticationFailed"}},
            method="get",
            response=AuthenticationFailed,
            status_code=401,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a PermissionDenied"}},
            method="get",
            response=PermissionDenied,
            status_code=403,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a NotFound"}},
            method="get",
            response=NotFound,
            status_code=404,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a MethodNotAllowed"}},
            method="get",
            response=MethodNotAllowed,
            status_code=405,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a DuplicateRecordError"}},
            method="get",
            response=DuplicateRecordError,
            status_code=412,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a PayloadTooLarge"}},
            method="get",
            response=PayloadTooLarge,
            status_code=413,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a APILimitsExceeded"}},
            method="get",
            response=APILimitsExceeded,
            status_code=429,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a OperationNotImplemented"}},
            method="get",
            response=OperationNotImplemented,
            status_code=501,
        ),
        ClientResponse(
            request={"value": [], "error": {"message": "This is a WebAPIUnavailable"}},
            method="get",
            response=WebAPIUnavailable,
            status_code=503,
        ),
    ],
    indirect=True,
)
def test_client_get_request__errors(dynamics_client):
    with pytest.raises(dynamics_client.expected_response) as exc_info:
        dynamics_client.get()
    nf_message = "No records matching the given criteria."
    assert dynamics_client.this_request.get("error", {}).get("message", nf_message) == exc_info.value.args[0]


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"foo": "bar", "one": 2},
            method="post",
            response={"foo": "bar", "one": 2},
            status_code=200,
        ),
        ClientResponse(
            request={"foo": "bar", "one": 2},
            method="post",
            response={},
            status_code=204,
        ),
    ],
    indirect=True,
)
def test_client_post_request(dynamics_client):
    assert dynamics_client.post(data=dynamics_client.this_request) == dynamics_client.expected_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"error": {"message": "This is a ParseError"}},
            method="post",
            response=ParseError,
            status_code=400,
        ),
        ClientResponse(
            request={"error": {"message": "This is a AuthenticationFailed"}},
            method="post",
            response=AuthenticationFailed,
            status_code=401,
        ),
        ClientResponse(
            request={"error": {"message": "This is a PermissionDenied"}},
            method="post",
            response=PermissionDenied,
            status_code=403,
        ),
        ClientResponse(
            request={"error": {"message": "This is a NotFound"}},
            method="post",
            response=NotFound,
            status_code=404,
        ),
        ClientResponse(
            request={"error": {"message": "This is a MethodNotAllowed"}},
            method="post",
            response=MethodNotAllowed,
            status_code=405,
        ),
        ClientResponse(
            request={"error": {"message": "This is a DuplicateRecordError"}},
            method="post",
            response=DuplicateRecordError,
            status_code=412,
        ),
        ClientResponse(
            request={"error": {"message": "This is a PayloadTooLarge"}},
            method="post",
            response=PayloadTooLarge,
            status_code=413,
        ),
        ClientResponse(
            request={"error": {"message": "This is a APILimitsExceeded"}},
            method="post",
            response=APILimitsExceeded,
            status_code=429,
        ),
        ClientResponse(
            request={"error": {"message": "This is a OperationNotImplemented"}},
            method="post",
            response=OperationNotImplemented,
            status_code=501,
        ),
        ClientResponse(
            request={"error": {"message": "This is a WebAPIUnavailable"}},
            method="post",
            response=WebAPIUnavailable,
            status_code=503,
        ),
    ],
    indirect=True,
)
def test_client_post_request__errors(dynamics_client):
    with pytest.raises(dynamics_client.expected_response) as exc_info:
        dynamics_client.post({})

    assert dynamics_client.this_request.get("error", {}).get("message") == exc_info.value.args[0]


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"foo": "bar", "one": 2},
            method="patch",
            response={"foo": "bar", "one": 2},
            status_code=200,
        ),
        ClientResponse(
            request={"foo": "bar", "one": 2},
            method="patch",
            response={},
            status_code=204,
        ),
    ],
    indirect=True,
)
def test_client_patch_request(dynamics_client):
    assert dynamics_client.patch(data=dynamics_client.this_request) == dynamics_client.expected_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"error": {"message": "This is a ParseError"}},
            method="patch",
            response=ParseError,
            status_code=400,
        ),
        ClientResponse(
            request={"error": {"message": "This is a AuthenticationFailed"}},
            method="patch",
            response=AuthenticationFailed,
            status_code=401,
        ),
        ClientResponse(
            request={"error": {"message": "This is a PermissionDenied"}},
            method="patch",
            response=PermissionDenied,
            status_code=403,
        ),
        ClientResponse(
            request={"error": {"message": "This is a NotFound"}},
            method="patch",
            response=NotFound,
            status_code=404,
        ),
        ClientResponse(
            request={"error": {"message": "This is a MethodNotAllowed"}},
            method="patch",
            response=MethodNotAllowed,
            status_code=405,
        ),
        ClientResponse(
            request={"error": {"message": "This is a DuplicateRecordError"}},
            method="patch",
            response=DuplicateRecordError,
            status_code=412,
        ),
        ClientResponse(
            request={"error": {"message": "This is a PayloadTooLarge"}},
            method="patch",
            response=PayloadTooLarge,
            status_code=413,
        ),
        ClientResponse(
            request={"error": {"message": "This is a APILimitsExceeded"}},
            method="patch",
            response=APILimitsExceeded,
            status_code=429,
        ),
        ClientResponse(
            request={"error": {"message": "This is a OperationNotImplemented"}},
            method="patch",
            response=OperationNotImplemented,
            status_code=501,
        ),
        ClientResponse(
            request={"error": {"message": "This is a WebAPIUnavailable"}},
            method="patch",
            response=WebAPIUnavailable,
            status_code=503,
        ),
    ],
    indirect=True,
)
def test_client_patch_request__errors(dynamics_client):
    with pytest.raises(dynamics_client.expected_response) as exc_info:
        dynamics_client.patch({})

    assert dynamics_client.this_request.get("error", {}).get("message") == exc_info.value.args[0]


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"foo": "bar", "one": 2},
            method="delete",
            response=None,
            status_code=200,
        ),
        ClientResponse(
            request={"foo": "bar", "one": 2},
            method="delete",
            response=None,
            status_code=204,
        ),
    ],
    indirect=True,
)
def test_client_delete_request(dynamics_client):
    assert dynamics_client.delete() == dynamics_client.expected_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            request={"error": {"message": "This is a ParseError"}},
            method="delete",
            response=ParseError,
            status_code=400,
        ),
        ClientResponse(
            request={"error": {"message": "This is a AuthenticationFailed"}},
            method="delete",
            response=AuthenticationFailed,
            status_code=401,
        ),
        ClientResponse(
            request={"error": {"message": "This is a PermissionDenied"}},
            method="delete",
            response=PermissionDenied,
            status_code=403,
        ),
        ClientResponse(
            request={"error": {"message": "This is a NotFound"}},
            method="delete",
            response=NotFound,
            status_code=404,
        ),
        ClientResponse(
            request={"error": {"message": "This is a MethodNotAllowed"}},
            method="delete",
            response=MethodNotAllowed,
            status_code=405,
        ),
        ClientResponse(
            request={"error": {"message": "This is a DuplicateRecordError"}},
            method="delete",
            response=DuplicateRecordError,
            status_code=412,
        ),
        ClientResponse(
            request={"error": {"message": "This is a PayloadTooLarge"}},
            method="delete",
            response=PayloadTooLarge,
            status_code=413,
        ),
        ClientResponse(
            request={"error": {"message": "This is a APILimitsExceeded"}},
            method="delete",
            response=APILimitsExceeded,
            status_code=429,
        ),
        ClientResponse(
            request={"error": {"message": "This is a OperationNotImplemented"}},
            method="delete",
            response=OperationNotImplemented,
            status_code=501,
        ),
        ClientResponse(
            request={"error": {"message": "This is a WebAPIUnavailable"}},
            method="delete",
            response=WebAPIUnavailable,
            status_code=503,
        ),
    ],
    indirect=True,
)
def test_client_delete_request__errors(dynamics_client):
    with pytest.raises(dynamics_client.expected_response) as exc_info:
        dynamics_client.delete()

    assert dynamics_client.this_request.get("error", {}).get("message") == exc_info.value.args[0]


@pytest.mark.parametrize(
    "method,headers",
    [
        [
            "get",
            {
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json; odata.metadata=minimal",
                "Prefer": "odata.maxpagesize=5000",
            },
        ],
        [
            "post",
            {
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json; odata.metadata=minimal",
                "Content-Type": "application/json; charset=utf-8",
                "Prefer": "return=representation",
                "MSCRM.SuppressDuplicateDetection": "false",
            },
        ],
        [
            "patch",
            {
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json; odata.metadata=minimal",
                "Content-Type": "application/json; charset=utf-8",
                "Prefer": "return=representation",
                "MSCRM.SuppressDuplicateDetection": "false",
                "If-None-Match": "null",
                "If-Match": "*",
            },
        ],
        [
            "delete",
            {
                "OData-MaxVersion": "4.0",
                "OData-Version": "4.0",
                "Accept": "application/json; odata.metadata=minimal",
                "Content-Type": "application/json; charset=utf-8",
                "Prefer": "odata.maxpagesize=5000",
            },
        ],
    ],
)
def test_client_set_default_headers(dynamics_client, method: MethodType, headers: dict):
    dynamics_client.set_default_headers(method=method)
    assert dynamics_client.headers == headers


def test_client_headers(dynamics_client):
    assert dynamics_client.headers == {}
    dynamics_client["Accept"] = "application/json"
    assert dynamics_client["Accept"] == "application/json"


def test_client_init_from_environment():
    os.environ["DYNAMICS_API_URL"] = "apiurl"
    os.environ["DYNAMICS_TOKEN_URL"] = "tokenurl"
    os.environ["DYNAMICS_CLIENT_ID"] = "clientid"
    os.environ["DYNAMICS_CLIENT_SECRET"] = "secret"
    os.environ["DYNAMICS_SCOPE"] = "scope"

    try:
        client = DynamicsClient.from_environment()
    except KeyError as error:
        pytest.fail(f"Wrong environment variables: {error}")
        return

    assert client._api_url == "apiurl/"
    assert client._session._client.client_id == "clientid"


def test_client_init_from_cache():
    with mock.patch("dynamics.utils.SQLiteCache.get", mock.MagicMock(return_value="token")):
        client = DynamicsClient("", "", "", "", [])

    assert client._session.token == "token"

    cache.set("dynamics-client-token", None)


def test_client_query__table(dynamics_client):
    dynamics_client.table = "table"
    assert dynamics_client.table == "table"
    assert dynamics_client.current_query == "/table"


def test_client_query__row_id(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.row_id = "row_id"
    assert dynamics_client.row_id == "row_id"
    assert dynamics_client.current_query == "/table(row_id)"


def test_client_query__add_ref_to_property(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.row_id = "row_id"
    dynamics_client.add_ref_to_property = "property"
    assert dynamics_client.add_ref_to_property == "property"
    assert dynamics_client.current_query == "/table(row_id)/property/$ref"


def test_client_query__pre_expand(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.pre_expand = "foo"
    assert dynamics_client.pre_expand == "foo"
    assert dynamics_client.current_query == "/table/foo"


def test_client_query__action(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.action = "foo"
    assert dynamics_client.action == "foo"
    assert dynamics_client.current_query == "/table/foo"

    dynamics_client.table = ""
    assert dynamics_client.current_query == "/foo"


def test_client_query__select(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.select = ["foo"]
    assert dynamics_client.select == ["foo"]
    assert dynamics_client.current_query == "/table?$select=foo"


def test_client_query__select__multiple(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.select = ["foo", "bar"]
    assert dynamics_client.select == ["foo", "bar"]
    assert dynamics_client.current_query == "/table?$select=foo,bar"


def test_client_query__expand(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": None}
    assert dynamics_client.expand == {"foo": None}
    assert dynamics_client.current_query == "/table?$expand=foo"


def test_client_query__expand__with_select(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"select": ["bar"]}}
    assert dynamics_client.expand == {"foo": {"select": ["bar"]}}
    assert dynamics_client.current_query == "/table?$expand=foo($select=bar)"


def test_client_query__expand__with_select_and_filer(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"select": ["bar"], "filter": ["baz"]}}
    assert dynamics_client.expand == {"foo": {"select": ["bar"], "filter": ["baz"]}}
    assert dynamics_client.current_query == "/table?$expand=foo($select=bar;$filter=baz)"


def test_client_query__expand__with_select_and_filer__multiple(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"select": ["bar", "baz"], "filter": ["fizz", "buzz"]}}
    assert dynamics_client.expand == {"foo": {"select": ["bar", "baz"], "filter": ["fizz", "buzz"]}}
    assert dynamics_client.current_query == "/table?$expand=foo($select=bar,baz;$filter=fizz and buzz)"


def test_client_query__expand__with_all_options(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {
        "foo": {
            "select": ["bar", "baz"],
            "filter": ["fizz", "buzz"],
            "orderby": {"one": "two"},
            "top": 10,
            "expand": {
                "foobar": {
                    "select": ["barbaz"],
                },
            },
        },
    }
    assert dynamics_client.expand == {
        "foo": {
            "select": ["bar", "baz"],
            "filter": ["fizz", "buzz"],
            "orderby": {"one": "two"},
            "top": 10,
            "expand": {
                "foobar": {
                    "select": ["barbaz"],
                },
            },
        },
    }
    assert dynamics_client.current_query == (
        "/table?"
        "$expand=foo("
        "$select=bar,baz;"
        "$filter=fizz and buzz;"
        "$orderby=one two;"
        "$top=10;"
        "$expand=foobar($select=barbaz)"
        ")"
    )


def test_client_query__expand__invalid_option(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"bar": "baz"}}
    assert dynamics_client.expand == {"foo": {"bar": "baz"}}

    with pytest.raises(KeyError) as exc_info:
        a = dynamics_client.current_query

    assert exc_info.value.args[0] == "'bar' is not a valid query inside expand statement!"


def test_client_query__filter(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.filter = ["foo"]
    assert dynamics_client.filter == ["foo"]
    assert dynamics_client.current_query == "/table?$filter=foo"


def test_client_query__filter__empty(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(ValueError) as exc_info:
        dynamics_client.filter = []

    assert exc_info.value.args[0] == "Filter list cannot be empty."


def test_client_query__filter__not_valid_type(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(TypeError) as exc_info:
        dynamics_client.filter = "foo"

    assert exc_info.value.args[0] == "Filter items must be either a set or a list."


def test_client_query__filter__multiple__and(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.filter = ["foo", "bar"]
    assert dynamics_client.filter == ["foo", "bar"]
    assert dynamics_client.current_query == "/table?$filter=foo and bar"


def test_client_query__filter__multiple__or(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.filter = {"foo", "bar"}
    assert dynamics_client.filter == {"foo", "bar"}
    # Since sets are unordered, both can be true
    try:
        assert dynamics_client.current_query == "/table?$filter=foo or bar"
    except AssertionError:
        assert dynamics_client.current_query == "/table?$filter=bar or foo"


def test_client_query__apply(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.apply = "foo"
    assert dynamics_client.apply == "foo"
    assert dynamics_client.current_query == "/table?$apply=foo"


def test_client_query__top(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.top = 1
    assert dynamics_client.top == 1
    assert dynamics_client.current_query == "/table?$top=1"


def test_client_query__orderby(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.orderby = {"foo": "asc"}
    assert dynamics_client.orderby == {"foo": "asc"}
    assert dynamics_client.current_query == "/table?$orderby=foo asc"


def test_client_query__orderby__multiple(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.orderby = {"foo": "asc", "bar": "desc"}
    assert dynamics_client.orderby == {"foo": "asc", "bar": "desc"}
    assert dynamics_client.current_query == "/table?$orderby=foo asc,bar desc"


def test_client_query__orderby__empty(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(ValueError) as exc_info:
        dynamics_client.orderby = {}

    assert exc_info.value.args[0] == "Orderby dict must not be empty."


def test_client_query__orderby__not_valid_type(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(TypeError) as exc_info:
        dynamics_client.orderby = "foo"

    assert exc_info.value.args[0] == "Orderby items must be a dict."


def test_client_query__count(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.count = True
    assert dynamics_client.count is True
    assert dynamics_client.current_query == "/table?$count=true"

    with dynamics_client_response(
        dynamics_client,
        request={"@odata.count": 1, "value": [{"foo": "bar"}]},
        method="get",
        response=[1, {"foo": "bar"}],
        status_code=200,
    ):
        assert dynamics_client.get() == dynamics_client.expected_response  # noqa


def test_client_pagesize(dynamics_client):
    assert dynamics_client.pagesize == 5000
    dynamics_client.pagesize = 2000
    assert dynamics_client.pagesize == 2000

    with pytest.raises(ValueError) as exc_info:
        dynamics_client.pagesize = -10

    assert exc_info.value.args[0] == "Value must be bigger than 0. Got -10."

    with pytest.raises(ValueError) as exc_info:
        dynamics_client.pagesize = 5001

    assert exc_info.value.args[0] == "Max pagesize is 5000. Got 5001."


def test_client_show_annotations(dynamics_client):
    assert dynamics_client.show_annotations is False
    dynamics_client.show_annotations = True
    assert dynamics_client.show_annotations is True
    assert dynamics_client.headers == {"Prefer": 'odata.include-annotations="*"'}
    dynamics_client.show_annotations = False
    assert dynamics_client.headers == {}


def test_client_get_next_page(dynamics_client):
    pass  # TODO: get next page
