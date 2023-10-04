from unittest.mock import patch

import pytest
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from dynamics.test import MockClient, ResponseMock
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


def test_client__get_and_set_token():
    client_1 = MockClient(client_id="id")

    assert client_1.get_token() is None

    token = OAuth2Token({"expires_in": "120"})
    client_1.set_token(token)

    assert client_1.get_token() == token


def test_client__get_and_set_token__multiple_clients():
    client_1 = MockClient(client_id="id1")
    client_2 = MockClient(client_id="id2")

    assert client_1.get_token() is None
    assert client_2.get_token() is None

    token = OAuth2Token({"expires_in": "120"})
    client_1.set_token(token)

    assert client_1.get_token() == token
    assert client_2.get_token() is None


def test_client__get_next_page(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar"}],
            "@odata.nextLink": "link-to-next-page-1",
        },
        {
            "value": [{"fizz": "buzz"}],
            "@odata.nextLink": "link-to-next-page-2",
        },
        {
            "value": [{"1": "2"}],
        },
    )

    response = dynamics_client.get(pagination_rules={"pages": 2})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}, {"fizz": "buzz"}, {"1": "2"}],
        next_link=None,
    )


def test_client__get_next_page__not_all_pages(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar"}],
            "@odata.nextLink": "link-to-next-page-1",
        },
        {
            "value": [{"fizz": "buzz"}],
            "@odata.nextLink": "link-to-next-page-2",
        },
        {
            "value": [{"1": "2"}],
        },
    )

    response = dynamics_client.get(pagination_rules={"pages": 1})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}, {"fizz": "buzz"}],
        next_link="link-to-next-page-2",
    )


def test_client__get_next_page__dont_paginate(dynamics_client):
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


def test_client__get_next_page__dont_fetch_if_under_pagesize(dynamics_client):
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


def test_client__get_next_page__nested(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": [{"bar": "baz"}], "foo@odata.nextLink": "link-to-next-page-1"}],
        },
        {
            "value": [{"fizz": "buzz"}],
            "@odata.nextLink": "link-to-next-page-2",
        },
        {
            "value": [{"1": "2"}],
        },
    )

    response = dynamics_client.get(pagination_rules={"pages": 0, "children": {"foo": {"pages": 2}}})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": [{"bar": "baz"}, {"fizz": "buzz"}, {"1": "2"}]}],
        next_link=None,
    )


def test_client__get_next_page__nested__not_all_pages(dynamics_client):
    dynamics_client.pagesize = 1

    dynamics_client.internal.with_responses(
        {
            "value": [{"foo": [{"bar": "baz"}], "foo@odata.nextLink": "link-to-next-page-1"}],
        },
        {
            "value": [{"fizz": "buzz"}],
            "@odata.nextLink": "link-to-next-page-2",
        },
        {
            "value": [{"1": "2"}],
        },
    )

    response = dynamics_client.get(pagination_rules={"pages": 0, "children": {"foo": {"pages": 1}}})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": [{"bar": "baz"}, {"fizz": "buzz"}], "foo@odata.nextLink": "link-to-next-page-2"}],
        next_link=None,
    )


def test_client__get_next_page__nested__dont_paginate(dynamics_client):
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


def test_client__get_next_page__nested__dont_fetch_if_under_pagesize(dynamics_client):
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


def test_client__ensure_token__token_already_set(dynamics_client):
    token = OAuth2Token({"expires_in": "60"})
    response = ResponseMock(response=token)
    dynamics_client._oauth_client.token = token

    patch_1 = patch("dynamics.client.sync.DynamicsClient.get_token", return_value=token)
    patch_2 = patch("authlib.integrations.httpx_client.oauth2_client.OAuth2Client.post", return_value=response)

    with patch_1 as mock_1, patch_2 as mock_2:
        dynamics_client._ensure_token()

    assert dynamics_client._oauth_client.token == token

    assert mock_1.call_count == 0
    assert mock_2.call_count == 0


def test_client__ensure_token__token_in_cache(dynamics_client):
    token = OAuth2Token({"expires_in": "60"})
    response = ResponseMock(response=token)
    assert dynamics_client._oauth_client.token is None

    patch_1 = patch("dynamics.client.sync.DynamicsClient.get_token", return_value=token)
    patch_2 = patch("authlib.integrations.httpx_client.oauth2_client.OAuth2Client.post", return_value=response)

    with patch_1 as mock_1, patch_2 as mock_2:
        dynamics_client._ensure_token()

    assert dynamics_client._oauth_client.token == token

    assert mock_1.call_count == 1
    assert mock_2.call_count == 0


def test_client__ensure_token__token_fetched_from_endpoint(dynamics_client):
    token = OAuth2Token({"expires_in": "60"})
    response = ResponseMock(response=token)
    assert dynamics_client._oauth_client.token is None

    patch_1 = patch("dynamics.client.sync.DynamicsClient.get_token", return_value=None)
    patch_2 = patch("authlib.integrations.httpx_client.oauth2_client.OAuth2Client.post", return_value=response)

    with patch_1 as mock_1, patch_2 as mock_2:
        dynamics_client._ensure_token()

    assert dynamics_client._oauth_client.token == token

    assert mock_1.call_count == 1
    assert mock_2.call_count == 1
