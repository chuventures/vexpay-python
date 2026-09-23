"""Cursor pagination for list endpoints that return ``items`` + ``nextCursor``."""

from __future__ import annotations

from collections.abc import AsyncIterator, Awaitable, Generator, Iterator, Sequence
from typing import Any, Callable, Generic, Optional, TypeVar

from typing_extensions import Protocol


class _CursorPage(Protocol):
    @property
    def items(self) -> Sequence[Any]: ...

    @property
    def nextCursor(self) -> Optional[str]: ...  # noqa: N802 — API field name


P = TypeVar("P", bound=_CursorPage)
I = TypeVar("I")  # noqa: E741

_DEFAULT_LIMIT = 10_000


class SyncPage(Generic[P, I]):
    """First page of a list, fetched on creation. Iterate it to walk every item across pages.

    >>> page = vexpay.merchants.list({"limit": 100})    # doctest: +SKIP
    >>> page.items, page.next_cursor                     # doctest: +SKIP
    >>> for merchant in vexpay.merchants.list():         # doctest: +SKIP
    ...     print(merchant.merchantId)
    """

    def __init__(self, fetch: Callable[[Optional[str]], P], start_cursor: Optional[str] = None) -> None:
        self._fetch = fetch
        self._start_cursor = start_cursor
        #: The first page as returned by the API.
        self.data: P = fetch(start_cursor)

    @property
    def items(self) -> list[I]:
        return list(self.data.items)

    @property
    def next_cursor(self) -> Optional[str]:
        return self.data.nextCursor

    def __iter__(self) -> Iterator[I]:
        page, cursor = self.data, self._start_cursor
        while True:
            yield from page.items
            following = page.nextCursor
            # Stop on the last page, or if the API ever repeats a cursor.
            if not following or following == cursor:
                return
            cursor = following
            page = self._fetch(following)

    def auto_paging_iter(self) -> Iterator[I]:
        return iter(self)

    def to_list(self, limit: int = _DEFAULT_LIMIT) -> list[I]:
        items: list[I] = []
        for item in self:
            items.append(item)
            if len(items) >= limit:
                break
        return items


class AsyncPage(Generic[P, I]):
    """``await`` it for the first page; ``async for`` over it for every item across pages.

    Nothing is sent until it is awaited or iterated.
    """

    def __init__(self, fetch: Callable[[Optional[str]], Awaitable[P]], start_cursor: Optional[str] = None) -> None:
        self._fetch = fetch
        self._start_cursor = start_cursor
        self._first: Optional[P] = None

    async def _first_page(self) -> P:
        if self._first is None:
            self._first = await self._fetch(self._start_cursor)
        return self._first

    def __await__(self) -> Generator[Any, None, P]:
        return self._first_page().__await__()

    async def __aiter__(self) -> AsyncIterator[I]:
        page, cursor = await self._first_page(), self._start_cursor
        while True:
            for item in page.items:
                yield item
            following = page.nextCursor
            if not following or following == cursor:
                return
            cursor = following
            page = await self._fetch(following)

    async def to_list(self, limit: int = _DEFAULT_LIMIT) -> list[I]:
        items: list[I] = []
        async for item in self:
            items.append(item)
            if len(items) >= limit:
                break
        return items
