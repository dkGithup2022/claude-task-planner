"""request_json: 서버가 연결을 받은 뒤 응답 없이 끊어도 HttpJsonError 로 나오는지 본다."""

import socket
import threading

import pytest

from task_planner.common.http.http_json import request_json
from task_planner.common.http.http_json_error import HttpJsonError


def _start_server_that_closes_after_request() -> int:
    """요청을 받고 아무 응답 없이 연결을 닫는 서버를 띄우고 포트를 돌려준다 (서버가 답하기 전에 꺼진 경우)."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)

    def accept_and_close() -> None:
        connection, _ = listener.accept()
        connection.recv(65536)
        connection.close()
        listener.close()

    threading.Thread(target=accept_and_close, daemon=True).start()
    return int(listener.getsockname()[1])


def test_should_raise_http_json_error_when_server_closes_without_response():
    port = _start_server_that_closes_after_request()

    with pytest.raises(HttpJsonError, match="의 응답을 받지 못함"):
        request_json("POST", f"http://127.0.0.1:{port}/api/memories/search", {"query": "설계"})
