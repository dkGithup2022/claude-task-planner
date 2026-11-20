"""계획 노드의 실행 상태. 번들 engine 의 NodeStatus 와 다른 것이라 이름에 Plan 을 붙인다."""

from __future__ import annotations

from enum import StrEnum


class PlanNodeStatus(StrEnum):
    """계획 노드가 실행에서 어디까지 왔는지. 예: 서브에이전트가 도는 중이면 RUNNING."""

    TODO = "todo"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"
