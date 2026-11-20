from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

from task_plan_server.model.plan_node.plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class PlanNodeCounts:
    """계획의 상태별 노드 수. 계획 목록의 "6/9 (실패 1)" 에 쓴다."""

    todo: int
    running: int
    done: int
    failed: int
    skipped: int

    @classmethod
    def of(cls, statuses: Iterable[PlanNodeStatus]) -> Self:
        """노드 상태들을 세어 만든다."""
        listed = list(statuses)
        return cls(
            listed.count(PlanNodeStatus.TODO),
            listed.count(PlanNodeStatus.RUNNING),
            listed.count(PlanNodeStatus.DONE),
            listed.count(PlanNodeStatus.FAILED),
            listed.count(PlanNodeStatus.SKIPPED),
        )

    @property
    def total(self) -> int:
        return self.todo + self.running + self.done + self.failed + self.skipped
