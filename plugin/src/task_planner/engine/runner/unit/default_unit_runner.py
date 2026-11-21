"""DefaultUnitRunner: 다음 차례 노드를 찾아 수행하고 결과·상태·history 를 기록한다."""

from __future__ import annotations

import os
import traceback
from collections.abc import Mapping
from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.reply_rejected_error import ReplyRejectedError
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.instruction.instruction import Instruction
from task_planner.engine.instruction.instruction_type import InstructionType
from task_planner.engine.model.history.history_entry import HistoryEntry
from task_planner.engine.model.result.item_key import NO_ITEM_KEY
from task_planner.engine.model.run_state.executing_step import ExecutingStep
from task_planner.engine.model.run_state.flow_run_state import FlowRunState
from task_planner.engine.model.run_state.flow_run_status import FlowRunStatus
from task_planner.engine.model.run_state.node_kind import NodeKind
from task_planner.engine.model.run_state.node_status import NodeStatus
from task_planner.engine.model.run_state.scenario_node import ScenarioNode
from task_planner.engine.performer.call_outcome import CallOutcome
from task_planner.engine.performer.claude_prompt.recorded_prompt_call_error import RecordedPromptCallError
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.performer.task_performer import TaskPerformer
from task_planner.engine.port.history.history_writer import HistoryWriter
from task_planner.engine.port.result.result_reader import ResultReader
from task_planner.engine.port.result.result_writer import ResultWriter
from task_planner.engine.port.run_state.run_state_writer import RunStateWriter
from task_planner.engine.registry.registries import CONDITIONS, TASKS
from task_planner.engine.request.show_request import ShowRequest
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.engine.runner.child_run.child_run_strategy import ChildRunStrategy
from task_planner.engine.runner.unit.scenario_status import _complete_descendants, _is_done, now
from task_planner.engine.runner.unit.unit_runner import UnitRunner


