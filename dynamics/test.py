from contextlib import contextmanager
from copy import deepcopy
from itertools import cycle as _cycle
from unittest.mock import patch

import pytest

from .client import DynamicsClient
from .typing import Any, Dict, Iterator, List, MethodType, Optional, ResponseType


__all__ = [
    "MockClient",
    "BaseMockClient",
    "dynamics_cache",
    "dynamics_client",
]


class BaseMockClient:
    def __init__(self):
        with patch("dynamics.client.get_token"):
            super().__init__("", "", "", "", [])

        self.__len: int = -1
        self.__default_status: int = 200
        self.__internal: bool = False
        self.__response: ResponseType = None
        self.__responses: Iterator[ResponseType] = _cycle([None])
        self.__status_codes: Iterator[int] = _cycle([self.__default_status])
        self.__exceptions: Optional[Iterator[Optional[Exception]]] = None

    def with_responses(self, *responses: ResponseType, cycle: bool = False) -> "BaseMockClient":
        """List the responses the client should return, or exceptions it should raise.
        When the client uses one of its HTTP methods (get, post, patch, delete),
        the responses from the list given here are patched to those methods
        in the order they are given.

        :param responses: The list of responses in the order they should be used.
        :param cycle: Cycle the given responses when the list is exhausted.
        :return: The current instance of the MockClient.
        """
        self._check_length(len(responses))
        self.__responses = _cycle(responses) if cycle else iter(responses)
        return self

    # These are tools for testing internal behaviour

    @property
    def internal(self) -> "BaseMockClient":
        """Mock the OAuthSession HTTP methods instead of the Dynamics client ones.
        This allows testing of the internal logic of the client in case, e.g.,
        special error handling has been implemented on a client.
        """
        self.__internal = True
        return self

    def with_status_codes(self, *status_codes: int, cycle: bool = False) -> "BaseMockClient":
        """Not needed if not using the 'dynamics_client.internal'.

        List the status codes the OAuthSession should return. When the client uses one of its
        HTTP methods (get, post, patch, delete), the status code from the list given here
        are patched to the OAuthSession response in those methods in the order they are given.

        :param status_codes: List of status codes in the order they should be used.
        :param cycle: Cycle the given status codes when the list is exhausted.
        :return: The current instance of the MockClient.
        """
        self._check_length(len(status_codes))
        self.__status_codes = _cycle(status_codes) if cycle else iter(status_codes)
        return self

    def with_exceptions(self, *exceptions: Exception, cycle: bool = False) -> "BaseMockClient":
        """Not needed if not using the 'dynamics_client.internal'.

        List the exceptions the client should raise based on what the OAuthSession returned.
        After setting the responses and status codes, the exceptions here can be used to verify that
        those responses and status codes produce a given exception. This way the exceptions can be set
        ahead of time, e.g., when using `pytest.mark.parametrize`. The exceptions are accessible from
        `dynamics_client.next_exception`, one at a time.

        When the client uses one of its HTTP methods (get, post, patch, delete),
        the status code from the list given here are patched to the OAuthSession response
        in those methods in the order they are given.

        :param exceptions: List of exceptions in the order they should be raised.
        :param cycle: Cycle the given exceptions when the list is exhausted.
        :return: The current instance of the MockClient.
        """
        self._check_length(len(exceptions))
        self.__exceptions = _cycle(exceptions) if cycle else iter(exceptions)
        return self

    @property
    def next_exception(self) -> Exception:
        """Not needed if not using the 'dynamics_client.internal'.

        The next exception from the defined list.
        """
        try:
            return next(self.__exceptions)
        except TypeError as error:
            raise TypeError("Cannot call 'next_exception' without setting exceptions first") from error

    @property
    def current_response(self) -> ResponseType:
        """Not needed if not using the 'dynamics_client.internal'.

        :return: The last expected reponse from the client.
                 Tries to correct for some of the internal logic of the
                 client methods, but might not be correct all of the time.
        """
        return self.__response

    def _check_length(self, length: int) -> "BaseMockClient":
        if self.__len != -1 and length != self.__len:
            raise ValueError("Mismaching number of arguments given for MockResponse")
        self.__len = length
        return self

    @contextmanager
    def _mock_method(self, method: MethodType):
        try:
            self.__response = next(self.__responses)
        except StopIteration as error:
            raise ValueError("Ran out of responses on the MockClient") from error

        if self.__internal:
            try:
                status_code = next(self.__status_codes)
            except StopIteration as error:
                raise ValueError("Ran out of status codes on the MockClient") from error

            response_mock = ResponseMock(response=deepcopy(self.__response), status_code=status_code)

            if method == "get" and isinstance(self.__response, dict):
                self.__response = self.__response.get("value", [self.__response])

            with patch(f"requests_oauthlib.oauth2_session.OAuth2Session.{method}", side_effect=[response_mock]):
                yield
        else:

            client_class = self.__class__.__bases__[-1]
            class_dot_path = f"{client_class.__module__}.{client_class.__qualname__}"

            with patch(f"{class_dot_path}.{method}", side_effect=[self.__response]):
                yield

    def get(self, not_found_ok: bool = False, next_link: Optional[str] = None, **kwargs) -> List[Dict[str, Any]]:
        with self._mock_method("get"):
            return super().get(not_found_ok=not_found_ok, next_link=next_link, **kwargs)  # noqa pylint: disable=E1101

    def post(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        with self._mock_method("post"):
            return super().post(data=data, **kwargs)  # noqa pylint: disable=E1101

    def patch(self, data: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        with self._mock_method("patch"):
            return super().patch(data=data, **kwargs)  # noqa pylint: disable=E1101

    def delete(self, **kwargs) -> None:
        with self._mock_method("delete"):
            return super().delete(**kwargs)  # noqa pylint: disable=E1101


class MockClient(BaseMockClient, DynamicsClient):
    r"""A testing client for the Dynamics client.

    -----------------------------------------------------------

    Can be used with `pytest.mark.parametrize`::

        @pytest.mark.parametrize(
            "dynamics_client",
            [
                MockClient().with_responses({"foo": "bar"}),
                MockClient().with_responses({"foo": "baz"}),
            ],
            indirect=True,  # important!
        )
        def test_foo(dynamics_client):
            x = dynamics_client.get()

    -----------------------------------------------------------

    Can also be used without `pytest.mark.parametrize`::

        def test_foo(dynamics_client):
            dynamics_client.with_responses({"foo": "bar"})

            x = dynamics_client.get()

    -----------------------------------------------------------
    """


@pytest.fixture(scope="session")
def _dynamics_cache_constructor():
    """Imports the django cache instance or creates a SQLiteCache instance."""
    try:
        from django.core.cache import cache  # pylint: disable=C0415,W0621
    except ImportError:
        from dynamics.utils import SQLiteCache  # pylint: disable=C0415,W0621

        cache = SQLiteCache()

    return cache


@pytest.fixture()
def dynamics_cache(_dynamics_cache_constructor):  # pylint: disable=W0621
    """Get the session instance of either Django's cache or SQLiteCache."""
    _dynamics_cache_constructor.clear()
    yield _dynamics_cache_constructor


@pytest.fixture
def dynamics_client(request) -> MockClient:  # pylint: disable=W0621
    """Get a mocked client instance, or forward one created in `pytest.mark.parametrize`."""
    if not hasattr(request, "param"):
        yield MockClient()
    else:
        yield request.param


class ResponseMock:
    def __init__(self, *, response: ResponseType, status_code: int = 200):
        self.response = response
        self.status_code = status_code

    def json(self):
        if isinstance(self.response, Exception):
            raise self.response
        return self.response
