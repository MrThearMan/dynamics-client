import sys
from unittest import mock

import pytest
from authlib.oauth2.rfc6749 import OAuth2Token

from dynamics import DynamicsClient
from dynamics.client.aio import DynamicsClient as AsyncDynamicsClient
from dynamics.test import AsyncMockClient, ResponseMock

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
    assert (await async_dynamics_client.get(not_found_ok=True)) == async_dynamics_client.current_response


@pytest.mark.parametrize(
    "async_dynamics_client",
    [
        AsyncMockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        AsyncMockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
async def test_async_client__post_request(async_dynamics_client):
    assert (await async_dynamics_client.post(data={})) == async_dynamics_client.current_response


@pytest.mark.parametrize(
    "async_dynamics_client",
    [
        AsyncMockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        AsyncMockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
async def test_async_client__patch_request(async_dynamics_client):
    assert (await async_dynamics_client.patch(data={})) == async_dynamics_client.current_response


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
async def test_async_client__task_group(environ):
    r1 = ResponseMock(response={"value": [{"x": 1}]})
    r2 = ResponseMock(response={"y": 2})
    r3 = ResponseMock(response={"value": []})
    r4 = ResponseMock(response=None, status_code=204)

    token = OAuth2Token({"expires_in": "60"})
    p1 = mock.patch("dynamics.client.aio.DynamicsClient.get_token", return_value=token)
    p2 = mock.patch("authlib.integrations.httpx_client.AsyncOAuth2Client.get", return_value=r1)
    p3 = mock.patch("authlib.integrations.httpx_client.AsyncOAuth2Client.patch", return_value=r2)
    p4 = mock.patch("authlib.integrations.httpx_client.AsyncOAuth2Client.delete", return_value=r3)
    p5 = mock.patch("authlib.integrations.httpx_client.AsyncOAuth2Client.post", side_effect=[r2, r4])

    with environ(
        DYNAMICS_API_URL="apiurl",
        DYNAMICS_TOKEN_URL="tokenurl",
        DYNAMICS_CLIENT_ID="clientid",
        DYNAMICS_CLIENT_SECRET="secret",
        DYNAMICS_SCOPE="scope",
    ):
        with p1, p2, p3, p4, p5:
            async with AsyncDynamicsClient.from_environment() as client:
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

    assert task_1.result() == [{"x": 1}]
    assert task_2.result() == {"y": 2}
    assert task_3.result() == {"y": 2}
    assert task_4.result() is None
    assert task_5.result() is None


async def test_async_client__task_group__outside_context_manager(environ):
    with environ(
        DYNAMICS_API_URL="apiurl",
        DYNAMICS_TOKEN_URL="tokenurl",
        DYNAMICS_CLIENT_ID="clientid",
        DYNAMICS_CLIENT_SECRET="secret",
        DYNAMICS_SCOPE="scope",
    ):
        client = AsyncDynamicsClient.from_environment()

    response_mock = ResponseMock(response={"value": []})
    token = OAuth2Token({"expires_in": "60"})

    with mock.patch("authlib.integrations.httpx_client.AsyncOAuth2Client.get", side_effect=[response_mock]):
        with mock.patch("dynamics.client.aio.DynamicsClient.get_token", return_value=token):
            task = client.create_task(client.get, not_found_ok=True)
            result = await task

    assert result == []


@pytest.mark.skipif(sys.version_info >= (3, 11), reason="TaskGroups available from python 3.11 onwards.")
async def test_async_client__task_group__no_taskgroup(environ):
    r1 = ResponseMock(response={"value": [{"x": 1}]})

    p1 = mock.patch("dynamics.client.DynamicsClient.get_token")
    p2 = mock.patch("dynamics.client.OAuth2Client.get", return_value=r1)

    with environ(
        DYNAMICS_API_URL="apiurl",
        DYNAMICS_TOKEN_URL="tokenurl",
        DYNAMICS_CLIENT_ID="clientid",
        DYNAMICS_CLIENT_SECRET="secret",
        DYNAMICS_SCOPE="scope",
    ):
        with p1, p2:
            async with DynamicsClient.from_environment() as client:
                client.table = "foo"
                client.select = ["bar"]
                task = client.create_task(client.get)
                result = await task

    assert result == [{"x": 1}]


async def test_async_client__get_next_page__before_pagesize_reached(async_dynamics_client):
    async_dynamics_client.internal.with_responses(
        {"value": [{"foo": "bar", "foo@odata.nextLink": "link-to-next-page"}]},
    )
    assert (await async_dynamics_client.get()) == [{"foo": "bar"}]


async def test_async_client__get_next_page__over_pagesize(async_dynamics_client):
    async_dynamics_client.pagesize = 1

    async_dynamics_client.internal.with_responses(
        {"value": [{"foo": [{"@odata.etag": "12345", "bar": "baz"}], "foo@odata.nextLink": "link-to-next-page"}]},
        {"value": [{"@odata.etag": "23456", "fizz": "buzz"}]},
    )

    assert (await async_dynamics_client.get()) == [
        {
            "foo": [
                {"@odata.etag": "12345", "bar": "baz"},
                {"@odata.etag": "23456", "fizz": "buzz"},
            ],
        },
    ]
