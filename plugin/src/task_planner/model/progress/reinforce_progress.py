"""지식 강화(/plan-go)의 진행. 예: 지식 후보 3번째 / 7개 중, 하위 기획 작성, 본문 초안을 쓰는 중."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.model.progress.reinforce_phase import ReinforcePhase


@dataclass(frozen=True, slots=True)
class ReinforceProgress:
    phase: ReinforcePhase
    index: int | None  # 지금 후보의 번호 (1 부터). 후보를 뽑는 중이면 None
    total: int | None  # 후보 수. 후보를 뽑는 중이면 None
    theme: str | None  # 지금 후보의 작업 이름
    started_at: str | None  # 도구가 일하는 과정이면 그 시작 시각. 사용자 차례면 None
