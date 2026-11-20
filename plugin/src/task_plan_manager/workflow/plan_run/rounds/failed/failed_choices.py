"""실패한 노드를 어떻게 할지 묻는 선택지 (도식화 D 5 단계)."""

from __future__ import annotations

RERUN = "다시 실행"
EDIT_AND_RERUN = "작업 지시를 고쳐 다시"
SKIP = "건너뛰기"
STOP = "멈추기"
FAILED_CHOICES = (RERUN, EDIT_AND_RERUN, SKIP, STOP)
