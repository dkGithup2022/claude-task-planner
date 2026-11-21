"""HTTP 로 JSON 을 주고받지 못함."""

from __future__ import annotations


class HttpJsonError(RuntimeError):
    """메시지에 방법, 주소, 상태 코드(있으면), 응답 글을 담는다."""
