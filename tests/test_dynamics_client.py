import os
import re
import sys
from unittest import mock

import pytest
from oauthlib.oauth2 import OAuth2Token
from requests import JSONDecodeError  # noqa

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
from dynamics.test import MockClient, ResponseMock
from dynamics.typing import MethodType


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({"value": []}).with_status_codes(204),
        MockClient().internal.with_responses({"value": [{"foo": "bar"}, {"one": 2}]}).with_status_codes(200),
    ],
    indirect=True,
)
def test_client_get_request(dynamics_client):
    assert dynamics_client.get(not_found_ok=True) == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
def test_client_post_request(dynamics_client):
    assert dynamics_client.post(data={}) == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
def test_client_patch_request(dynamics_client):
    assert dynamics_client.patch(data={}) == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_status_codes(204),
    ],
    indirect=True,
)
def test_client_delete_request(dynamics_client):
    assert dynamics_client.delete() == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient()
        .internal.with_responses({"error": {"message": "This is a ParseError"}}, cycle=True)
        .with_status_codes(400, cycle=True)
        .with_exceptions(ParseError("This is a ParseError")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a AuthenticationFailed"}}, cycle=True)
        .with_status_codes(401, cycle=True)
        .with_exceptions(AuthenticationFailed("This is a AuthenticationFailed")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a PermissionDenied"}}, cycle=True)
        .with_status_codes(403, cycle=True)
        .with_exceptions(PermissionDenied("This is a PermissionDenied")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a NotFound"}}, cycle=True)
        .with_status_codes(404, cycle=True)
        .with_exceptions(NotFound("This is a NotFound")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a MethodNotAllowed"}}, cycle=True)
        .with_status_codes(405, cycle=True)
        .with_exceptions(MethodNotAllowed("This is a MethodNotAllowed")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a DuplicateRecordError"}}, cycle=True)
        .with_status_codes(412, cycle=True)
        .with_exceptions(DuplicateRecordError("This is a DuplicateRecordError")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a PayloadTooLarge"}}, cycle=True)
        .with_status_codes(413, cycle=True)
        .with_exceptions(PayloadTooLarge("This is a PayloadTooLarge")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a APILimitsExceeded"}}, cycle=True)
        .with_status_codes(429, cycle=True)
        .with_exceptions(APILimitsExceeded("This is a APILimitsExceeded")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a DynamicsException"}}, cycle=True)
        .with_status_codes(500, cycle=True)
        .with_exceptions(DynamicsException("This is a DynamicsException")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a OperationNotImplemented"}}, cycle=True)
        .with_status_codes(501, cycle=True)
        .with_exceptions(OperationNotImplemented("This is a OperationNotImplemented")),
        MockClient()
        .internal.with_responses({"error": {"message": "This is a WebAPIUnavailable"}}, cycle=True)
        .with_status_codes(503, cycle=True)
        .with_exceptions(WebAPIUnavailable("This is a WebAPIUnavailable")),
    ],
    indirect=True,
)
def test_client_error_handling(dynamics_client):
    error = dynamics_client.next_exception

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.get()

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.post({})

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.patch({})

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.delete()


def test_client_error_handling__get_return_no_items(dynamics_client):
    dynamics_client.internal.with_responses({"value": []})

    with pytest.raises(NotFound, match="No records matching the given criteria."):
        dynamics_client.get()


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
    default_headers = dynamics_client.default_headers(method=method)
    assert default_headers == headers


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
        with mock.patch("dynamics.client.DynamicsClient.get_token"):
            client = DynamicsClient.from_environment()
    except KeyError as error:
        pytest.fail(f"Wrong environment variables: {error}")
        return

    assert client._api_url == "apiurl/"
    assert client._session._client.client_id == "clientid"


def test_client_init_from_cache():
    with mock.patch("dynamics.client.DynamicsClient.get_token", mock.MagicMock(return_value="token")):
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

    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}], "@odata.count": 1})

    assert dynamics_client.get() == [1, {"foo": "bar"}]


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


def test_client_suppress_duplicate_detection(dynamics_client):
    assert dynamics_client.suppress_duplicate_detection is False
    dynamics_client.suppress_duplicate_detection = True
    assert dynamics_client.suppress_duplicate_detection is True
    assert dynamics_client.headers == {"MSCRM.SuppressDuplicateDetection": "true"}
    dynamics_client.suppress_duplicate_detection = False
    assert dynamics_client.headers == {"MSCRM.SuppressDuplicateDetection": "false"}


def test_client_query__fetch_xml(dynamics_client):
    fetch_xml = (
        '<fetch mapping="logical">'
        '<entity name="account">'
        '<attribute name="accountid"/>'
        '<attribute name="name"/>'
        '<attribute name="accountnumber"/>'
        "</entity>"
        "</fetch>"
    )

    dynamics_client.table = "table"
    dynamics_client.fetch_xml = fetch_xml

    expected = (
        "%3Cfetch%20mapping%3D%22logical%22%3E%3Centity%20name%3D%22"
        "account%22%3E%3Cattribute%20name%3D%22accountid%22%2F%3E%3C"
        "attribute%20name%3D%22name%22%2F%3E%3Cattribute%20name%3D%22"
        "accountnumber%22%2F%3E%3C%2Fentity%3E%3C%2Ffetch%3E"
    )

    assert dynamics_client.fetch_xml == fetch_xml
    assert dynamics_client.current_query == f"/table?fetchXml={expected}"


def test_client_get_next_page__before_pagesize_reached(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar", "foo@odata.nextLink": "link-to-next-page"}]})
    assert dynamics_client.get() == [{"foo": "bar"}]


def test_client_get_next_page__over_pagesize(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {"value": [{"foo": [{"@odata.etag": "12345", "bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"}]},
        {"value": [{"@odata.etag": "23456", "fizz": "buzz"}]},
    )

    assert dynamics_client.get() == [
        {
            "foo": [
                {"@odata.etag": "12345", "bar": "baz"},
                {"@odata.etag": "23456", "fizz": "buzz"},
            ],
        },
    ]


def test_client_simplify_errors(dynamics_client):
    dynamics_client.internal.with_responses(*[DynamicsException()] * 4)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.get(simplify_errors=True)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.post({}, simplify_errors=True)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.patch({}, simplify_errors=True)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.delete(simplify_errors=True)


def test_client_simplify_errors__raise_separately(dynamics_client):
    dynamics_client.internal.with_responses(TypeError("Foo"), cycle=True)

    with pytest.raises(TypeError, match="Foo"):
        dynamics_client.get(simplify_errors=True, raise_separately=[TypeError])

    with pytest.raises(TypeError, match="Foo"):
        dynamics_client.post({}, simplify_errors=True, raise_separately=[TypeError])

    with pytest.raises(TypeError, match="Foo"):
        dynamics_client.patch({}, simplify_errors=True, raise_separately=[TypeError])

    with pytest.raises(TypeError, match="Foo"):
        dynamics_client.delete(simplify_errors=True, raise_separately=[TypeError])


def test_client_request_counter(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}, {"value": [{"foo": "baz"}]})

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


def test_client_headers_are_set_on_call(dynamics_client):

    loc = "dynamics.client.DynamicsClient.default_headers"
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}, cycle=True)

    with mock.patch(loc, side_effect=dynamics_client.default_headers) as patch:
        dynamics_client.get()

    patch.assert_called_once()

    with mock.patch(loc, side_effect=dynamics_client.default_headers) as patch:
        dynamics_client.post({})

    patch.assert_called_once()

    with mock.patch(loc, side_effect=dynamics_client.default_headers) as patch:
        dynamics_client.patch({})

    patch.assert_called_once()

    with mock.patch(loc, side_effect=dynamics_client.default_headers) as patch:
        dynamics_client.delete()

    patch.assert_called_once()


def test_client__json_decode_error(dynamics_client):
    dynamics_client.internal.with_responses(JSONDecodeError("foo", "bar", 1), cycle=True)

    with pytest.raises(DynamicsException, match="foo"):
        dynamics_client.get()

    with pytest.raises(DynamicsException, match="foo"):
        dynamics_client.post({})

    with pytest.raises(DynamicsException, match="foo"):
        dynamics_client.patch({})

    with pytest.raises(DynamicsException, match="foo"):
        dynamics_client.delete()


def test_utils__get_token(dynamics_cache, dynamics_client):
    value = dynamics_client.get_token()
    assert value is None
    token = OAuth2Token(params={"foo": "bar"})
    dynamics_cache.set(dynamics_client.cache_key, token)

    value = dynamics_client.get_token()
    assert value == token


def test_utils__set_token(dynamics_cache, dynamics_client):
    value = dynamics_cache.get(dynamics_client.cache_key, None)
    assert value is None
    token = OAuth2Token(params={"foo": "bar", "expires_in": 3600})
    dynamics_client.set_token(token)

    value = dynamics_cache.get(dynamics_client.cache_key, None)
    assert value == token


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info < (3, 11), reason="TaskGroups only available from python 3.11 onwards.")
async def test_client_task_group():
    os.environ["DYNAMICS_API_URL"] = "apiurl"
    os.environ["DYNAMICS_TOKEN_URL"] = "tokenurl"
    os.environ["DYNAMICS_CLIENT_ID"] = "clientid"
    os.environ["DYNAMICS_CLIENT_SECRET"] = "secret"
    os.environ["DYNAMICS_SCOPE"] = "scope"

    r1 = ResponseMock(response={"value": [{"x": 1}]})
    r2 = ResponseMock(response={"y": 2})
    r3 = ResponseMock(response={"value": []})
    r4 = ResponseMock(response=None, status_code=204)

    p1 = mock.patch("dynamics.client.DynamicsClient.get_token")
    p2 = mock.patch("dynamics.client.OAuth2Session.get", return_value=r1)
    p3 = mock.patch("dynamics.client.OAuth2Session.patch", return_value=r2)
    p4 = mock.patch("dynamics.client.OAuth2Session.delete", return_value=r3)
    p5 = mock.patch("dynamics.client.OAuth2Session.post", return_value=r4)

    with p1, p2, p3, p4, p5:
        async with DynamicsClient.from_environment() as client:
            client.table = "foo"
            client.select = ["bar"]
            task_1 = client.create_task(client.get, not_found_ok=True)
            client.reset_query()

            client.table = "fizz"
            client.select = ["buzz"]
            task_2 = client.create_task(client.patch, data={"1": "2"}, simplify_errors=True)
            client.reset_query()

            client.table = "xxx"
            client.row_id = "yyy"
            task_3 = client.create_task(client.delete)
            client.reset_query()

            task4 = client.create_task(client.actions.win_quote, quote_id="abc")
            client.reset_query()

    assert task_1.result() == [{"x": 1}]
    assert task_2.result() == {"y": 2}
    assert task_3.result() is None
    assert task4.result() is None


@pytest.mark.asyncio
async def test_client_task_group__outside_context_manager():
    os.environ["DYNAMICS_API_URL"] = "apiurl"
    os.environ["DYNAMICS_TOKEN_URL"] = "tokenurl"
    os.environ["DYNAMICS_CLIENT_ID"] = "clientid"
    os.environ["DYNAMICS_CLIENT_SECRET"] = "secret"
    os.environ["DYNAMICS_SCOPE"] = "scope"

    with mock.patch("dynamics.client.DynamicsClient.get_token"):
        client = DynamicsClient.from_environment()

    with mock.patch("dynamics.client.OAuth2Session.get", return_value=ResponseMock(response={"value": []})):
        task = client.create_task(client.get, not_found_ok=True)
        result = await task

    assert result == []


@pytest.mark.asyncio
@pytest.mark.skipif(sys.version_info >= (3, 11), reason="TaskGroups available from python 3.11 onwards.")
async def test_client_task_group__no_taskgroup():
    os.environ["DYNAMICS_API_URL"] = "apiurl"
    os.environ["DYNAMICS_TOKEN_URL"] = "tokenurl"
    os.environ["DYNAMICS_CLIENT_ID"] = "clientid"
    os.environ["DYNAMICS_CLIENT_SECRET"] = "secret"
    os.environ["DYNAMICS_SCOPE"] = "scope"

    r1 = ResponseMock(response={"value": [{"x": 1}]})

    p1 = mock.patch("dynamics.client.DynamicsClient.get_token")
    p2 = mock.patch("dynamics.client.OAuth2Session.get", return_value=r1)

    with p1, p2:
        async with DynamicsClient.from_environment() as client:
            client.table = "foo"
            client.select = ["bar"]
            task = client.create_task(client.get)
            result = await task

    assert result == [{"x": 1}]
