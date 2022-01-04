import json
from contextlib import contextmanager
from unittest import mock

import pytest

from dynamics.client import DynamicsClient
from dynamics.typing import Any, Callable, Dict, List, Literal, MethodType, Sequence, Type, Union
from dynamics.utils import SQLiteCache


__all__ = [
    "ClientResponse",
    "dynamics_client_response",
    "dynamics_client_response_mirror",
    "ResponseMock",
]

JsonType = Union[Dict[str, Any], List[Dict[str, Any]], None]
RequestType = Union["ResponseMock", Sequence["ResponseMock"], None, Exception]
ResponseType = Union[JsonType, Type[Exception]]


@pytest.fixture(scope="session")
def cache():
    return SQLiteCache()


@pytest.fixture(scope="session")
def _dynamics_client_constructor(cache):
    patch: Any

    def no_token_caching(key: str, value: Any, timeout: int = cache.DEFAULT_TIMEOUT):
        if key != "dynamics-client-token":
            patch.stop()
            cache.set(key, value, timeout)
            patch.start()

    with mock.patch("requests_oauthlib.oauth2_session.OAuth2Session.fetch_token", new_callable=mock.PropertyMock):
        patch = mock.patch("dynamics.utils.SQLiteCache.set", mock.MagicMock(side_effect=no_token_caching))
        patch.start()
        dynamics_client = DynamicsClient("", "", "", "", [])
        yield dynamics_client
        try:
            patch.stop()
        except RuntimeError:
            pass


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


class ResponseMock:
    def __init__(self, *, data: JsonType, status_code: int):
        self.data = data
        self.status_code = status_code

    def json(self) -> JsonType:
        return self.data


class ClientResponse(DynamicsClient):
    def __init__(self, *, session_response: RequestType, method: MethodType, client_response: ResponseType):  # noqa
        """Used in pytest.mark.parametrize to pass used client method,
        request data, and status code to the mocker fixture in a more explicit way.

        :param session_response: What the oauth2 session should return.
        :param method: What oauth2 session method should be called.
        :param client_response: What the dynamics client expected response is.
        """

        self._input_ = session_response
        """'session_response' is saved to this for use in testing."""
        self._output_ = client_response
        """'client_response' is save to this for use in testing."""
        self._method_ = method
        """'method' is save to this for use in testing."""

        self.__content = [session_response, method, client_response]

    def __iter__(self):
        return self

    def __getitem__(self, item: int):
        return self.__content[item]


@contextmanager
def dynamics_client_response(
    client: DynamicsClient,
    *,
    session_response: RequestType,
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

    # Save these to the client for usage in testing assertions
    client._input_ = session_response
    client._output_ = client_response
    client._method_ = method

    # Make side_effect a list so that ResponseMock is returned and not called
    side_effect = [session_response] if isinstance(session_response, ResponseMock) else session_response

    with mock.patch(
        f"requests_oauthlib.oauth2_session.OAuth2Session.{method}",
        mock.MagicMock(side_effect=side_effect),
    ):
        yield client


@contextmanager
def dynamics_client_response_mirror(client: DynamicsClient, *, method: Literal["post", "patch"]) -> DynamicsClient:
    """Make OAuthSessionClient mirror any post or patch data given to it."""

    def mirror(url: str, data: bytes, headers: Dict[str, Any]) -> ResponseMock:
        return ResponseMock(data=json.loads(data.decode()), status_code=200)

    with mock.patch(
        f"requests_oauthlib.oauth2_session.OAuth2Session.{method}",
        mock.MagicMock(side_effect=mirror),
    ):
        yield client
