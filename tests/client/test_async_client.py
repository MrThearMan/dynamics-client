import sys
from unittest.mock import patch

import pytest
from authlib.oauth2.rfc6749 import OAuth2Token

from dynamics.test import AsyncMockClient, ResponseMock
from dynamics.typing import DynamicsClientGetResponse

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    "async_dynamics_client",
    [
        AsyncMockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        AsyncMockClient().internal.with_responses({"value": []}).with_status_codes(204),
        AsyncMockClient().internal.with_responses({"value": [{"foo": "bar"}, {"one": 2}]}).with_status_codes(200),
    ],
    indirect=True,
)
async def test_async_client__get_request(async_dynamics_client):
    response = await async_dynamics_client.get(not_found_ok=True)
    assert response.data == async_dynamics_client.current_response


@pytest.mark.parametrize(
    "async_dynamics_client",
    [
        AsyncMockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        AsyncMockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
async def test_async_client__post_request(async_dynamics_client):
    response = await async_dynamics_client.post(data={})
    assert response.data == async_dynamics_client.current_response


@pytest.mark.parametrize(
    "async_dynamics_client",
    [
        AsyncMockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        AsyncMockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
async def test_async_client__patch_request(async_dynamics_client):
    response = await async_dynamics_client.patch(data={})
    assert response.data == async_dynamics_client.current_response


@pytest.mark.parametrize(
    "async_dynamics_client",
    [
        AsyncMockClient().internal.with_status_codes(204),
    ],
    indirect=True,
)
async def test_async_client__delete_request(async_dynamics_client):
    assert (await async_dynamics_client.delete()) == async_dynamics_client.current_response


async def test_async_client__get_and_set_token(async_dynamics_client):
    value = await async_dynamics_client.get_token()
    assert value is None
    token = OAuth2Token(params={"foo": "bar", "expires_in": 3600})
    await async_dynamics_client.set_token(token)

    value = await async_dynamics_client.get_token()
    assert value == token


@pytest.mark.skipif(sys.version_info < (3, 11), reason="TaskGroups only available from python 3.11 onwards.")
async def test_async_client__task_group(async_dynamics_client):
    async_dynamics_client.internal.with_status_codes(200, 200, 200, 204, 200).with_responses(
        {"value": [{"x": 1}]},
        {"y": 2},
        {"y": 3},
        None,
        {"y": 2},
    )

    async with async_dynamics_client as client:
        client.table = "foo"
        client.select = ["bar"]
        task_1 = client.create_task(client.get, not_found_ok=True)
        client.reset_query()

        client.table = "fizz"
        client.select = ["buzz"]
        task_2 = client.create_task(client.post, data={"1": "2"}, simplify_errors=True)
        client.reset_query()

        client.table = "fizz"
        client.select = ["buzz"]
        task_3 = client.create_task(client.patch, data={"1": "2"}, simplify_errors=True)
        client.reset_query()

        client.table = "xxx"
        client.row_id = "yyy"
        task_4 = client.create_task(client.delete)
        client.reset_query()

        task_5 = client.create_task(client.actions.win_quote, quote_id="abc")
        client.reset_query()

    assert task_1.result().data == [{"x": 1}]
    assert task_2.result().data == {"y": 2}
    assert task_3.result().data == {"y": 3}
    assert task_4.result() is None
    assert task_5.result() is None


async def test_async_client__task_group__outside_context_manager(async_dynamics_client):
    async_dynamics_client.internal.with_status_codes(200).with_responses({"value": []})
    task = async_dynamics_client.create_task(async_dynamics_client.get, not_found_ok=True)
    result = await task

    assert result.data == []


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="TaskGroups available from python 3.11 onwards.")
async def test_async_client__task_group__no_taskgroup(async_dynamics_client):
    async_dynamics_client.internal.with_status_codes(200).with_responses({"value": [{"x": 1}]})

    async with async_dynamics_client as client:
        client.table = "foo"
        client.select = ["bar"]
        task = client.create_task(client.get)
        result = await task

    assert result.data == [{"x": 1}]


async def test_async_client__get_next_page(async_dynamics_client):
    async_dynamics_client.pagesize = 1

    async_dynamics_client.internal.with_responses(
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

    response = await async_dynamics_client.get(pagination_rules={"pages": 2})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}, {"fizz": "buzz"}, {"1": "2"}],
        next_link=None,
    )


async def test_async_client__get_next_page__not_all_pages(async_dynamics_client):
    async_dynamics_client.pagesize = 1

    async_dynamics_client.internal.with_responses(
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

    response = await async_dynamics_client.get(pagination_rules={"pages": 1})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}, {"fizz": "buzz"}],
        next_link="link-to-next-page-2",
    )


