"""작업 지시를 만들지 못한 노드를 다시 만들지 묻는 선택지. ask_retry 가 묻고 retry_prompts 가 답을 본다.
끊긴 노드처럼 한 질문에 모아 묻는다 (사용자, 2026-11-19)."""

from __future__ import annotations

RETRY_ALL = "모두 다시 만들기"
STOP = "멈추기"
RETRY_CHOICES = (RETRY_ALL, STOP)
