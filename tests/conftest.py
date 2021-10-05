from contextlib import contextmanager
from unittest import mock

import pytest

from dynamics.client import DynamicsClient
from dynamics.typing import MethodType, Sequence, Type, Union


__all__ = [
    "ClientResponse",
    "dynamics_client_response",
    "ResponseMock",
]

ResponseType = Union[list, dict, None, Type[Exception]]
RequestType = Union[list, dict, None]


class ResponseMock:
    def __init__(self, *, data: RequestType, status_code: int):
        self.data = data
        self.status_code = status_code

    def json(self) -> RequestType:
        return self.data


@pytest.fixture
def dynamics_client(request, _dynamics_client_constructor) -> DynamicsClient:
    _dynamics_client_constructor.reset_query()
    _dynamics_client_constructor.request_counter = 0

    if not hasattr(request, "param"):
        yield _dynamics_client_constructor
        return

    with dynamics_client_response(
        _dynamics_client_constructor,
        session_response=request.param[0],
        method=request.param[1],
        client_response=request.param[2],
    ) as client:
        yield client


class ClientResponse(DynamicsClient):
    """Used in pytest.mark.parametrize to pass used client method,
    request data, and status code to the mocker fixture in a more explicit way.
    """

    # dynamics_client_response saves to these
    _input_: RequestType = None
    _output_: ResponseType = None

    def __init__(  # noqa
        self,
        *,
        session_response: Union[ResponseMock, Sequence[ResponseMock]],
        method: MethodType,
        client_response: ResponseType,
    ):
        self.__content = [session_response, method, client_response]

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
    session_response: Union[ResponseMock, Sequence[ResponseMock]],
    method: MethodType,
    client_response: ResponseType,
) -> DynamicsClient:
    """Mock dynamics client OAuthSession response for testing HTTP client methods.

    :param client: Client to mock session response for.
    :param session_response: Mocked response, or a series of responses
                             recieved from the OAuthSession when it's called.
    :param method: HTTP client method to mock.
    :param client_response: Expected response from the HTTP client method.
    """

    # Save input and output for usage in testing assertions
    client._input_ = session_response[0].data if isinstance(session_response, Sequence) else session_response.data
    client._output_ = client_response

    with mock.patch(
        f"requests_oauthlib.oauth2_session.OAuth2Session.{method}",
        mock.MagicMock(side_effect=session_response if isinstance(session_response, Sequence) else [session_response]),
    ):
        yield client


@pytest.fixture(scope="session")
def _dynamics_client_constructor():
    with mock.patch("requests_oauthlib.oauth2_session.OAuth2Session.fetch_token", new_callable=mock.PropertyMock):
        with mock.patch("dynamics.utils.SQLiteCache.set", new_callable=mock.PropertyMock):
            dynamics_client = DynamicsClient("", "", "", "", [])
            yield dynamics_client
