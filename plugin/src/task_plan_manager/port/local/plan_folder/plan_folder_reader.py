"""계획 폴더 읽기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.plan.shown_record import ShownRecord
from task_plan_manager.port.local.plan_folder.dto.node_output import NodeOutput
from task_plan_manager.port.local.plan_folder.dto.result_target import ResultTarget
from task_plan_manager.port.local.plan_folder.dto.stop_mark import StopMark


class PlanFolderReader(ABC):
    @abstractmethod
    def list_plan_ids(self) -> tuple[int, ...]:
        """이 작업 폴더의 계획 id (.plan/ 아래 폴더 이름 가운데 정수인 것). 작은 순. 없으면 빈 튜플."""

    @abstractmethod
    def read_command(self, plan_id: int) -> str:
        """명령서 사본. 없으면 PlanFolderMissingError."""

    @abstractmethod
    def read_prompt(self, plan_id: int, node_id: int) -> str | None:
        """노드의 작업 지시. 아직 쓰지 않았으면 None."""

    @abstractmethod
    def result_target(self, plan_id: int, node_id: int) -> ResultTarget:
        """서브에이전트가 쓸 result.md 와 files/ 의 절대 경로. 파일이나 폴더를 만들지는 않는다."""

    @abstractmethod
    def read_output(self, plan_id: int, node_id: int) -> NodeOutput | None:
        """노드의 마지막 회차 결과의 위치와 파일 목록. result.md 가 없으면 None."""

    @abstractmethod
    def read_run(self, plan_id: int, node_id: int) -> NodeRun | None:
        """노드의 실행 기록 (run.json). 없으면 None."""

    @abstractmethod
    def read_shown(self, plan_id: int) -> ShownRecord | None:
        """계획을 보여 준 기록 (shown.json). 아직 보여 주지 않았으면 None."""

    @abstractmethod
    def read_stop(self, plan_id: int) -> StopMark | None:
        """멈추기로 한 자리 (stop.json). 없으면 None. 어느 실행의 것인지는 부르는 쪽이 run_id 로 본다."""
