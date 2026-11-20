"""노드 하나의 작업 지시를 만들지 못함. 메시지는 실패 이유로 사용자에게 보인다."""

from __future__ import annotations


class NodePromptError(RuntimeError):
    pass
