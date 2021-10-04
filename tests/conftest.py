from contextlib import contextmanager
from unittest import mock

import pytest

from dynamics.client import DynamicsClient
from dynamics.typing import MethodType, Type, Union


__all__ = [
    "ClientResponse",
    "dynamics_client_response",
]

ResponseType = Union[list, dict, None, Type[Exception]]
RequestType = Union[list, dict, None]


@pytest.fixture
def dynamics_client(request, _dynamics_client_constructor) -> DynamicsClient:
    _dynamics_client_constructor.reset_query()
    _dynamics_client_constructor.request_counter = 0

    if not hasattr(request, "param"):
        yield _dynamics_client_constructor
        return

    with dynamics_client_response(
        _dynamics_client_constructor,
        request=request.param[0],
        method=request.param[1],
        response=request.param[2],
        status_code=request.param[3],
    ) as client:
        yield client


class ClientResponse(DynamicsClient):
    """Used in pytest.mark.parametrize to pass used client method,
    request data, and status code to the mocker fixture in a more explicit way.
    """

    # dynamics_client_response saves to these
    expected_response: ResponseType = None
    this_request: RequestType = None

    def __init__(  # noqa
        self,
        *,
        request: RequestType,
        method: MethodType,
        response: ResponseType,
        status_code: int,
    ):
        self.__content = [request, method, response, status_code]

    def __iter__(self):
        return self

    def __getitem__(self, item: int):
        return self.__content[item]

    def __next__(self):
        return next(self.__content)


@contextmanager
def dynamics_client_response(
    client: DynamicsClient,
    *,
    request: RequestType,
    method: MethodType,
    response: ResponseType,
    status_code: int,
) -> DynamicsClient:
    client.expected_response = response
    client.this_request = request
    with mock.patch(
        f"requests_oauthlib.oauth2_session.OAuth2Session.{method}",
        new_callable=_request_mock_call(request, status_code),
    ):
        yield client


class _ResponseMock:
    def __init__(self, request: RequestType, status_code: int):
        self.response = request
        self.status_code = status_code

    def json(self) -> RequestType:
        return self.response


def _request_mock_call(request: RequestType, status_code: int):
    def request_mock(self, url, **kwargs):
        return _ResponseMock(request=request, status_code=status_code)

    return lambda: request_mock


@pytest.fixture(scope="session")
def _dynamics_client_constructor():
    with mock.patch("requests_oauthlib.oauth2_session.OAuth2Session.fetch_token", new_callable=mock.PropertyMock):
        with mock.patch("dynamics.utils.SQLiteCache.set", new_callable=mock.PropertyMock):
            dynamics_client = DynamicsClient("", "", "", "", [])
            yield dynamics_client
