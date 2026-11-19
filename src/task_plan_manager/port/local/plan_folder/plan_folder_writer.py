"""계획 폴더 쓰기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.model.node_run.node_run import NodeRun
from task_plan_manager.model.plan.shown_record import ShownRecord


class PlanFolderWriter(ABC):
    @abstractmethod
    def create_plan(self, plan_id: int, command_md: str) -> None:
        """계획 폴더와 command.md 를 만든다. 같은 내용이면 그대로, 다른 내용이 있으면 PlanFolderExistsError."""

    @abstractmethod
    def write_prompt(self, plan_id: int, node_id: int, text: str) -> None:
        """노드의 작업 지시를 쓴다. 노드 폴더가 없으면 이때 만든다."""

    @abstractmethod
    def save_run(self, plan_id: int, node_id: int, run: NodeRun) -> None:
        """노드의 실행 기록을 덮어쓴다."""

    @abstractmethod
    def archive_round(self, plan_id: int, node_id: int) -> int:
        """다시 실행하기 전에 지금 회차의 파일을 runs/<회차>/ 로 보관하고 새 회차 번호를 돌려준다.
        prompt.md 는 복사하고(다시 실행에도 쓰므로), result.md 와 files/ 는 옮긴다.
        run.json 의 회차도 올려 저장한다 (상태는 todo). 그래서 연달아 불러도 앞 회차를 덮어쓰지 않는다."""

    @abstractmethod
    def save_shown(self, plan_id: int, record: ShownRecord) -> None:
        """계획을 보여 준 기록을 덮어쓴다. 마지막으로 보여 준 때가 기준이다."""
