"""Generates src/vexpay/_async_resources.py from src/vexpay/_resources.py.

    python scripts/generate_async.py           write the async module
    python scripts/generate_async.py --check   exit 1 if it is stale

Rules (the sync file is written to keep them simple):
  * ``class Foo(SyncAPIResource)``          → ``class AsyncFoo(AsyncAPIResource)``
  * ``= Foo(self._http)``                   → ``= AsyncFoo(self._http)``
  * ``def name(...) -> T:`` methods         → ``async def`` (except list methods returning ``SyncPage[...]``,
                                               which return an ``AsyncPage`` that is awaited/iterated instead)
  * ``return self._request…`` / ``= self._request…`` → ``… await self._request…``
  * ``SyncPage`` → ``AsyncPage``, ``SyncAPIResource`` → ``AsyncAPIResource``
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "src" / "vexpay" / "_resources.py"
TARGET = ROOT / "src" / "vexpay" / "_async_resources.py"

HEADER = '"""Asynchronous resources — generated from ``_resources.py`` by ``scripts/generate_async.py``. Do not edit."""\n'


def transform(source: str) -> str:
    body = source.split('"""', 2)[2].lstrip("\n")  # drop the module docstring

    body = re.sub(r"class (\w+)\(SyncAPIResource\)", r"class Async\1(AsyncAPIResource)", body)
    body = re.sub(r"= ([A-Z]\w*)\(self\._http\)", r"= Async\1(self._http)", body)

    def make_async(match: re.Match[str]) -> str:
        signature = match.group(0)
        if match.group("name") == "__init__" or "SyncPage[" in signature:
            return signature
        return signature.replace("    def ", "    async def ", 1)

    body = re.sub(
        r"    def (?P<name>\w+)\(.*?\) -> [^\n]*?:\n",
        make_async,
        body,
        flags=re.DOTALL,
    )
    body = re.sub(r"return self\._request", "return await self._request", body)
    body = re.sub(r"= self\._request_json\(", "= await self._request_json(", body)
    body = body.replace("SyncPage", "AsyncPage").replace("SyncAPIResource", "AsyncAPIResource")
    return HEADER + "\n" + body


def main() -> int:
    generated = transform(SOURCE.read_text(encoding="utf-8"))
    if "--check" in sys.argv:
        current = TARGET.read_text(encoding="utf-8") if TARGET.exists() else ""
        if current != generated:
            print("src/vexpay/_async_resources.py is stale — run: python scripts/generate_async.py", file=sys.stderr)
            return 1
        print("async resources up to date")
        return 0
    TARGET.write_text(generated, encoding="utf-8")
    print(f"wrote {TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
