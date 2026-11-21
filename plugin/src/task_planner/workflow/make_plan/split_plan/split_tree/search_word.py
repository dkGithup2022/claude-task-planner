"""나누기 판단에서 지식을 찾을 검색어."""

from __future__ import annotations

from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem


def build_search_word(work_item: WorkItem) -> str:
    """나눌지 판단할 작업으로 지식을 찾을 검색어: 작업 이름과 하는 일.
    명령서는 넣지 않는다. 가중치 없이 넣으면 명령서의 낱말이 검색어를 거의 다 차지해,
    한 계획 안의 작업이 모두 같은 지식을 받게 된다 (사용자, 2026-11-21)."""
    return f"{work_item.name} {work_item.scope}"