class DefaultUnitRunner(UnitRunner):
    def __init__(
        self,
        run_state_writer: RunStateWriter,
        history_writer: HistoryWriter,
        result_reader: ResultReader,
        result_writer: ResultWriter,
        performers: Mapping[PerformedBy, TaskPerformer],
        child_run_strategies: Mapping[ChildRun, ChildRunStrategy],
    ) -> None:
        self.run_state_writer, self.history_writer = run_state_writer, history_writer
        self.result_reader, self.result_writer = result_reader, result_writer
        self.performers, self.strategies = performers, child_run_strategies

    # --- 1. 다음 차례 찾기 ---
    def _find_next(self, state: FlowRunState) -> tuple[ScenarioNode, FlowContext] | None:
        root = FlowContext(state, state.scenario, NO_ITEM_KEY, self.result_reader, self.result_writer)
        return self._walk(state.scenario, root)

    def _walk(self, node: ScenarioNode, context: FlowContext) -> tuple[ScenarioNode, FlowContext] | None:
        key = context.item_key or NO_ITEM_KEY
        if _is_done(node, key):
            return None
        if node.run_if is not None and not CONDITIONS.create(node.run_if)(context):
            self._mark(context.state, node, key, NodeStatus.SKIPPED)
            return None
        if node.kind is NodeKind.TASK:
            return node, context
        assert node.child_run is not None
        if node.status is NodeStatus.PENDING:  # 묶음 노드는 자식이 진행 중이면 RUNNING
            node.status = NodeStatus.RUNNING
        for child, child_key in self.strategies[node.child_run].children_in_turn(node, context):
            found = self._walk(
                child, FlowContext(context.state, child, child_key, context.result_reader, context.result_writer)
            )
            if found is not None:
                return found
        self._mark(context.state, node, key, NodeStatus.COMPLETED, record=False)
        if key == NO_ITEM_KEY:
            _complete_descendants(node)
        return None

    # --- 2·3. 수행과 기록 ---
    def next_instruction(self, state: FlowRunState) -> Instruction | None:
        while True:
            node: ScenarioNode | None = None
            context: FlowContext | None = None
            call: CallOutcome | None = None
            try:
                found = self._find_next(state)
                if found is None:
                    return None
                node, context = found
                assert node.task is not None and node.performed_by is not None
                task = TASKS.create(node.task)
                self._mark_executing(state, node, context)
                done = self.performers[node.performed_by].perform(node, task.build_request(context), context)
                if isinstance(done, Instruction) and done.type is not InstructionType.SHOW:
                    return self._wait(state, node, context, done)
                call = done if isinstance(done, CallOutcome) else None
                result = call.value if call else (None if isinstance(done, Instruction) else done)
                self._complete(state, node, context, task.output_kind, task.build_output(context, result), call)
                if isinstance(done, Instruction):  # SHOW: 기록한 뒤 메인 세션에 보임
                    node = context = None  # 완료한 보이기를 비움: 다음 차례 찾기의 오류가 보이기 실패로 남지 않게
                    return self._finish_with_last_show(state, done)
            except Exception as e:  # noqa: BLE001 — 단계 실패는 FAILED 로 기록하고 지시로 알린다
                return self._fail(state, node, context, e, call)

    def submit_reply(self, state: FlowRunState, reply: str | None) -> Instruction | None:
        waiting = state.waiting_instruction
        assert waiting is not None
        node: ScenarioNode | None = None
        context: FlowContext | None = None
        try:
            found = self._find_next(state)
            if found is None or found[0].uuid != waiting.node_uuid or found[1].item_key != waiting.item_key:
                raise RuntimeError(f"기다리던 노드를 찾지 못했습니다: {waiting.node_uuid} [{waiting.item_key}]")
            node, context = found
            assert node.task is not None and node.performed_by is not None
            task = TASKS.create(node.task)
            try:
                result = self.performers[node.performed_by].receive_reply(node, reply, context)
                output = task.build_output(context, result)
            except ReplyRejectedError as e:  # 같은 지시를 다시
                self._history(state, node, context.item_key, NodeStatus.WAITING, note=f"다시 물음: {e} ({reply!r})")
                return waiting
            state.waiting_instruction = None
            self._complete(state, node, context, task.output_kind, output)
            return None
        except Exception as e:  # noqa: BLE001
            return self._fail(state, node, context, e)

    def _finish_with_last_show(self, state: FlowRunState, show: Instruction) -> Instruction:
        """마지막 단계가 보이기면 그 글을 끝 지시에 싣는다. 메인 세션은 마지막 지시의 글을 빠뜨리지 않는다."""
        if self._find_next(state) is not None:
            return show
        assert isinstance(show.payload, ShowRequest)
        return Instruction.finished(state.scenario.uuid, show.payload.text, show.payload.skill)

    def _mark_executing(self, state: FlowRunState, node: ScenarioNode, context: FlowContext) -> None:
        """단계를 실행하기 직전에 표시해 저장한다. 그동안 들어온 다른 명령은 이것을 보고 기다린다."""
        item_key = None if context.item_key in (None, NO_ITEM_KEY) else context.item_key
        state.executing = ExecutingStep(node.uuid, item_key, os.getpid(), now())
        self.run_state_writer.save_run(state)

    def _wait(self, state: FlowRunState, node: ScenarioNode, context: FlowContext, ins: Instruction) -> Instruction:
        key = context.item_key or NO_ITEM_KEY
        node.status = NodeStatus.WAITING
        node.waiting_item = None if key == NO_ITEM_KEY else key
        state.waiting_instruction, state.executing = ins, None
        state.updated_at = now()
        self.run_state_writer.save_run(state)
        self._history(state, node, context.item_key, NodeStatus.WAITING)
        return ins

    def _complete(self, state: FlowRunState, node: ScenarioNode, context: FlowContext, kind: OutputKind,
                  output: TaskOutput, call: CallOutcome | None = None) -> None:  # fmt: skip
        key = context.item_key or NO_ITEM_KEY
        note = None
        if (kind is OutputKind.FILES and output.data) or (kind is OutputKind.DATA and output.files):
            raise ValueError(f"{node.name}: 결과 종류가 {kind} 인데 다른 종류의 결과를 돌려줌")
        if kind is OutputKind.FILES:  # 받은 파일을 쓰고, 산출물 폴더에 있는 파일 전부를 결과로 적는다
            names = self.result_writer.save_files(state, node, key, output.files)
            output = TaskOutput({"files": names})
            note = None if names else "경고: 산출물 폴더가 비어 있음"
        ref = self.result_writer.save_result(state, node, key, output)
        self._mark(state, node, key, NodeStatus.COMPLETED, record=False)
        state.executing, state.updated_at = None, now()
        self.run_state_writer.save_run(state)
        self._history(state, node, context.item_key, NodeStatus.COMPLETED, result_ref=ref,
                      call_files=(call.call_file,) if call else (), cost_usd=call.cost_usd if call else None,
                      seconds=call.seconds if call else None, note=note)  # fmt: skip

    def _mark(self, state: FlowRunState, node: ScenarioNode, key: str, status: NodeStatus, record: bool = True) -> None:
        """반복 밖은 상태로, 반복 안은 done_items 로. 건너뛴 항목도 done_items 에."""
        if key == NO_ITEM_KEY:
            node.status = status
        else:
            if key not in node.done_items:
                node.done_items.append(key)
            node.status = NodeStatus.RUNNING
        node.waiting_item = None
        if record:
            self.run_state_writer.save_run(state)
            self._history(state, node, None if key == NO_ITEM_KEY else key, status)

    def _fail(self, state: FlowRunState, node: ScenarioNode | None, context: FlowContext | None,
              e: Exception, done_call: CallOutcome | None = None) -> Instruction:  # fmt: skip
        key = context.item_key if context else None
        state.status, state.executing = FlowRunStatus.FAILED, None
        state.updated_at = now()
        # 호출이 실패했거나, 호출은 성공했는데 결과 처리에서 실패한 경우 모두 비용을 남긴다
        failed_call = e if isinstance(e, RecordedPromptCallError) else None
        call: CallOutcome | RecordedPromptCallError | None = done_call or failed_call
        if node is not None:
            node.status = NodeStatus.FAILED
        self.run_state_writer.save_run(state)
        # 노드를 찾기 전의 실패(반복 항목·조건)는 루트 노드로 기록한다
        self._history(state, node or state.scenario, key, NodeStatus.FAILED, note=traceback.format_exc(),
                      call_files=(call.call_file,) if call else (), cost_usd=call.cost_usd if call else None,
                      seconds=call.seconds if call else None)  # fmt: skip
        where = f"{node.name} " if node else ""
        return Instruction.failed(f"{where}실행 중 오류: {e}", node.uuid if node else "", key)

    def _history(self, state: FlowRunState, node: ScenarioNode, item_key: str | None, status: NodeStatus,
                 **kw: Any) -> None:  # fmt: skip
        self.history_writer.append_history(state, HistoryEntry(at=now(), node_uuid=node.uuid,
            node_folder=node.folder_name,
            item_key=None if item_key in (None, NO_ITEM_KEY) else item_key, status=status,
            performed_by=node.performed_by, **kw))  # fmt: skip
