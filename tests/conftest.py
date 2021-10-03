from contextlib import contextmanager
from unittest import mock

import pytest

from dynamics.client import DynamicsClient
from dynamics.typing import Literal, Union


__all__ = [
    "DynamicsResponse",
    "dynamics_client_response",
]


@pytest.fixture
def dynamics_client(request, _dynamics_client_constructor) -> DynamicsClient:
    if not hasattr(request, "param"):
        yield _dynamics_client_constructor
        return

    with dynamics_client_response(
        _dynamics_client_constructor,
        method=request.param[0],
        response=request.param[1],
        status_code=request.param[2],
    ) as client:
        yield client


class DynamicsResponse:
    """Used in pytest.mark.parametrize to pass used client method,
    response data, and status code to the mocker fixture in a more explicit way.
    """

    def __init__(
        self,
        *,
        method: Literal["get", "post", "patch", "delete"],
        response: Union[list, dict, None],
        status_code: int,
    ):
        self.content = [method, response, status_code]

    def __iter__(self):
        return self

    def __getitem__(self, item):
        return self.content[item]

    def __next__(self):
        return next(self.content)


@contextmanager
def dynamics_client_response(
    client: DynamicsClient,
    *,
    method: Literal["get", "post", "patch", "delete"],
    response: Union[list, dict, None],
    status_code: int,
) -> DynamicsClient:
    """Mock dynamics client response for certain method."""
    with mock.patch(
        f"requests_oauthlib.oauth2_session.OAuth2Session.{method}",
        new_callable=_request_call(response, status_code),
    ):
        yield client


class _RequestMock:
    def __init__(self, params, status_code):
        self.params = params
        self.status_code = status_code

    def json(self):
        return self.params


def _request_call(response, status_code):
    def request_mock(self, url, **kwargs):
        return _RequestMock(response, status_code)

    return lambda: request_mock


@pytest.fixture(scope="session")
def _dynamics_client_constructor():
    with mock.patch("requests_oauthlib.oauth2_session.OAuth2Session.fetch_token", new_callable=mock.PropertyMock):
        with mock.patch("dynamics.utils.SQLiteCache.set", new_callable=mock.PropertyMock):
            dynamics_client = DynamicsClient("", "", "", "", [])
            yield dynamics_client
