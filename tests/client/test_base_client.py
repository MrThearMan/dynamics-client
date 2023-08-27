import re
from types import SimpleNamespace
from unittest import mock

import httpx
import pytest
from requests import JSONDecodeError

from dynamics import DynamicsClient
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
from dynamics.test import MockClient
from dynamics.typing import DynamicsClientGetResponse, MethodType


@pytest.mark.parametrize(
    "dynamics_client",
    [
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a ParseError", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(400, cycle=True)
            .with_exceptions(ParseError("This is a ParseError"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a AuthenticationFailed", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(401, cycle=True)
            .with_exceptions(AuthenticationFailed("This is a AuthenticationFailed"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a PermissionDenied", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(403, cycle=True)
            .with_exceptions(PermissionDenied("This is a PermissionDenied"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a NotFound", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(404, cycle=True)
            .with_exceptions(NotFound("This is a NotFound"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a MethodNotAllowed", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(405, cycle=True)
            .with_exceptions(MethodNotAllowed("This is a MethodNotAllowed"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a DuplicateRecordError", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(412, cycle=True)
            .with_exceptions(DuplicateRecordError("This is a DuplicateRecordError"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a PayloadTooLarge", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(413, cycle=True)
            .with_exceptions(PayloadTooLarge("This is a PayloadTooLarge"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a APILimitsExceeded", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(429, cycle=True)
            .with_exceptions(APILimitsExceeded("This is a APILimitsExceeded"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a DynamicsException", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(500, cycle=True)
            .with_exceptions(DynamicsException("This is a DynamicsException"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a OperationNotImplemented", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(501, cycle=True)
            .with_exceptions(OperationNotImplemented("This is a OperationNotImplemented"))
        ),
        (
            MockClient()
            .internal.with_responses(
                {"error": {"message": "This is a WebAPIUnavailable", "code": "0"}},
                cycle=True,
            )
            .with_status_codes(503, cycle=True)
            .with_exceptions(WebAPIUnavailable("This is a WebAPIUnavailable"))
        ),
    ],
    indirect=True,
)
def test_client__error_handling(dynamics_client):
    error = dynamics_client.next_exception

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.get()

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.post({})

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.patch({})

    with pytest.raises(error.__class__, match=error.args[0]):
        dynamics_client.delete()


def test_client__error_handling__get_return_no_items(dynamics_client):
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
def test_client__set_default_headers(dynamics_client, method: MethodType, headers: dict):
    default_headers = dynamics_client.default_headers(method=method)
    assert default_headers == headers


def test_client__headers(dynamics_client):
    assert dynamics_client.headers == {}
    dynamics_client["Accept"] = "application/json"
    assert dynamics_client["Accept"] == "application/json"


@pytest.mark.parametrize(
    ["scope", "resource"],
    [
        (None, "resource"),
        ("scope", None),
        ("scope1,scope2", None),
        ("scope", "resource"),
    ],
)
def test_client__init_from_environment_successes(scope, resource, environ):
    env = {
        "DYNAMICS_API_URL": "apiurl",
        "DYNAMICS_TOKEN_URL": "tokenurl",
        "DYNAMICS_CLIENT_ID": "clientid",
        "DYNAMICS_CLIENT_SECRET": "secret",
    }
    if scope is not None:
        env["DYNAMICS_SCOPE"] = scope
    if resource is not None:
        env["DYNAMICS_RESOURCE"] = resource

    with environ(**env):
        with mock.patch("dynamics.client.DynamicsClient.get_token"):
            DynamicsClient.from_environment()


def test_client__init_from_environment_scope_or_resource_required(environ):
    env = {
        "DYNAMICS_API_URL": "apiurl",
        "DYNAMICS_TOKEN_URL": "tokenurl",
        "DYNAMICS_CLIENT_ID": "clientid",
        "DYNAMICS_CLIENT_SECRET": "secret",
    }

    with environ(**env):
        with mock.patch("dynamics.client.DynamicsClient.get_token"):
            with pytest.raises(
                KeyError,
                match=re.escape("At least one of DYNAMICS_SCOPE or DYNAMICS_RESOURCE env var must be set."),
            ):
                DynamicsClient.from_environment()


@pytest.mark.parametrize(
    "missing_env",
    [
        "DYNAMICS_API_URL",
        "DYNAMICS_TOKEN_URL",
        "DYNAMICS_CLIENT_ID",
        "DYNAMICS_CLIENT_SECRET",
        "DYNAMICS_SCOPE",
    ],
)
def test_client__init_from_environment_fails_when_missing(missing_env, environ):
    env = {
        "DYNAMICS_API_URL": "apiurl",
        "DYNAMICS_TOKEN_URL": "tokenurl",
        "DYNAMICS_CLIENT_ID": "clientid",
        "DYNAMICS_CLIENT_SECRET": "secret",
        "DYNAMICS_SCOPE": "scope",
    }
    env.pop(missing_env)

    with environ(**env):
        with mock.patch("dynamics.client.DynamicsClient.get_token"):
            with pytest.raises(KeyError):
                DynamicsClient.from_environment()


@pytest.mark.parametrize(
    "arguments",
    [
        {
            "api_url": "http://dynamics.local/",
            "token_url": "http://token.local",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "scope": "http://scope.local/",
            "resource": None,
        },
        {
            "api_url": "http://dynamics.local/",
            "token_url": "http://token.local",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "scope": ["http://scope.local/"],
            "resource": None,
        },
        {
            "api_url": "http://dynamics.local/",
            "token_url": "http://token.local",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "scope": ["http://scope.local/"],
            "resource": "http://resource.local/",
        },
        {
            "api_url": "http://dynamics.local/",
            "token_url": "http://token.local",
            "client_id": "client_id",
            "client_secret": "client_secret",
            "scope": None,
            "resource": "http://resource.local/",
        },
    ],
)
def test_client__init_success(arguments):
    with mock.patch("dynamics.client.DynamicsClient.get_token"):
        DynamicsClient(**arguments)


def test_client__init_scope_or_resource_required(environ):
    with mock.patch("dynamics.client.DynamicsClient.get_token"):
        with pytest.raises(
            ValueError,
            match=re.escape(
                "To instantiate a DynamicsClient, you must provide at least one of either "
                "the scope or resource parameters."
            ),
        ):
            DynamicsClient(api_url="apiurl", token_url="tokenurl", client_id="clientid", client_secret="secret")


def test_client__query__table(dynamics_client):
    dynamics_client.table = "table"
    assert dynamics_client.table == "table"
    assert dynamics_client.current_query == "http://dynamics.local/table"


def test_client__query__row_id(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.row_id = "row_id"
    assert dynamics_client.row_id == "row_id"
    assert dynamics_client.current_query == "http://dynamics.local/table(row_id)"


def test_client__query__add_ref_to_property(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.row_id = "row_id"
    dynamics_client.add_ref_to_property = "property"
    assert dynamics_client.add_ref_to_property == "property"
    assert dynamics_client.current_query == "http://dynamics.local/table(row_id)/property/$ref"


def test_client__query__pre_expand(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.pre_expand = "foo"
    assert dynamics_client.pre_expand == "foo"
    assert dynamics_client.current_query == "http://dynamics.local/table/foo"


def test_client__query__action(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.action = "foo"
    assert dynamics_client.action == "foo"
    assert dynamics_client.current_query == "http://dynamics.local/table/foo"

    dynamics_client.table = ""
    assert dynamics_client.current_query == "http://dynamics.local/foo"


def test_client__query__select(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.select = ["foo"]
    assert dynamics_client.select == ["foo"]
    assert dynamics_client.current_query == "http://dynamics.local/table?$select=foo"


def test_client__query__select__multiple(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.select = ["foo", "bar"]
    assert dynamics_client.select == ["foo", "bar"]
    assert dynamics_client.current_query == "http://dynamics.local/table?$select=foo,bar"


def test_client__query__expand(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": None}
    assert dynamics_client.expand == {"foo": None}
    assert dynamics_client.current_query == "http://dynamics.local/table?$expand=foo"


def test_client__query__expand__with_select(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"select": ["bar"]}}
    assert dynamics_client.expand == {"foo": {"select": ["bar"]}}
    assert dynamics_client.current_query == "http://dynamics.local/table?$expand=foo($select=bar)"


def test_client__query__expand__with_select_and_filer(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"select": ["bar"], "filter": ["baz"]}}
    assert dynamics_client.expand == {"foo": {"select": ["bar"], "filter": ["baz"]}}
    assert dynamics_client.current_query == "http://dynamics.local/table?$expand=foo($select=bar;$filter=baz)"


def test_client__query__expand__with_select_and_filer__multiple(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"select": ["bar", "baz"], "filter": ["fizz", "buzz"]}}
    assert dynamics_client.expand == {"foo": {"select": ["bar", "baz"], "filter": ["fizz", "buzz"]}}
    assert (
        dynamics_client.current_query
        == "http://dynamics.local/table?$expand=foo($select=bar,baz;$filter=fizz and buzz)"
    )


def test_client__query__expand__with_all_options(dynamics_client):
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
        "http://dynamics.local/table?"
        "$expand=foo("
        "$select=bar,baz;"
        "$filter=fizz and buzz;"
        "$orderby=one two;"
        "$top=10;"
        "$expand=foobar($select=barbaz)"
        ")"
    )


def test_client__query__expand__invalid_option(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.expand = {"foo": {"bar": "baz"}}
    assert dynamics_client.expand == {"foo": {"bar": "baz"}}

    with pytest.raises(KeyError) as exc_info:
        _ = dynamics_client.current_query

    assert exc_info.value.args[0] == "'bar' is not a valid query inside expand statement!"


def test_client__query__filter(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.filter = ["foo"]
    assert dynamics_client.filter == ["foo"]
    assert dynamics_client.current_query == "http://dynamics.local/table?$filter=foo"


def test_client__query__filter__empty(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(ValueError) as exc_info:
        dynamics_client.filter = []

    assert exc_info.value.args[0] == "Filter list cannot be empty."


def test_client__query__filter__not_valid_type(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(TypeError) as exc_info:
        dynamics_client.filter = "foo"

    assert exc_info.value.args[0] == "Filter items must be either a set or a list."


def test_client__query__filter__multiple__and(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.filter = ["foo", "bar"]
    assert dynamics_client.filter == ["foo", "bar"]
    assert dynamics_client.current_query == "http://dynamics.local/table?$filter=foo and bar"


def test_client__query__filter__multiple__or(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.filter = {"foo", "bar"}
    assert dynamics_client.filter == {"foo", "bar"}
    # Since sets are unordered, both can be true
    try:
        assert dynamics_client.current_query == "http://dynamics.local/table?$filter=foo or bar"
    except AssertionError:
        assert dynamics_client.current_query == "http://dynamics.local/table?$filter=bar or foo"


def test_client__query__apply(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.apply = "foo"
    assert dynamics_client.apply == "foo"
    assert dynamics_client.current_query == "http://dynamics.local/table?$apply=foo"


def test_client__query__top(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.top = 1
    assert dynamics_client.top == 1
    assert dynamics_client.current_query == "http://dynamics.local/table?$top=1"


def test_client__query__orderby(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.orderby = {"foo": "asc"}
    assert dynamics_client.orderby == {"foo": "asc"}
    assert dynamics_client.current_query == "http://dynamics.local/table?$orderby=foo asc"


def test_client__query__orderby__multiple(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.orderby = {"foo": "asc", "bar": "desc"}
    assert dynamics_client.orderby == {"foo": "asc", "bar": "desc"}
    assert dynamics_client.current_query == "http://dynamics.local/table?$orderby=foo asc,bar desc"


def test_client__query__orderby__empty(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(ValueError) as exc_info:
        dynamics_client.orderby = {}

    assert exc_info.value.args[0] == "Orderby dict must not be empty."


def test_client__query__orderby__not_valid_type(dynamics_client):
    dynamics_client.table = "table"
    with pytest.raises(TypeError) as exc_info:
        dynamics_client.orderby = "foo"

    assert exc_info.value.args[0] == "Orderby items must be a dict."


def test_client__query__count(dynamics_client):
    dynamics_client.table = "table"
    dynamics_client.count = True
    assert dynamics_client.count is True
    assert dynamics_client.current_query == "http://dynamics.local/table?$count=true"

    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}], "@odata.count": 1})

    assert dynamics_client.get() == DynamicsClientGetResponse(count=1, data=[{"foo": "bar"}], next_link=None)


def test_client__query__fetch_xml(dynamics_client):
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
    assert dynamics_client.current_query == f"http://dynamics.local/table?fetchXml={expected}"


def test_client__pagesize(dynamics_client):
    assert dynamics_client.pagesize == 5000
    dynamics_client.pagesize = 2000
    assert dynamics_client.pagesize == 2000

    with pytest.raises(ValueError) as exc_info:
        dynamics_client.pagesize = -10

    assert exc_info.value.args[0] == "Value must be bigger than 0. Got -10."

    with pytest.raises(ValueError) as exc_info:
        dynamics_client.pagesize = 5001

    assert exc_info.value.args[0] == "Max pagesize is 5000. Got 5001."


def test_client__show_annotations(dynamics_client):
    assert dynamics_client.show_annotations is False
    dynamics_client.show_annotations = True
    assert dynamics_client.show_annotations is True
    assert dynamics_client.headers == {"Prefer": 'odata.include-annotations="*"'}
    dynamics_client.show_annotations = False
    assert dynamics_client.headers == {}


def test_client__suppress_duplicate_detection(dynamics_client):
    assert dynamics_client.suppress_duplicate_detection is False
    dynamics_client.suppress_duplicate_detection = True
    assert dynamics_client.suppress_duplicate_detection is True
    assert dynamics_client.headers == {"MSCRM.SuppressDuplicateDetection": "true"}
    dynamics_client.suppress_duplicate_detection = False
    assert dynamics_client.headers == {"MSCRM.SuppressDuplicateDetection": "false"}


def test_client__simplify_errors(dynamics_client):
    dynamics_client.internal.with_responses(*[DynamicsException()] * 4)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.get(simplify_errors=True)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.post({}, simplify_errors=True)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.patch({}, simplify_errors=True)

    with pytest.raises(DynamicsException, match=dynamics_client.simplified_error_message):
        dynamics_client.delete(simplify_errors=True)


def test_client__simplify_errors__raise_separately(dynamics_client):
    data = {"error": {"message": "foo", "code": "1"}}
    dynamics_client.internal.with_responses(data, cycle=True).with_status_codes(400, cycle=True)

    with pytest.raises(ParseError, match=re.escape("[400] foo <dynamics_parse_error>")):
        dynamics_client.get(simplify_errors=True, raise_separately=[ParseError])

    with pytest.raises(ParseError, match=re.escape("[400] foo <dynamics_parse_error>")):
        dynamics_client.post({}, simplify_errors=True, raise_separately=[ParseError])

    with pytest.raises(ParseError, match=re.escape("[400] foo <dynamics_parse_error>")):
        dynamics_client.patch({}, simplify_errors=True, raise_separately=[ParseError])

    with pytest.raises(ParseError, match=re.escape("[400] foo <dynamics_parse_error>")):
        dynamics_client.delete(simplify_errors=True, raise_separately=[ParseError])


def test_client__request_counter(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar"}]}, {"value": [{"foo": "baz"}]})

    assert dynamics_client.request_counter == 0
    dynamics_client.get()
    assert dynamics_client.request_counter == 1
    dynamics_client.get()
    assert dynamics_client.request_counter == 2


def test_client__reset_query(dynamics_client):
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

    assert dynamics_client.current_query != "http://dynamics.local/"
    assert "foo" in dynamics_client.headers
    assert dynamics_client.pagesize == 2000

    dynamics_client.reset_query()

    assert dynamics_client.current_query == "http://dynamics.local/"
    assert "foo" not in dynamics_client.headers
    assert dynamics_client.pagesize == 2000


def test_client__headers_are_set_on_call(dynamics_client):
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


def test_client__http_error(dynamics_client):
    request = {}
    response = SimpleNamespace(text="response", status_code=401)
    exception = httpx.HTTPStatusError(message="TEST", request=request, response=response)
    dynamics_client.internal.with_responses(exception, cycle=True)

    with pytest.raises(DynamicsException):
        dynamics_client.get()

    with pytest.raises(DynamicsException):
        dynamics_client.post({})

    with pytest.raises(DynamicsException):
        dynamics_client.patch({})

    with pytest.raises(DynamicsException):
        dynamics_client.delete()


def test_client__json_decode_error(dynamics_client):
    dynamics_client.internal.with_responses(JSONDecodeError("foo", "bar", 1), cycle=True)

    with pytest.raises(DynamicsException):
        dynamics_client.get()

    with pytest.raises(DynamicsException):
        dynamics_client.post({})

    with pytest.raises(DynamicsException):
        dynamics_client.patch({})

    with pytest.raises(DynamicsException):
        dynamics_client.delete()
