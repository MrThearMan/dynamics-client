import asyncio
import json
from contextlib import contextmanager
from itertools import cycle as _cycle
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from authlib.oauth2.rfc6749 import OAuth2Token

from .cache import AsyncSQLiteCache, SQLiteCache
from .client import DynamicsClient, aio
from .typing import (
    Any,
    Dict,
    DynamicsClientGetResponse,
    DynamicsClientPatchResponse,
    DynamicsClientPostResponse,
    Generator,
    Iterator,
    MethodType,
    Optional,
    PaginationRules,
    ResponseType,
    Union,
)
from .utils import Singletons

if TYPE_CHECKING:
    from .client.base import BaseDynamicsClient

__all__ = [
    "async_dynamics_cache",
    "async_dynamics_client",
    "AsyncMockClient",
    "BaseMockClient",
    "dynamics_cache",
    "dynamics_client",
    "MockClient",
    "ResponseMock",
]


class ResponseMock:
    def __init__(self, *, response: ResponseType, status_code: int = 200) -> None:
        self.response = response
        self.status_code = status_code

    def json(self) -> ResponseType:
        if isinstance(self.response, Exception):
            raise self.response
        return self.response

    @property
    def text(self) -> str:
        if isinstance(self.response, Exception):
            return str(self.response)
        return json.dumps(self.response)  # pragma: no cover


class BaseMockClient:
    """Base mock client"""

    _mocking_object: Union[MagicMock, AsyncMock]

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        kwargs.setdefault("api_url", "http://dynamics.local/")
        kwargs.setdefault("token_url", "http://token.local")
        kwargs.setdefault("client_id", "client_id")
        kwargs.setdefault("client_secret", "client_secret")
        kwargs.setdefault("scope", ["http://scope.local/"])
        super().__init__(**kwargs)

        self.__len: int = -1
        self.__default_status: int = 200
        self.__internal: bool = False
        self.__response: ResponseType = None
        self.__responses: Iterator[ResponseType] = _cycle([None])
        self.__status_codes: Iterator[int] = _cycle([self.__default_status])
        self.__exceptions: Optional[Iterator[Optional[Exception]]] = None

    def with_responses(self, *responses: ResponseType, cycle: bool = False) -> "BaseMockClient":
        """
        List the responses the client should return, or exceptions it should raise.
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
        """
        Mock the OAuthSession HTTP methods instead of the Dynamics client ones.
        This allows testing of the internal logic of the client in case, e.g.,
        special error handling has been implemented on a client.
        """
        self.__internal = True
        return self

    def with_status_codes(self, *status_codes: int, cycle: bool = False) -> "BaseMockClient":
        """
        Not needed if not using the 'dynamics_client.internal'.

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
        """
        Not needed if not using the 'dynamics_client.internal'.

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
        """
        Not needed if not using the 'dynamics_client.internal'.

        The next exception from the defined list.
        """
        try:
            return next(self.__exceptions)
        except TypeError as error:
            msg = "Cannot call 'next_exception' without setting exceptions first"
            raise TypeError(msg) from error

    @property
    def current_response(self) -> ResponseType:
        """
        Not needed if not using the 'dynamics_client.internal'.

        :return: The last expected response from the client.
                 Tries to correct for some internal logic of the
                 client methods, but might not be correct all the time.
        """
        return self.__response

    def _check_length(self, length: int) -> "BaseMockClient":
        if self.__len not in (length, -1):
            msg = "Mismatching number of arguments given for MockResponse"
            raise ValueError(msg)
        self.__len = length
        return self

    @contextmanager
    def _mock_method(self, method: MethodType) -> Generator[Any, Any, None]:
        try:
            self.__response = next(self.__responses)
        except StopIteration as error:
            msg = "Ran out of responses on the MockClient"
            raise ValueError(msg) from error

        token = OAuth2Token({"expires_in": "60"})
        client_class: "BaseDynamicsClient" = self.__class__.__bases__[-1]  # type: ignore[assigment]
        class_dot_path = f"{client_class.__module__}.{client_class.__qualname__}"
        get_token_path = f"{class_dot_path}.get_token"

        if self.__internal:
            try:
                status_code = next(self.__status_codes)
            except StopIteration as error:
                msg = "Ran out of status codes on the MockClient"
                raise ValueError(msg) from error

            response_mock = ResponseMock(response=self.__response, status_code=status_code)
            if method == "get" and isinstance(self.__response, dict):
                self.__response = self.__response.get("value", [self.__response])

            oauth_dot_path = f"{client_class.oauth_class.__module__}.{client_class.oauth_class.__qualname__}"
            method_path = f"{oauth_dot_path}.{method}"
            yield from self._mock_internal(method_path, get_token_path, token, response_mock)
        else:
            method_path = f"{class_dot_path}.{method}"
            yield from self._mock_external(method_path, get_token_path, token)

    def _mock_internal(
        self,
        method_path: str,
        get_token_path: str,
        token: OAuth2Token,
        side_effect: ResponseMock,
    ) -> Generator[Any, Any, None]:
        with patch(method_path, new_callable=self._mocking_object, side_effect=[side_effect]):  # noqa: SIM117
            with patch(get_token_path, return_value=token):
                yield

    def _mock_external(
        self,
        method_path: str,
        get_token_path: str,
        token: OAuth2Token,
    ) -> Generator[Any, Any, None]:
        with patch(method_path, new_callable=self._mocking_object, side_effect=[self.__response]):  # noqa: SIM117
            with patch(get_token_path, return_value=token):
                yield


class BaseSyncMockClient(BaseMockClient):
    """Base sync mock client"""

    _mocking_object = MagicMock

    def get(
        self,
        *,
        not_found_ok: bool = False,
        pagination_rules: Optional[PaginationRules] = None,
        query: Optional[str] = None,
        **kwargs: Any,
    ) -> DynamicsClientGetResponse:
        with self._mock_method("get"):
            return super().get(
                not_found_ok=not_found_ok,
                pagination_rules=pagination_rules,
                query=query,
                **kwargs,
            )

    def post(
        self,
        data: Dict[str, Any],
        *,
        query: Optional[str] = None,
        **kwargs: Any,
    ) -> DynamicsClientPostResponse:
        with self._mock_method("post"):
            return super().post(data=data, query=query, **kwargs)

    def patch(
        self,
        data: Dict[str, Any],
        *,
        query: Optional[str] = None,
        **kwargs: Any,
    ) -> DynamicsClientPatchResponse:
        with self._mock_method("patch"):
            return super().patch(data=data, query=query, **kwargs)

    def delete(self, *, query: Optional[str] = None, **kwargs: Any) -> None:
        with self._mock_method("delete"):
            return super().delete(query=query, **kwargs)


class BaseASyncMockClient(BaseMockClient):
    """Base async mock client"""

    _mocking_object = AsyncMock

    async def get(
        self,
        *,
        not_found_ok: bool = False,
        pagination_rules: Optional[PaginationRules] = None,
        query: Optional[str] = None,
        **kwargs: Any,
    ) -> DynamicsClientGetResponse:
        with self._mock_method("get"):
            return await super().get(
                not_found_ok=not_found_ok,
                pagination_rules=pagination_rules,
                query=query,
                **kwargs,
            )

    async def post(
        self,
        data: Dict[str, Any],
        *,
        query: Optional[str] = None,
        **kwargs: Any,
    ) -> DynamicsClientPostResponse:
        with self._mock_method("post"):
            return await super().post(data=data, query=query, **kwargs)

    async def patch(
        self,
        data: Dict[str, Any],
        *,
        query: Optional[str] = None,
        **kwargs: Any,
    ) -> DynamicsClientPatchResponse:
        with self._mock_method("patch"):
            return await super().patch(data=data, query=query, **kwargs)

    async def delete(self, *, query: Optional[str] = None, **kwargs: Any) -> None:
        with self._mock_method("delete"):
            return await super().delete(query=query, **kwargs)


class MockClient(BaseSyncMockClient, DynamicsClient):
    """A testing client for the Dynamics client."""


class AsyncMockClient(BaseASyncMockClient, aio.DynamicsClient):
    """A testing client for the Dynamics client."""


@pytest.fixture(scope="session")
def _dynamics_cache_constructor() -> SQLiteCache:  # noqa: PT005
    """Imports the django cache instance or creates a SQLiteCache instance."""
    try:
        from django.core.cache import cache
    except ImportError:
        return Singletons.cache()
    else:  # pragma: no cover
        return cache


@pytest.fixture
def dynamics_cache(_dynamics_cache_constructor: SQLiteCache) -> Generator[SQLiteCache, Any, None]:
    """Get the session instance of either Django's cache or SQLiteCache."""
    _dynamics_cache_constructor.clear()
    try:
        yield _dynamics_cache_constructor
    finally:
        try:
            _dynamics_cache_constructor.clear()
        finally:
            _dynamics_cache_constructor.close()


