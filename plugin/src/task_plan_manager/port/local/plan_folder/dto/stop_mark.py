"""이번 실행에서 사용자가 멈추기로 한 자리 (stop.json).
바깥 차례(rounds) 안의 단계는 앞 차례의 결과를 읽을 수 없어서(선언 검사),
다음 차례가 멈춘 것을 알도록 계획 폴더에 남긴다.
run_id 가 지금 engine 실행과 같을 때만 쓴다. 다음 /plan-run 은 실행 id 가 달라 무시한다 (사용자, 2026-11-20)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StopMark:
    run_id: str  # 멈춘 engine 실행의 id
    reason: str  # failed_stop | prompt_edit | confirm_denied
    node_ids: tuple[int, ...]
    message: str  # 사용자에게 보일 글. 예: "노드 3 에서 멈췄습니다. 이어 하려면 /task_plan_manager:plan-run 7"
