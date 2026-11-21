"""정의서 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.make_plan.split_plan.write_specs.prompt_spec_need import SpecNeed
from task_planner.workflow.make_plan.split_plan.write_specs.prompt_spec_product import SpecProduct


@dataclass(frozen=True, slots=True)
class SpecOutput:
    name: str  # 트리의 작업 이름 그대로
    does: str  # 이 작업의 목적과 본질적으로 하는 일
    needs: list[SpecNeed]  # 필요한 정보와 출처
    output: SpecProduct  # 산출물의 형태와 담을 것
    notes: str  # 핵심적으로 해야 할 일과 주의할 점
    persona_ids: list[int]  # 개입하는 참여 페르소나 id. HITL 이면 빈 목록
    kind: str  # document / research / code / hitl
