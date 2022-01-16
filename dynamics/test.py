import json
from contextlib import contextmanager
from typing import Any, Dict
from unittest.mock import patch

import pytest
from typing_extensions import Literal

from .client import DynamicsClient
from .typing import List, MethodType, Sequence, Type, Union


__all__ = [
    "dynamics_cache_constructor",
    "dynamics_cache",
    "dynamics_client_constructor",
    "dynamics_client",
    "ResponseMock",
    "ClientResponse",
    "dynamics_client_response",
    "dynamics_client_response_mirror",
]


JsonType = Union[Dict[str, Any], List[Dict[str, Any]], None]
RequestType = Union["ResponseMock", Sequence["ResponseMock"], Exception]
ResponseType = Union[JsonType, Type[Exception]]


@pytest.fixture(scope="session")
def dynamics_cache_constructor():
    """Imports the django cache instance or creates a SQLiteCache instance."""
    try:
        from django.core.cache import cache  # pylint: disable=C0415,W0621
    except ImportError:
        from dynamics.utils import SQLiteCache  # pylint: disable=C0415,W0621

        cache = SQLiteCache()

    return cache


@pytest.fixture()
def dynamics_cache(dynamics_cache_constructor):  # pylint: disable=W0621
    """Imports the django cache instance or creates a SQLiteCache instance."""
    dynamics_cache_constructor.clear()
    yield dynamics_cache_constructor


@pytest.fixture(scope="session")
def dynamics_client_constructor(dynamics_cache_constructor):  # pylint: disable=W0621,W0613
    """Creates a mocked dynamics client for the session."""

    with patch("requests_oauthlib.oauth2_session.OAuth2Session.fetch_token"), patch("dynamics.client.set_token"):
        yield DynamicsClient("", "", "", "", [])


@pytest.fixture
def dynamics_client(request, dynamics_client_constructor) -> DynamicsClient:  # pylint: disable=W0621
    """Mocked dynamics client. Use with 'ClientResponse' object
    or 'dynamics_client_response' context manager.
    """

    dynamics_client_constructor.reset_query()
    dynamics_client_constructor.request_counter = 0

    if not hasattr(request, "param"):
        yield dynamics_client_constructor
        return

    with dynamics_client_response(
        dynamics_client_constructor,
        session_response=request.param[0],
        method=request.param[1],
        client_response=request.param[2],
    ) as client:
        yield client


class ResponseMock:
    """A mock object for a requests Response. Used with ClientResponse."""

    def __init__(self, *, data: JsonType, status_code: int):
        self.data = data
        self.status_code = status_code

    def json(self) -> JsonType:
        return self.data


class ClientResponse(DynamicsClient):
    def __init__(  # noqa pylint: disable=W0231
        self,
        *,
        session_response: RequestType,
        method: MethodType,
        client_response: ResponseType,
    ):
        r"""Used with pytest.mark.parametrize and ResponseMock to mock
        how the Dynamics client will respond to requests. Here is an example::

            @pytest.mark.parametrize(
                "dynamics_client",
                [
                    ClientResponse(
                        session_response=ResponseMock(data={"foo": "bar"}, status_code=200),
                        method="get",
                        client_response=[{"foo": "bar"}],
                    ),
                ],
                indirect=True,  # important!
            )
            def test_foo(dynamics_client):
                assert dynamics_client.get() == dynamics_client._output_

        :param session_response: What the OAuth2 session should be. This can be a single ResponseMock
                                 object, a sequence of ResponseMock objects, or an Exception.
                                 This is saved under '_input_' attribute on the client parameter.
        :param method: What OAuth2 session method should be mocked.
                       This is also saved under '_method_' attribute on the client parameter.
        :param client_response: What the DynamicsClient expected response is. The client does some
                                processing on the OAuth2 response, so this may not be the same as that.
                                It may also be an exception, in which case the error message from dynamics
                                is used as the exception message (unless 'simplify_errors' is used).
                                This is saved under '_output_' attribute on the client parameter.
        """

        self._input_ = session_response
        """'session_response' is saved to this for use in testing."""
        self._output_ = client_response
        """'client_response' is saved to this for use in testing."""
        self._method_ = method
        """'method' is saved to this for use in testing."""

        self.__content = [session_response, method, client_response]

    def __iter__(self):  # pylint: disable=E0301
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
    client._input_ = session_response  # pylint: disable=W0212
    client._output_ = client_response  # pylint: disable=W0212
    client._method_ = method  # pylint: disable=W0212

    # Make side_effect a list so that ResponseMock is returned and not called
    side_effect = [session_response] if isinstance(session_response, ResponseMock) else session_response

    with patch(f"requests_oauthlib.oauth2_session.OAuth2Session.{method}", side_effect=side_effect):
        yield client


@contextmanager
def dynamics_client_response_mirror(client: DynamicsClient, *, method: Literal["post", "patch"]) -> DynamicsClient:
    """Make OAuthSessionClient mirror any post or patch data given to it."""

    def mirror(url: str, data: bytes, headers: Dict[str, Any]) -> ResponseMock:  # pylint: disable=W0613
        return ResponseMock(data=json.loads(data.decode()), status_code=200)

    with patch(f"requests_oauthlib.oauth2_session.OAuth2Session.{method}", side_effect=mirror):
        yield client
