import pytest

from dynamics.client import DynamicsClient

from .conftest import DynamicsResponse, dynamics_client_response


@pytest.mark.parametrize(
    "dynamics_client",
    [
        DynamicsResponse(method="get", response={"foo": "bar", "one": 2}, status_code=200),
    ],
    indirect=True,
)
def test_get(dynamics_client: "DynamicsClient"):
    assert dynamics_client.get() == [{"foo": "bar", "one": 2}]


@pytest.mark.parametrize(
    "dynamics_client",
    [
        DynamicsResponse(method="post", response={"foo": "bar", "one": 2}, status_code=200),
    ],
    indirect=True,
)
def test_post(dynamics_client: "DynamicsClient"):
    assert dynamics_client.post(data={"foo": "bar", "one": 2}) == {"foo": "bar", "one": 2}


def test_no_parameters(dynamics_client: "DynamicsClient"):
    with dynamics_client_response(dynamics_client, method="post", response={}, status_code=200):
        assert dynamics_client.post(data={"foo": "bar", "one": 2}) == {}
