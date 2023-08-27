import pytest
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from dynamics.test import MockClient


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
    assert dynamics_client.get(not_found_ok=True) == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
def test_client__post_request(dynamics_client):
    assert dynamics_client.post(data={}) == dynamics_client.current_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        MockClient().internal.with_responses({"foo": "bar", "one": 2}).with_status_codes(200),
        MockClient().internal.with_responses({}).with_status_codes(204),
    ],
    indirect=True,
)
def test_client__patch_request(dynamics_client):
    assert dynamics_client.patch(data={}) == dynamics_client.current_response


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


def test_client__get_next_page__before_pagesize_reached(dynamics_client):
    dynamics_client.internal.with_responses({"value": [{"foo": "bar", "foo@odata.nextLink": "link-to-next-page"}]})
    assert dynamics_client.get() == [{"foo": "bar"}]


def test_client__get_next_page__over_pagesize(dynamics_client):
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
