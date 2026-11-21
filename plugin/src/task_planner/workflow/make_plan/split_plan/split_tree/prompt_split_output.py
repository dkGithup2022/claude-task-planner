"""나누기 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.make_plan.split_plan.split_tree.prompt_split_child import SplitChild


@dataclass(frozen=True, slots=True)
class SplitOutput:
    split: bool  # 이 작업을 더 작은 작업으로 나누는지
    why: str  # 판단 근거 한 문장. 겹쳐서 뺀 것이 있으면 함께
    children: list[SplitChild]  # 나눈 작업들. 나누지 않으면 빈 목록
