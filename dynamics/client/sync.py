import logging

from authlib.integrations.httpx_client import OAuth2Client
from authlib.oauth2.rfc6749.wrappers import OAuth2Token
from httpx import Response

from ..typing import Any, Dict, List, Optional
from ..utils import Singletons, error_simplification_available
from .base import BaseDynamicsClient

__all__ = ["DynamicsClient"]


logger = logging.getLogger(__name__)


class DynamicsClient(BaseDynamicsClient):
    oauth_class = OAuth2Client

    def _ensure_token(self) -> None:
        if self._oauth_client.token:
            return

        token = self.get_token()
        if token is None or token.is_expired():  # pragma: no cover
            token = self._oauth_client.fetch_token(
                url=self._token_url,
                grant_type="client_credentials",
                scope=self._scope,
                resource=self._resource,
            )
            self.set_token(token)
        else:
            self._oauth_client.token = token

    def get_token(self) -> Optional[OAuth2Token]:
        return Singletons.cache().get(self.cache_key)

    def set_token(self, token: OAuth2Token) -> None:
        expires = int(token["expires_in"]) - 60
        Singletons.cache().set(self.cache_key, token, expires)

    def _handle_pagination(self, entities: List[Dict[str, Any]], not_found_ok: bool) -> None:
        for i, key, query, id_tags in self._iterate_pages(entities):
            new_entities = self.get(not_found_ok=not_found_ok, query=query)
            # If next page includes duplicates based on id tags, filter them out
            new_entities = [value for value in new_entities if value["@odata.etag"] not in id_tags]
            entities[i][key] += new_entities

    @error_simplification_available
    def get(self, *, not_found_ok: bool = False, query: Optional[str] = None) -> List[Dict[str, Any]]:
        if query is None:
            query = self.current_query

        self._ensure_token()
        response: Response = self._oauth_client.get(
            url=query,
            headers={**self.default_headers("get"), **self.headers},
            auth=self._oauth_client.token_auth,
        )
        entities = self.process_get_response(response, not_found_ok)
        self._handle_pagination(entities, not_found_ok)
        return entities

    @error_simplification_available
    def post(self, data: Dict[str, Any], *, query: Optional[str] = None) -> Dict[str, Any]:
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
    def patch(self, data: Dict[str, Any], *, query: Optional[str] = None) -> Dict[str, Any]:
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
