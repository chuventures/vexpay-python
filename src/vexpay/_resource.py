from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Optional, TypeVar

from pydantic import BaseModel

from ._core import AsyncHttp, Body, QueryValue, RequestOptions, SyncHttp, fill_path
from ._generated.routes import RESPONSE_MODELS, ROUTES

M = TypeVar("M", bound=BaseModel)


def _check_model(operation_id: str, model: type[BaseModel]) -> None:
    expected = RESPONSE_MODELS[operation_id]
    if expected is not None and expected != model.__name__:
        raise TypeError(f"{operation_id} returns {expected}, not {model.__name__}")


def _query(query: Optional[Mapping[str, Any]]) -> Optional[Mapping[str, QueryValue]]:
    return {key: value for key, value in (query or {}).items() if value is not None}


class SyncAPIResource:
    def __init__(self, http: SyncHttp) -> None:
        self._http = http

    def _send(
        self,
        operation_id: str,
        *,
        path: Optional[Mapping[str, str]] = None,
        query: Optional[Mapping[str, Any]] = None,
        body: Body = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        method, template = ROUTES[operation_id]
        return self._http.request(
            method, fill_path(template, path or {}), query=_query(query), body=body, options=options
        )

    def _request_model(self, operation_id: str, model: type[M], **kwargs: Any) -> M:
        _check_model(operation_id, model)
        return model.model_validate(self._send(operation_id, **kwargs))

    def _request_json(self, operation_id: str, **kwargs: Any) -> Any:
        return self._send(operation_id, **kwargs)

    def _request_none(self, operation_id: str, **kwargs: Any) -> None:
        self._send(operation_id, **kwargs)


class AsyncAPIResource:
    def __init__(self, http: AsyncHttp) -> None:
        self._http = http

    async def _send(
        self,
        operation_id: str,
        *,
        path: Optional[Mapping[str, str]] = None,
        query: Optional[Mapping[str, Any]] = None,
        body: Body = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        method, template = ROUTES[operation_id]
        return await self._http.request(
            method, fill_path(template, path or {}), query=_query(query), body=body, options=options
        )

    async def _request_model(self, operation_id: str, model: type[M], **kwargs: Any) -> M:
        _check_model(operation_id, model)
        return model.model_validate(await self._send(operation_id, **kwargs))

    async def _request_json(self, operation_id: str, **kwargs: Any) -> Any:
        return await self._send(operation_id, **kwargs)

    async def _request_none(self, operation_id: str, **kwargs: Any) -> None:
        await self._send(operation_id, **kwargs)
