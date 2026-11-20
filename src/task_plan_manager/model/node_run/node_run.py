"""노드 하나의 로컬 실행 기록 (run.json). 회차와 확인한 말처럼 계획 저장소에 없는 것을 담는다."""

from __future__ import annotations

from dataclasses import dataclass, replace

from task_plan_manager.model.node_run.read_input import ReadInput
from task_plan_manager.model.plan.plan_node_status import PlanNodeStatus


@dataclass(frozen=True, slots=True)
class NodeRun:
    round: int  # 몇 번째 실행인지. 다시 실행할 때 올린다
    status: PlanNodeStatus  # 계획 저장소의 노드 상태와 같은 값. 원본은 계획 저장소
    started_at: str | None = None
    finished_at: str | None = None
    read_inputs: tuple[ReadInput, ...] = ()
    confirm: str | None = None  # 확인 노드면 사용자가 한 말
    skipped_reason: str | None = None  # 건너뛰었으면 사용자와 정한 이유
    failed_reason: str | None = None  # 실패했으면 이유. 예: "막힘", "결과 파일 없음"
    failed_summary: str | None = None  # 실패했을 때 claude -p 답의 요약

    def start(self, now: str, read_inputs: tuple[ReadInput, ...]) -> NodeRun:
        """실행 중으로 바꾸고 이 회차에 읽은 선행 노드를 남긴 새 기록. 지난 실패 이유는 비운다."""
        return replace(
            self,
            status=PlanNodeStatus.RUNNING,
            started_at=now,
            finished_at=None,
            read_inputs=read_inputs,
            failed_reason=None,
            failed_summary=None,
        )

    def finish(self, status: PlanNodeStatus, now: str) -> NodeRun:
        """끝난 상태(완료, 실패, 건너뜀)와 끝난 시각을 넣은 새 기록."""
        return replace(self, status=status, finished_at=now)

    def back_to_todo(self) -> NodeRun:
        """다시 실행할 할 일로 되돌린 새 기록. 회차는 그대로 둔다 (다음 시작 때 정한다)."""
        return replace(self, status=PlanNodeStatus.TODO, started_at=None, finished_at=None)
