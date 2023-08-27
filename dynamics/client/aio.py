import asyncio
import logging
from asyncio import iscoroutine
from types import TracebackType

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from httpx import Response

from ..typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    DynamicsClientGetResponse,
    DynamicsClientPatchResponse,
    DynamicsClientPostResponse,
    Optional,
    P,
    PaginationRules,
    T,
    Type,
    Union,
)
from ..utils import Singletons, error_simplification_available, to_coroutine
from .base import BaseDynamicsClient

__all__ = ["DynamicsClient"]


logger = logging.getLogger(__name__)


class DynamicsClient(BaseDynamicsClient):
    oauth_class = AsyncOAuth2Client

    async def _ensure_token(self) -> None:
        if self._oauth_client.token:  # pragma: no cover
            return

        token = await self.get_token()
        async with self._oauth_client._token_refresh_lock:
            if token is None or token.is_expired():  # pragma: no cover
                token = await self._oauth_client.fetch_token(
                    url=self._token_url,
                    grant_type="client_credentials",
                    scope=self._scope,
                    resource=self._resource,
                )
                await self.set_token(token)
            else:  # pragma: no cover
                self._oauth_client.token = token

    async def get_token(self) -> Optional[OAuth2Token]:
        return await Singletons.async_cache().aget(self.cache_key)

    async def set_token(self, token: OAuth2Token) -> None:
        expires = int(token["expires_in"]) - 60
        await Singletons.async_cache().aset(self.cache_key, token, expires)

    async def _handle_pagination(
        self,
        response: DynamicsClientGetResponse,
        pagination_rules: PaginationRules,
        *,
        not_found_ok: bool,
    ) -> None:
        if pagination_rules["pages"] != 0 and response.next_link is not None and len(response.data) == self.pagesize:
            pagination_rules["pages"] -= 1
            rest: DynamicsClientGetResponse = await self.get(
                not_found_ok=not_found_ok,
                pagination_rules=pagination_rules,
                query=response.next_link,
            )
            response.data += rest.data
            response.next_link = rest.next_link

        elif len(response.data) < self.pagesize:
            response.next_link = None

        if "children" not in pagination_rules:
            return

        for page_data in self._paginate_children(response.data, pagination_rules["children"]):
            rest_nested: DynamicsClientGetResponse = await self.get(
                not_found_ok=not_found_ok,
                pagination_rules=page_data.rules,
                query=page_data.query,
            )
            response.data[page_data.index][page_data.key] += rest_nested.data
            if rest_nested.next_link is not None:
                response.data[page_data.index][page_data.column_key] = rest_nested.next_link

    @error_simplification_available
    async def get(
        self,
        *,
        not_found_ok: bool = False,
        pagination_rules: Optional[PaginationRules] = None,
        query: Optional[str] = None,
    ) -> DynamicsClientGetResponse:
        if query is None:
            query = self.current_query

        await self._ensure_token()
        response: Response = await self._oauth_client.get(
            url=query,
            headers={**self.default_headers("get"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        data = self.process_get_response(response, not_found_ok=not_found_ok)
        if pagination_rules is not None:
            await self._handle_pagination(data, pagination_rules, not_found_ok=not_found_ok)
        return data

    @error_simplification_available
    async def post(self, data: Dict[str, Any], *, query: Optional[str] = None) -> DynamicsClientPostResponse:
        if query is None:
            query = self.current_query

        await self._ensure_token()
        response: Response = await self._oauth_client.post(
            url=query,
            json=data,
            headers={**self.default_headers("post"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        return self.process_post_response(response)

    @error_simplification_available
    async def patch(self, data: Dict[str, Any], *, query: Optional[str] = None) -> DynamicsClientPatchResponse:
        if query is None:
            query = self.current_query

        await self._ensure_token()
        response: Response = await self._oauth_client.patch(
            url=query,
            json=data,
            headers={**self.default_headers("patch"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        return self.process_patch_response(response)

    @error_simplification_available
    async def delete(self, *, query: Optional[str] = None) -> None:
        if query is None:
            query = self.current_query

        await self._ensure_token()
        response: Response = await self._oauth_client.delete(
            url=query,
            headers={**self.default_headers("delete"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        return self.process_delete_response(response)

    async def __aenter__(self) -> "DynamicsClient":
        if hasattr(asyncio, "TaskGroup"):  # pragma: no cover; python >=3.11 only
            self.__tg = asyncio.TaskGroup()
            await self.__tg.__aenter__()

        return self

    async def __aexit__(self, exc_type: Optional[Type[Exception]], exc: Exception, traceback: TracebackType) -> None:
        if hasattr(asyncio, "TaskGroup"):  # pragma: no cover; python >=3.11 only
            try:
                await self.__tg.__aexit__(exc_type, exc, traceback)
            finally:
                del self.__tg

    def create_task(
        self,
        method: Union[Callable[P, T], Coroutine[Any, Any, Callable[P, T]]],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> asyncio.Task:
        """Create task when the client is used as an async context manager.

        :param method: Client method to create task for.
        :param args: Positional arguments passed to the method.
        :param kwargs: Keyword arguments passed to the method.
        """

        if method in {self.get, self.post, self.patch, self.delete}:
            kwargs["query"] = self.current_query
        elif not iscoroutine(method):
            method = to_coroutine(method)

        if hasattr(self, "_DynamicsClient__tg"):  # pragma: no cover; python 3.11 only
            return self.__tg.create_task(method(*args, **kwargs))

        return asyncio.create_task(method(*args, **kwargs))
