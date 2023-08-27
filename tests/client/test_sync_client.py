import pytest
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from dynamics.test import MockClient
from dynamics.typing import DynamicsClientGetResponse


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({"value": []}).with_status_codes(204),
        MockClient().internal.with_responses({"value": [{"foo": "bar"}, {"one": 2}]}).with_status_codes(200),
    ],
    indirect=True,
)
def test_client__get_request(dynamics_client):
    assert dynamics_client.get(not_found_ok=True).data == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
def test_client__post_request(dynamics_client):
    assert dynamics_client.post(data={}).data == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
def test_client__patch_request(dynamics_client):
    assert dynamics_client.patch(data={}).data == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_status_codes(204),
    ],
    indirect=True,
)
def test_client__delete_request(dynamics_client):
    assert dynamics_client.delete() == dynamics_client.current_response


def test_client__get_and_set_token(dynamics_client):
    value = dynamics_client.get_token()
    assert value is None
    token = OAuth2Token(params={"foo": "bar", "expires_in": 3600})
    dynamics_client.set_token(token)

    value = dynamics_client.get_token()
    assert value == token


def test_async_client__get_next_page(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar"}],
            "@odata.nextLink": "link-to-next-page",
        },
        {
            "value": [{"fizz": "buzz"}],
        },
    )

    response = dynamics_client.get(pagination_rules={"pages": 1})
    assert response.data == [{"foo": "bar"}, {"fizz": "buzz"}]


def test_async_client__get_next_page__dont_paginate(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar"}],
            "@odata.nextLink": "link-to-next-page",
        },
    )

    response = dynamics_client.get()
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}],
        next_link="link-to-next-page",
    )


def test_async_client__get_next_page__dont_fetch_if_under_pagesize(dynamics_client):
    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar"}],
            "@odata.nextLink": "link-to-next-page",
        },
    )

    response = dynamics_client.get(pagination_rules={"pages": 1})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}],
        next_link=None,
    )


def test_async_client__get_next_page__nested(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": [{"bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"}],
        },
        {
            "value": [{"fizz": "buzz"}],
        },
    )

    response = dynamics_client.get(pagination_rules={"pages": 0, "children": {"foo": {"pages": 1}}})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": [{"bar": "baz"}, {"fizz": "buzz"}]}],
        next_link=None,
    )


def test_async_client__get_next_page__nested__dont_paginate(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": [{"bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"}],
        },
    )

    response = dynamics_client.get()
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": [{"bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"}],
        next_link=None,
    )


def test_async_client__get_next_page__nested__dont_fetch_if_under_pagesize(dynamics_client):
    dynamics_client.internal.with_responses(
        {
            "value": [
                {"foo": "bar", "foo@odata.nextLink": "link-to-next-page"},
            ],
        },
    )
    response = dynamics_client.get(pagination_rules={"pages": 0, "children": {"foo": {"pages": 1}}})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}],
        next_link=None,
    )
