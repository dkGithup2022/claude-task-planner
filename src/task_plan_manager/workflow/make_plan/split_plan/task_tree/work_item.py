"""작업 트리의 작업 하나. split_plan 단계 안에서만 쓰는 저장 전 모양."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind


@dataclass(frozen=True, slots=True)
class WorkItem:
    item_key: str  # 트리 안의 위치. 맨 위 "0", 그 자식 "0.1", "0.2", 손자 "0.1.1"
    name: str
    scope: str  # 작업의 목적 한 줄. HITL 이면 확인받을 것
    kind: WorkKind
    depth: int  # 맨 위(명령서 전체)가 0
    parent_key: str | None = None
    why: str = ""  # 이 작업을 나눌지 판단한 근거
    local_id: str | None = None  # 맨 아래 작업에만 붙는 임시 이름표 ("n1", "n2" …). 저장할 때 서버 id 로 바뀐다
