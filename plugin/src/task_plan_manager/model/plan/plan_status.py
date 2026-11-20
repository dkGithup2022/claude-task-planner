"""계획의 상태와 허용하는 바꾸기 (흐름 도식 B 절의 가안)."""

from __future__ import annotations

from enum import StrEnum


class PlanStatus(StrEnum):
    """계획이 어느 단계에 있는지. 예: 확정을 기다리면 REVIEWING."""

    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    APPROVED = "approved"
    REJECTED = "rejected"
    RUNNING = "running"
    DONE = "done"

    def can_move_to(self, to: PlanStatus) -> bool:
        """이 상태에서 to 로 바꿀 수 있는지. 불허(REJECTED)와 끝남(DONE)에서는 바꿀 수 없다."""
        return to in _ALLOWED[self]


_ALLOWED: dict[PlanStatus, tuple[PlanStatus, ...]] = {
    PlanStatus.DRAFTING: (PlanStatus.REVIEWING,),
    PlanStatus.REVIEWING: (PlanStatus.APPROVED, PlanStatus.REJECTED),
    PlanStatus.APPROVED: (PlanStatus.RUNNING,),
    PlanStatus.REJECTED: (),
    PlanStatus.RUNNING: (PlanStatus.DONE,),
    PlanStatus.DONE: (),
}
