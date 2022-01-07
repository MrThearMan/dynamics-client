import os
from unittest import mock

import pytest

from dynamics.client import DynamicsClient
from dynamics.exceptions import (
    APILimitsExceeded,
    AuthenticationFailed,
    DuplicateRecordError,
    DynamicsException,
    MethodNotAllowed,
    NotFound,
    OperationNotImplemented,
    ParseError,
    PayloadTooLarge,
    PermissionDenied,
    WebAPIUnavailable,
)
from dynamics.test import ClientResponse, ResponseMock, dynamics_client_response
from dynamics.typing import MethodType


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(data={"foo": "bar", "one": 2}, status_code=200),
            method="get",
            client_response=[{"foo": "bar", "one": 2}],
        ),
        ClientResponse(
            session_response=ResponseMock(data={"value": []}, status_code=204),
            method="get",
            client_response=[],
        ),
        ClientResponse(
            session_response=ResponseMock(data={"value": [{"foo": "bar"}, {"one": 2}]}, status_code=204),
            method="get",
            client_response=[{"foo": "bar"}, {"one": 2}],
        ),
    ],
    indirect=True,
)
def test_client_get_request(dynamics_client):
    assert dynamics_client.get(not_found_ok=True) == dynamics_client._output_


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(data={"value": []}, status_code=404),
            method="get",
            client_response=NotFound,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a ParseError"}},
                status_code=400,
            ),
            method="get",
            client_response=ParseError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a AuthenticationFailed"}},
                status_code=401,
            ),
            method="get",
            client_response=AuthenticationFailed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a PermissionDenied"}},
                status_code=403,
            ),
            method="get",
            client_response=PermissionDenied,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a NotFound"}},
                status_code=404,
            ),
            method="get",
            client_response=NotFound,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a MethodNotAllowed"}},
                status_code=405,
            ),
            method="get",
            client_response=MethodNotAllowed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a DuplicateRecordError"}},
                status_code=412,
            ),
            method="get",
            client_response=DuplicateRecordError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a PayloadTooLarge"}},
                status_code=413,
            ),
            method="get",
            client_response=PayloadTooLarge,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a APILimitsExceeded"}},
                status_code=429,
            ),
            method="get",
            client_response=APILimitsExceeded,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a DynamicsException"}},
                status_code=500,
            ),
            method="get",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a OperationNotImplemented"}},
                status_code=501,
            ),
            method="get",
            client_response=OperationNotImplemented,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"value": [], "error": {"message": "This is a WebAPIUnavailable"}},
                status_code=503,
            ),
            method="get",
            client_response=WebAPIUnavailable,
        ),
    ],
    indirect=True,
)
def test_client_get_request__errors(dynamics_client):
    with pytest.raises(dynamics_client._output_) as exc_info:
        dynamics_client.get()
    nf_message = "No records matching the given criteria."
    assert dynamics_client._input_.data.get("error", {}).get("message", nf_message) == exc_info.value.args[0]


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(data={"foo": "bar", "one": 2}, status_code=200),
            method="post",
            client_response={"foo": "bar", "one": 2},
        ),
        ClientResponse(
            session_response=ResponseMock(data={"foo": "bar", "one": 2}, status_code=204),
            method="post",
            client_response={},
        ),
    ],
    indirect=True,
)
def test_client_post_request(dynamics_client):
    assert dynamics_client.post(data=dynamics_client._input_.data) == dynamics_client._output_


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a ParseError"}},
                status_code=400,
            ),
            method="post",
            client_response=ParseError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a AuthenticationFailed"}},
                status_code=401,
            ),
            method="post",
            client_response=AuthenticationFailed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a PermissionDenied"}},
                status_code=403,
            ),
            method="post",
            client_response=PermissionDenied,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a NotFound"}},
                status_code=404,
            ),
            method="post",
            client_response=NotFound,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a MethodNotAllowed"}},
                status_code=405,
            ),
            method="post",
            client_response=MethodNotAllowed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a DuplicateRecordError"}},
                status_code=412,
            ),
            method="post",
            client_response=DuplicateRecordError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a PayloadTooLarge"}},
                status_code=413,
            ),
            method="post",
            client_response=PayloadTooLarge,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a APILimitsExceeded"}},
                status_code=429,
            ),
            method="post",
            client_response=APILimitsExceeded,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a DynamicsException"}},
                status_code=500,
            ),
            method="post",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a OperationNotImplemented"}},
                status_code=501,
            ),
            method="post",
            client_response=OperationNotImplemented,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a WebAPIUnavailable"}},
                status_code=503,
            ),
            method="post",
            client_response=WebAPIUnavailable,
        ),
    ],
    indirect=True,
)
def test_client_post_request__errors(dynamics_client):
    with pytest.raises(dynamics_client._output_) as exc_info:
        dynamics_client.post({})

    assert dynamics_client._input_.data.get("error", {}).get("message") == exc_info.value.args[0]


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(data={"foo": "bar", "one": 2}, status_code=200),
            method="patch",
            client_response={"foo": "bar", "one": 2},
        ),
        ClientResponse(
            session_response=ResponseMock(data={"foo": "bar", "one": 2}, status_code=204),
            method="patch",
            client_response={},
        ),
    ],
    indirect=True,
)
def test_client_patch_request(dynamics_client):
    assert dynamics_client.patch(data=dynamics_client._input_.data) == dynamics_client._output_


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a ParseError"}},
                status_code=400,
            ),
            method="patch",
            client_response=ParseError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a AuthenticationFailed"}},
                status_code=401,
            ),
            method="patch",
            client_response=AuthenticationFailed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a PermissionDenied"}},
                status_code=403,
            ),
            method="patch",
            client_response=PermissionDenied,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a NotFound"}},
                status_code=404,
            ),
            method="patch",
            client_response=NotFound,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a MethodNotAllowed"}},
                status_code=405,
            ),
            method="patch",
            client_response=MethodNotAllowed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a DuplicateRecordError"}},
                status_code=412,
            ),
            method="patch",
            client_response=DuplicateRecordError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a PayloadTooLarge"}},
                status_code=413,
            ),
            method="patch",
            client_response=PayloadTooLarge,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a APILimitsExceeded"}},
                status_code=429,
            ),
            method="patch",
            client_response=APILimitsExceeded,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a DynamicsException"}},
                status_code=500,
            ),
            method="patch",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a OperationNotImplemented"}},
                status_code=501,
            ),
            method="patch",
            client_response=OperationNotImplemented,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a WebAPIUnavailable"}},
                status_code=503,
            ),
            method="patch",
            client_response=WebAPIUnavailable,
        ),
    ],
    indirect=True,
)
def test_client_patch_request__errors(dynamics_client):
    with pytest.raises(dynamics_client._output_) as exc_info:
        dynamics_client.patch({})

    assert dynamics_client._input_.data.get("error", {}).get("message") == exc_info.value.args[0]


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(data={"foo": "bar", "one": 2}, status_code=200),
            method="delete",
            client_response=None,
        ),
        ClientResponse(
            session_response=ResponseMock(data={"foo": "bar", "one": 2}, status_code=204),
            method="delete",
            client_response=None,
        ),
    ],
    indirect=True,
)
def test_client_delete_request(dynamics_client):
    assert dynamics_client.delete() == dynamics_client._output_


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a ParseError"}},
                status_code=400,
            ),
            method="delete",
            client_response=ParseError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a AuthenticationFailed"}},
                status_code=401,
            ),
            method="delete",
            client_response=AuthenticationFailed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a PermissionDenied"}},
                status_code=403,
            ),
            method="delete",
            client_response=PermissionDenied,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a NotFound"}},
                status_code=404,
            ),
            method="delete",
            client_response=NotFound,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a MethodNotAllowed"}},
                status_code=405,
            ),
            method="delete",
            client_response=MethodNotAllowed,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a DuplicateRecordError"}},
                status_code=412,
            ),
            method="delete",
            client_response=DuplicateRecordError,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a PayloadTooLarge"}},
                status_code=413,
            ),
            method="delete",
            client_response=PayloadTooLarge,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a APILimitsExceeded"}},
                status_code=429,
            ),
            method="delete",
            client_response=APILimitsExceeded,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a DynamicsException"}},
                status_code=500,
            ),
            method="delete",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a OperationNotImplemented"}},
                status_code=501,
            ),
            method="delete",
            client_response=OperationNotImplemented,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"error": {"message": "This is a WebAPIUnavailable"}},
                status_code=503,
            ),
            method="delete",
            client_response=WebAPIUnavailable,
        ),
    ],
    indirect=True,
)
def test_client_delete_request__errors(dynamics_client):
    with pytest.raises(dynamics_client._output_) as exc_info:
        dynamics_client.delete()

    assert dynamics_client._input_.data.get("error", {}).get("message") == exc_info.value.args[0]


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
        session_response=ResponseMock(data={"@odata.count": 1, "value": [{"foo": "bar"}]}, status_code=200),
        method="get",
        client_response=[1, {"foo": "bar"}],
    ):
        assert dynamics_client.get() == dynamics_client._output_  # noqa


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


