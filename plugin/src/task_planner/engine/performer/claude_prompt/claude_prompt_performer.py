"""ClaudePromptPerformer: claude -p 로 수행하고 호출 기록을 노드 폴더에 남긴다."""

from __future__ import annotations

from task_planner.claude_utils.prompt.call_prompt import call_prompt
from task_planner.claude_utils.prompt.prompt_call_error import PromptCallError
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.model.run_state.scenario_node import ScenarioNode
from task_planner.engine.performer.call_outcome import CallOutcome
from task_planner.engine.performer.claude_prompt.recorded_prompt_call_error import RecordedPromptCallError
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.performer.task_performer import TaskPerformer
from task_planner.engine.request.prompt_request import PromptRequest
from task_planner.engine.request.task_request import TaskRequest


class ClaudePromptPerformer(TaskPerformer):
    performed_by = PerformedBy.CLAUDE_P

    def perform(self, node: ScenarioNode, request: TaskRequest, context: FlowContext) -> CallOutcome:
        assert isinstance(request, PromptRequest)
        try:
            result, record = call_prompt(request.spec, request.input_text)
        except PromptCallError as e:
            ref = context.result_writer.save_prompt_call(context.state, node, e.record)
            raise RecordedPromptCallError(str(e), ref, e.record.response.get("cost_usd"),
                                        e.record.response.get("seconds")) from e  # fmt: skip
        ref = context.result_writer.save_prompt_call(context.state, node, record)
        return CallOutcome(result, ref, record.response.get("cost_usd"), record.response.get("seconds"))
