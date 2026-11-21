"""작업 지시 만들기에서 지식을 찾을 검색어."""

from __future__ import annotations

from task_plan_manager.model.plan.plan_node import PlanNode


def build_search_word(node: PlanNode) -> str:
    """작업 지시를 쓸 노드로 지식을 찾을 검색어: 제목과 산출물 스펙.
    산출물 스펙의 머리 줄(### 하는 일, ### 산출물, ### 그 외 설명)은 모든 노드에 같아 뺀다."""
    spec_lines = [line for line in node.output_spec.splitlines() if not line.lstrip().startswith("#")]
    return "\n".join([node.title, *spec_lines]).strip()