def test_client_get_next_page__before_pagesize_reached(dynamics_client):
    with dynamics_client_response(
        dynamics_client,
        session_response=ResponseMock(
            data={"foo": ["bar"], "foo@odata.nextLink": "link-to-next-page"},
            status_code=200,
        ),
        method="get",
        client_response=[{"foo": ["bar"]}],
    ):
        assert dynamics_client.get() == dynamics_client._output_  # noqa


def test_client_get_next_page__over_pagesize(dynamics_client):
    dynamics_client.pagesize = 1

    with dynamics_client_response(
        dynamics_client,
        session_response=[
            ResponseMock(
                data={"foo": [{"@odata.etag": "12345", "bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"},
                status_code=200,
            ),
            ResponseMock(
                data={"@odata.etag": "23456", "fizz": "buzz"},
                status_code=200,
            ),
        ],
        method="get",
        client_response=[
            {
                "foo": [
                    {"@odata.etag": "12345", "bar": "baz"},
                    {"@odata.etag": "23456", "fizz": "buzz"},
                ],
            },
        ],
    ):
        assert dynamics_client.get() == dynamics_client._output_  # noqa


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="get",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="post",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="patch",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="delete",
            client_response=DynamicsException,
        ),
    ],
    indirect=True,
)
def test_client_simplify_errors(dynamics_client):
    with pytest.raises(dynamics_client._output_) as exc_info:
        if dynamics_client._method_ == "get":
            dynamics_client.get(simplify_errors=True)
        elif dynamics_client._method_ == "post":
            dynamics_client.post({}, simplify_errors=True)
        elif dynamics_client._method_ == "patch":
            dynamics_client.patch({}, simplify_errors=True)
        elif dynamics_client._method_ == "delete":
            dynamics_client.delete(simplify_errors=True)

    assert exc_info.value.args[0] == dynamics_client.simplified_error_message


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="get",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=TypeError("Unexpected Error!"),
            method="get",
            client_response=TypeError,
        ),
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="post",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=TypeError("Unexpected Error!"),
            method="post",
            client_response=TypeError,
        ),
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="patch",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=TypeError("Unexpected Error!"),
            method="patch",
            client_response=TypeError,
        ),
        ClientResponse(
            session_response=ValueError("Unexpected Error!"),
            method="delete",
            client_response=DynamicsException,
        ),
        ClientResponse(
            session_response=TypeError("Unexpected Error!"),
            method="delete",
            client_response=TypeError,
        ),
    ],
    indirect=True,
)
def test_client_simplify_errors__raise_separately(dynamics_client):
    with pytest.raises(dynamics_client._output_) as exc_info:
        if dynamics_client._method_ == "get":
            dynamics_client.get(simplify_errors=True, raise_separately=[TypeError])
        elif dynamics_client._method_ == "post":
            dynamics_client.post({}, simplify_errors=True, raise_separately=[TypeError])
        elif dynamics_client._method_ == "patch":
            dynamics_client.patch({}, simplify_errors=True, raise_separately=[TypeError])
        elif dynamics_client._method_ == "delete":
            dynamics_client.delete(simplify_errors=True, raise_separately=[TypeError])

    msg = dynamics_client._input_.args[0]
    if issubclass(dynamics_client._output_, DynamicsException):
        msg = dynamics_client.simplified_error_message

    assert exc_info.value.args[0] == msg


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=[
                ResponseMock(
                    data={"foo": "bar"},
                    status_code=200,
                ),
                ResponseMock(
                    data={"foo": "baz"},
                    status_code=200,
                ),
            ],
            method="get",
            client_response=DynamicsException,
        ),
    ],
    indirect=True,
)
def test_client_request_counter(dynamics_client):
    assert dynamics_client.request_counter == 0
    dynamics_client.get()
    assert dynamics_client.request_counter == 1
    dynamics_client.get()
    assert dynamics_client.request_counter == 2


