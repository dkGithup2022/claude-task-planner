"""계획 실행(/plan-run)이 지나는 과정. 상태 줄의 셋째 줄 글과 누구 차례인지가 여기서 정해진다."""

from __future__ import annotations

from enum import StrEnum


class RunPhase(StrEnum):
    READY = "ready"  # 승인했고 아직 /plan-run 을 부르기 전
    PROMPTS = "prompts"  # 노드마다 작업 지시를 만드는 중
    NODES = "nodes"  # 노드를 실행하는 중
    CONFIRM = "confirm"  # 확인 노드: 사용자가 결과를 보고 넘어갈지 답할 차례
    FAILED = "failed"  # 실패한 노드를 어떻게 할지 사용자가 고를 차례
    FINISHED = "finished"  # 모든 노드가 끝남