async def test_async_client__dont_paginate(async_dynamics_client):
    async_dynamics_client.pagesize = 1

    async_dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar"}],
            "@odata.nextLink": "link-to-next-page",
        },
        {
            "value": [{"fizz": "buzz"}],
        },
    )

    response = await async_dynamics_client.get()
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}],
        next_link="link-to-next-page",
    )


async def test_async_client__get_next_page__dont_fetch_if_under_pagesize(async_dynamics_client):
    async_dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar"}],
            "@odata.nextLink": "link-to-next-page",
        },
    )

    response = await async_dynamics_client.get(pagination_rules={"pages": 1})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}],
        next_link=None,
    )


async def test_async_client__get_next_page__nested(async_dynamics_client):
    async_dynamics_client.pagesize = 1

    async_dynamics_client.internal.with_responses(
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

    response = await async_dynamics_client.get(pagination_rules={"pages": 0, "children": {"foo": {"pages": 2}}})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": [{"bar": "baz"}, {"fizz": "buzz"}, {"1": "2"}]}],
        next_link=None,
    )


async def test_async_client__get_next_page__nested__not_all_pages(async_dynamics_client):
    async_dynamics_client.pagesize = 1

    async_dynamics_client.internal.with_responses(
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

    response = await async_dynamics_client.get(pagination_rules={"pages": 0, "children": {"foo": {"pages": 1}}})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": [{"bar": "baz"}, {"fizz": "buzz"}], "foo@odata.nextLink": "link-to-next-page-2"}],
        next_link=None,
    )


async def test_async_client__get_next_page__nested__dont_paginate(async_dynamics_client):
    async_dynamics_client.pagesize = 1

    async_dynamics_client.internal.with_responses(
        {
            "value": [{"foo": [{"bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"}],
        },
    )

    response = await async_dynamics_client.get()
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": [{"bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"}],
        next_link=None,
    )


async def test_async_client__get_next_page__nested__dont_fetch_if_under_pagesize(async_dynamics_client):
    async_dynamics_client.internal.with_responses(
        {
            "value": [{"foo": "bar", "foo@odata.nextLink": "link-to-next-page"}],
        },
    )
    response = await async_dynamics_client.get(pagination_rules={"pages": 0, "children": {"foo": {"pages": 1}}})
    assert response == DynamicsClientGetResponse(
        count=None,
        data=[{"foo": "bar"}],
        next_link=None,
    )


async def test_async_client__ensure_token__token_already_set(async_dynamics_client):
    token = OAuth2Token({"expires_in": "60"})
    response = ResponseMock(response=token)
    async_dynamics_client._oauth_client.token = token

    patch_1 = patch("dynamics.client.aio.DynamicsClient.get_token", return_value=token)
    patch_2 = patch("authlib.integrations.httpx_client.oauth2_client.AsyncOAuth2Client.post", return_value=response)

    with patch_1 as mock_1, patch_2 as mock_2:
        await async_dynamics_client._ensure_token()

    assert async_dynamics_client._oauth_client.token == token

    assert mock_1.await_count == 0
    assert mock_2.await_count == 0


async def test_async_client__ensure_token__token_in_cache(async_dynamics_client):
    token = OAuth2Token({"expires_in": "60"})
    response = ResponseMock(response=token)
    assert async_dynamics_client._oauth_client.token is None

    patch_1 = patch("dynamics.client.aio.DynamicsClient.get_token", return_value=token)
    patch_2 = patch("authlib.integrations.httpx_client.oauth2_client.AsyncOAuth2Client.post", return_value=response)

    with patch_1 as mock_1, patch_2 as mock_2:
        await async_dynamics_client._ensure_token()

    assert async_dynamics_client._oauth_client.token == token

    assert mock_1.await_count == 1
    assert mock_2.await_count == 0


async def test_async_client__ensure_token__token_fetched_from_endpoint(async_dynamics_client):
    token = OAuth2Token({"expires_in": "60"})
    response = ResponseMock(response=token)
    assert async_dynamics_client._oauth_client.token is None

    patch_1 = patch("dynamics.client.aio.DynamicsClient.get_token", return_value=None)
    patch_2 = patch("authlib.integrations.httpx_client.oauth2_client.AsyncOAuth2Client.post", return_value=response)

    with patch_1 as mock_1, patch_2 as mock_2:
        await async_dynamics_client._ensure_token()

    assert async_dynamics_client._oauth_client.token == token

    assert mock_1.await_count == 1
    assert mock_2.await_count == 1