def test_client_reset_query(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.row_id = "row"
    dynamics_client.action = "action"
    dynamics_client.select = ["foo", "bar"]
    dynamics_client.add_ref_to_property = "foo"
    dynamics_client.pre_expand = "fizzbuzz"
    dynamics_client.show_annotations = True
    dynamics_client.filter = {"foo", "bar"}
    dynamics_client.expand = {"foo": {"select": ["bar", "baz"], "filter": ["fizz", "buzz"]}}
    dynamics_client.apply = "statement"
    dynamics_client.top = 2
    dynamics_client.orderby = {"foo": "asc"}
    dynamics_client.count = True
    dynamics_client["foo"] = "bar"

    # Not overridden
    dynamics_client.pagesize = 2000

    assert dynamics_client.current_query != "/"
    assert "foo" in dynamics_client.headers
    assert dynamics_client.pagesize == 2000

    dynamics_client.reset_query()

    assert dynamics_client.current_query == "/"
    assert "foo" not in dynamics_client.headers
    assert dynamics_client.pagesize == 2000


@pytest.mark.parametrize(
    "dynamics_client",
    [
        ClientResponse(
            session_response=ResponseMock(
                data={"foo": "bar"},
                status_code=200,
            ),
            method="get",
            client_response=None,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"foo": "bar"},
                status_code=200,
            ),
            method="post",
            client_response=None,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"foo": "bar"},
                status_code=200,
            ),
            method="patch",
            client_response=None,
        ),
        ClientResponse(
            session_response=ResponseMock(
                data={"foo": "bar"},
                status_code=200,
            ),
            method="delete",
            client_response=None,
        ),
    ],
    indirect=True,
)
def test_client_headers_are_set_on_call(dynamics_client):
    with mock.patch(
        "dynamics.client.DynamicsClient.set_default_headers",
        side_effect=dynamics_client.set_default_headers,
    ) as patch:
        if dynamics_client._method_ == "get":
            dynamics_client.get()
        elif dynamics_client._method_ == "post":
            dynamics_client.post({})
        elif dynamics_client._method_ == "patch":
            dynamics_client.patch({})
        elif dynamics_client._method_ == "delete":
            dynamics_client.delete()

    patch.assert_called_once()
