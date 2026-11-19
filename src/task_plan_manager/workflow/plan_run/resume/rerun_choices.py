"""끊긴 노드를 다시 실행할지 묻는 선택지. ask_rerun 이 묻고 apply_rerun 이 답을 본다.
끊긴 노드를 한 질문에 모아 묻는다. 멈추기를 고르면 어차피 전부 멈추므로
노드마다 물을 까닭이 없다 (사용자, 2026-11-19)."""

from __future__ import annotations

RERUN_ALL = "모두 다시 실행"
STOP = "멈추기"
RERUN_CHOICES = (RERUN_ALL, STOP)
