"""HTTP 로 JSON 을 보내고 받는다. 새 라이브러리 없이 표준 라이브러리만 쓴다."""

from __future__ import annotations

import http.client
import json
import urllib.error
import urllib.request
from typing import Any

from task_plan_manager.common.http.http_json_error import HttpJsonError

TIMEOUT_SECONDS = 30


def request_json(method: str, url: str, body: Any = None) -> Any:
    """method(GET, POST, PATCH, DELETE)로 url 을 부르고 응답 JSON 을 돌려준다. 응답 글이 비면 None.
    연결 실패, 시간 초과, 응답 도중 끊김, 2xx 가 아닌 응답은 HttpJsonError."""
    data = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=data, method=method, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:  # noqa: S310 — 주소는 설정에서만 온다
            text = response.read().decode("utf-8")
    except urllib.error.HTTPError as failed:
        raise HttpJsonError(
            f"{method} {url} 실패 ({failed.code}): {failed.read().decode('utf-8', 'replace')}"
        ) from failed
    except (urllib.error.URLError, TimeoutError) as failed:
        raise HttpJsonError(f"{method} {url} 에 연결하지 못함: {failed}") from failed
    # urllib 은 연결과 요청 보내기의 에러만 URLError 로 감싼다. 응답을 받는 도중 서버가 끊으면
    # (서버 재시작 등) RemoteDisconnected, ConnectionResetError 가 그대로 나오므로 여기서 잡는다.
    # URLError 도 OSError 의 한 종류라 이 절은 맨 뒤에 둔다
    except (http.client.HTTPException, OSError) as failed:
        raise HttpJsonError(f"{method} {url} 의 응답을 받지 못함: {failed}") from failed
    return json.loads(text) if text.strip() else None
