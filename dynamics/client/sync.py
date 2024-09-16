import logging
from typing import TYPE_CHECKING

from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from ..typing import (
    Any,
    Dict,
    DynamicsClientGetResponse,
    DynamicsClientPatchResponse,
    DynamicsClientPostResponse,
    Optional,
    PaginationRules,
)
from ..utils import Singletons, error_simplification_available
from .base import BaseDynamicsClient

if TYPE_CHECKING:
    from httpx import Response

__all__ = ["DynamicsClient"]


logger = logging.getLogger(__name__)


class DynamicsClient(BaseDynamicsClient):
    oauth_class = OAuth2Client

    def _ensure_token(self) -> None:
        if self._oauth_client.token:
            return

        token: Optional[OAuth2Token] = None
        if self._cache_token:
            token = self.get_token()

        if token is None or token.is_expired(leeway=5):  # pragma: no cover
            token = self._oauth_client.fetch_token(
                url=self._token_url,
                grant_type="client_credentials",
                scope=self._scope,
                resource=self._resource,
            )
            if self._cache_token:
                self.set_token(token)
        else:
            self._oauth_client.token = token

    def get_token(self) -> Optional[OAuth2Token]:
        return Singletons.cache().get(self.cache_key)

    def set_token(self, token: OAuth2Token) -> None:
        expires = int(token["expires_in"]) - 60
        Singletons.cache().set(self.cache_key, token, expires)

    def _handle_pagination(
        self,
        response: DynamicsClientGetResponse,
        pagination_rules: PaginationRules,
        *,
        not_found_ok: bool,
    ) -> None:
        if pagination_rules["pages"] != 0 and response.next_link is not None and len(response.data) == self.pagesize:
            pagination_rules["pages"] -= 1
            rest: DynamicsClientGetResponse = self.get(
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
            rest_nested: DynamicsClientGetResponse = self.get(
                not_found_ok=not_found_ok,
                pagination_rules=page_data.rules,
                query=page_data.query,
            )
            response.data[page_data.index][page_data.key] += rest_nested.data
            if rest_nested.next_link is not None:
                response.data[page_data.index][page_data.column_key] = rest_nested.next_link

    @error_simplification_available
    def get(
        self,
        *,
        not_found_ok: bool = False,
        pagination_rules: Optional[PaginationRules] = None,
        query: Optional[str] = None,
    ) -> DynamicsClientGetResponse:
        if query is None:
            query = self.current_query

        self._ensure_token()
        response: "Response" = self._oauth_client.get(
            url=query,
            headers={**self.default_headers("get"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        data = self.process_get_response(response, not_found_ok=not_found_ok)
        if pagination_rules is not None:
            self._handle_pagination(data, pagination_rules, not_found_ok=not_found_ok)
        return data

    @error_simplification_available
    def post(self, data: Dict[str, Any], *, query: Optional[str] = None) -> DynamicsClientPostResponse:
        if query is None:
            query = self.current_query

        self._ensure_token()
        response = self._oauth_client.post(
            url=query,
            json=data,
            headers={**self.default_headers("post"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        return self.process_post_response(response)

    @error_simplification_available
    def patch(self, data: Dict[str, Any], *, query: Optional[str] = None) -> DynamicsClientPatchResponse:
        if query is None:
            query = self.current_query

        self._ensure_token()
        response = self._oauth_client.patch(
            url=query,
            json=data,
            headers={**self.default_headers("patch"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        return self.process_patch_response(response)

    @error_simplification_available
    def delete(self, *, query: Optional[str] = None) -> None:
        if query is None:
            query = self.current_query

        self._ensure_token()
        response = self._oauth_client.delete(
            url=query,
            headers={**self.default_headers("delete"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        return self.process_delete_response(response)
