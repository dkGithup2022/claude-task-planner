"""포트 시험의 가짜 서버. 정해 둔 (방법, 경로) 에 정해 둔 응답을 주고, 받은 요청을 남긴다."""

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any


class FakeApiServer:
    def __init__(self) -> None:
        self.responses: dict[tuple[str, str], tuple[int, Any]] = {}
        self.requests: list[tuple[str, str, Any]] = []  # (방법, 경로, 본문)
        self._server = HTTPServer(("127.0.0.1", 0), self._handler_class())
        self.url = f"http://127.0.0.1:{self._server.server_port}"
        threading.Thread(target=self._server.serve_forever, daemon=True).start()

    def answer(self, method: str, path: str, body: Any, status: int = 200) -> None:
        self.responses[(method, path)] = (status, body)

    def stop(self) -> None:
        self._server.shutdown()

    def _handler_class(self) -> type[BaseHTTPRequestHandler]:
        fake = self

        class Handler(BaseHTTPRequestHandler):
            def _reply(self) -> None:
                length = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(length)) if length else None
                fake.requests.append((self.command, self.path, body))
                status, answer = fake.responses.get((self.command, self.path), (404, {"error": "없는 경로"}))
                payload = b"" if answer is None else json.dumps(answer, ensure_ascii=False).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_PATCH = do_DELETE = _reply

            def log_message(self, *args: Any) -> None:
                pass

        return Handler


import pytest  # noqa: E402


@pytest.fixture
def fake_api(monkeypatch):
    """서버 구현을 쓰게 환경 변수를 바꾸고 가짜 서버를 띄운다."""
    server = FakeApiServer()
    monkeypatch.setenv("TASK_PLAN_MANAGER_API", "server")
    monkeypatch.setenv("TASK_PLAN_MANAGER_API_URL", server.url)
    yield server
    server.stop()
