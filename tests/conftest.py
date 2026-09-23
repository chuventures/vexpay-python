from __future__ import annotations

import json
import threading
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Optional, Union

import pytest


@dataclass
class Scripted:
    status: int
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    delay: float = 0.0


@dataclass
class Recorded:
    method: str
    path: str
    headers: dict[str, str]
    body: Any


Handler = Callable[[Recorded, int], Scripted]


class MockServer:
    """Real HTTP server with one scripted answer per request (the last one repeats)."""

    def __init__(self) -> None:
        self.requests: list[Recorded] = []
        self._handler: Handler = lambda _req, _i: Scripted(200, {})
        server = self

        class _RequestHandler(BaseHTTPRequestHandler):
            def log_message(self, *_args: Any) -> None:
                pass

            def _handle(self) -> None:
                length = int(self.headers.get("content-length") or 0)
                raw = self.rfile.read(length) if length else b""
                recorded = Recorded(
                    method=self.command,
                    path=self.path,
                    headers={k.lower(): v for k, v in self.headers.items()},
                    body=json.loads(raw) if raw else None,
                )
                index = len(server.requests)
                server.requests.append(recorded)
                answer = server._handler(recorded, index)
                if answer.delay:
                    time.sleep(answer.delay)
                payload = b"" if answer.body is None else json.dumps(answer.body).encode()
                try:
                    self.send_response(answer.status)
                    self.send_header("content-type", "application/json")
                    self.send_header("content-length", str(len(payload)))
                    for key, value in answer.headers.items():
                        self.send_header(key, value)
                    self.end_headers()
                    self.wfile.write(payload)
                except (BrokenPipeError, ConnectionResetError):
                    pass

            do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = _handle

        self._httpd = ThreadingHTTPServer(("127.0.0.1", 0), _RequestHandler)
        self._httpd.daemon_threads = True
        self.url = f"http://127.0.0.1:{self._httpd.server_address[1]}"
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()

    def script(self, answers: Union[list[Scripted], Handler]) -> None:
        if callable(answers):
            self._handler = answers
        else:
            self._handler = lambda _req, i: answers[min(i, len(answers) - 1)]

    def close(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()


@pytest.fixture
def server() -> Iterator[MockServer]:
    mock = MockServer()
    yield mock
    mock.close()


def sleeps_recorder() -> tuple[list[float], Callable[[float], None]]:
    recorded: list[float] = []
    return recorded, recorded.append


def async_sleeps_recorder() -> tuple[list[float], Callable[[float], Any]]:
    recorded: list[float] = []

    async def sleep(seconds: float) -> None:
        recorded.append(seconds)

    return recorded, sleep


def first(items: list[Recorded], key: str) -> Optional[str]:
    return items[0].headers.get(key) if items else None