@pytest.fixture(scope="session")
def _dynamics_async_cache_constructor() -> AsyncSQLiteCache:  # noqa: PT005
    """Imports the django cache instance or creates a SQLiteCache instance."""
    try:
        from django.core.cache import cache
    except ImportError:
        return Singletons.async_cache()
    else:  # pragma: no cover
        return cache


@pytest.fixture
def async_dynamics_cache(_dynamics_async_cache_constructor: AsyncSQLiteCache) -> Generator[AsyncSQLiteCache, Any, None]:
    """Get the session instance of either Django's cache or SQLiteCache."""
    asyncio.run(_dynamics_async_cache_constructor.clear())
    try:
        yield _dynamics_async_cache_constructor
    finally:
        try:
            asyncio.run(_dynamics_async_cache_constructor.clear())
        finally:
            asyncio.run(_dynamics_async_cache_constructor.close())


@pytest.fixture
def dynamics_client(request) -> MockClient:  # noqa: ANN001
    """Get a sync mocked client instance, or forward one created in `pytest.mark.parametrize`."""
    if not hasattr(request, "param"):
        yield MockClient()
    else:
        yield request.param


@pytest.fixture
def async_dynamics_client(request) -> AsyncMockClient:  # noqa: ANN001
    """Get an async mocked client instance, or forward one created in `pytest.mark.parametrize`."""
    if not hasattr(request, "param"):
        yield AsyncMockClient()
    else:
        yield request.param
