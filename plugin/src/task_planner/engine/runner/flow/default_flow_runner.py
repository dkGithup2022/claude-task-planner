"""DefaultFlowRunner: 명령(start, next, done, cancel)마다 상태를 읽고, 진행하고, 저장한다."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime

from task_planner.engine.instruction.instruction import Instruction
from task_planner.engine.instruction.instruction_type import InstructionType
from task_planner.engine.model.history.history_entry import HistoryEntry
from task_planner.engine.model.run_state.flow_run_state import FlowRunState
from task_planner.engine.model.run_state.flow_run_status import FlowRunStatus
from task_planner.engine.model.run_state.node_status import NodeStatus
from task_planner.engine.model.session.claude_session import ClaudeSession
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.performer.task_performer import TaskPerformer
from task_planner.engine.port.history.history_writer import HistoryWriter
from task_planner.engine.port.run_state.run_state_reader import RunStateReader
from task_planner.engine.port.run_state.run_state_writer import RunStateWriter
from task_planner.engine.port.session.session_reader import SessionReader
from task_planner.engine.port.session.session_writer import SessionWriter
from task_planner.engine.runner.flow.flow_registry import FlowRegistry
from task_planner.engine.runner.flow.flow_runner import FlowRunner
from task_planner.engine.runner.scenario.build_scenario import build_scenario
from task_planner.engine.runner.scenario.check_definition import check_definition
from task_planner.engine.runner.unit.scenario_status import _find_uuid, _reset_failed, now
from task_planner.engine.runner.unit.unit_runner import UnitRunner


class DefaultFlowRunner(FlowRunner):
    def __init__(self, flows: FlowRegistry, session_reader: SessionReader, session_writer: SessionWriter,
                 run_state_reader: RunStateReader, run_state_writer: RunStateWriter, unit_runner: UnitRunner,
                 performers: Mapping[PerformedBy, TaskPerformer], history_writer: HistoryWriter) -> None:  # fmt: skip
        self.flows, self.unit_runner, self.performers = flows, unit_runner, performers
        self.history_writer = history_writer
        self.session_reader, self.session_writer = session_reader, session_writer
        self.run_state_reader, self.run_state_writer = run_state_reader, run_state_writer

    def start(self, session: ClaudeSession, flow_name: str) -> Instruction:
        try:
            definition = self.flows.get(flow_name)
        except KeyError as e:
            return Instruction.failed(str(e.args[0]))
        problems = check_definition(definition.root, self.performers.keys())
        if problems:
            return Instruction.failed("실행을 시작하지 않았습니다.\n" + "\n".join(f"- {p}" for p in problems))
        t = now()
        state = FlowRunState(run_id=self._new_run_id(session.session_id), flow_name=flow_name,
                             session_id=session.session_id, status=FlowRunStatus.RUNNING, created_at=t, updated_at=t,
                             scenario=build_scenario(definition.root), waiting_instruction=None)  # fmt: skip
        self.run_state_writer.save_run(state)
        saved = self.session_reader.load_session(session.session_id) or session  # 훅이 적은 대화 기록 경로를 지킴
        saved.active_run_id, saved.updated_at = state.run_id, t
        self.session_writer.save_session(saved)
        return self._advance(session, state)

    def _new_run_id(self, session_id: str) -> str:
        """r_<UTC 초>. 같은 초에 이미 있으면 _2, _3 … 을 붙인다."""
        base = "r_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        run_id, n = base, 1
        while self._run_exists(session_id, run_id):
            n += 1
            run_id = f"{base}_{n}"
        return run_id

    def _run_exists(self, session_id: str, run_id: str) -> bool:
        try:
            self.run_state_reader.load_run(session_id, run_id)
        except FileNotFoundError:
            return False
        return True

    def next_instruction(self, session: ClaudeSession) -> Instruction:
        state = self.read_state(session)
        if state is None:
            text = "진행 중인 실행이 없습니다. " + "task-planner start <워크플로 이름> 으로 시작하세요."
            return Instruction.failed(text)
        busy = self._check_executing(state)
        if busy is not None:
            return busy
        self._recover(state)
        if state.waiting_instruction is not None:  # 기다리던 지시를 그대로 다시
            return state.waiting_instruction
        return self._advance(session, state)

    def submit_reply(self, session: ClaudeSession, reply: str | None) -> Instruction:
        state = self.read_state(session)
        if state is None or state.waiting_instruction is None:
            busy = self._check_executing(state) if state is not None else None
            return busy or Instruction.failed("기다리는 지시가 없습니다. task-planner next 를 부르세요.")
        self._recover(state)
        again = self.unit_runner.submit_reply(state, reply)
        if again is not None:  # 다시 묻기 또는 실패
            return again
        return self._advance(session, state)

    def read_state(self, session: ClaudeSession) -> FlowRunState | None:
        saved = self.session_reader.load_session(session.session_id)
        if saved is None or saved.active_run_id is None:
            return None
        return self.run_state_reader.load_run(saved.session_id, saved.active_run_id)

    def cancel(self, session: ClaudeSession) -> Instruction:
        state = self.read_state(session)
        if state is None:
            return Instruction.failed("진행 중인 실행이 없습니다.")
        busy = self._check_executing(state)  # 실행 중인 명령이 끝나며 취소를 덮어쓰지 않게
        if busy is not None:
            return busy
        state.status, state.waiting_instruction, state.updated_at = FlowRunStatus.CANCELLED, None, now()
        self.run_state_writer.save_run(state)
        self._clear_active(session)
        return Instruction.finished(state.scenario.uuid, "취소했습니다.")

    def _check_executing(self, state: FlowRunState) -> Instruction | None:
        """다른 명령이 단계를 실행 중이면 wait 지시. 그 프로세스가 사라졌으면 표시를 지우고 그 단계부터 다시."""
        step = state.executing
        if step is None:
            return None
        node = _find_uuid(state.scenario, step.node_uuid)
        name = node.name if node else step.node_uuid
        if step.is_alive():
            text = f"{name} 을 실행 중입니다 ({step.started_at} 시작). 앞 명령의 완료 알림을 기다리세요."
            return Instruction.wait(text, step.node_uuid, step.item_key)
        state.executing, state.updated_at = None, now()
        self.run_state_writer.save_run(state)
        if node is not None:
            note = f"앞 실행(pid {step.pid})이 끝나지 않고 사라져 다시 실행"
            self.history_writer.append_history(state, HistoryEntry(at=now(), node_uuid=node.uuid,
                node_folder=node.folder_name, item_key=step.item_key, status=node.status,
                performed_by=node.performed_by, note=note))  # fmt: skip
        return None

    def _recover(self, state: FlowRunState) -> None:
        """실패 상태면 RUNNING 으로, 실패한 노드를 되돌려 저장한다 (그 노드부터 다시)."""
        if state.status is FlowRunStatus.FAILED:
            state.status, state.updated_at = FlowRunStatus.RUNNING, now()
            _reset_failed(state.scenario)
            if state.waiting_instruction is not None:  # 답을 기다리던 노드는 WAITING 으로
                waiting = _find_uuid(state.scenario, state.waiting_instruction.node_uuid)
                if waiting is not None:
                    waiting.status = NodeStatus.WAITING
            self.run_state_writer.save_run(state)

    def _advance(self, session: ClaudeSession, state: FlowRunState) -> Instruction:
        ins = self.unit_runner.next_instruction(state)
        if ins is not None and ins.type is not InstructionType.FINISHED:
            return ins
        state.status, state.updated_at = FlowRunStatus.FINISHED, now()
        self.run_state_writer.save_run(state)
        self._clear_active(session)
        return ins or Instruction.finished(state.scenario.uuid)  # 마지막 보이기 글을 실은 끝 지시, 없으면 기본 글

    def _clear_active(self, session: ClaudeSession) -> None:
        saved = self.session_reader.load_session(session.session_id) or session
        saved.active_run_id, saved.updated_at = None, now()
        self.session_writer.save_session(saved)
