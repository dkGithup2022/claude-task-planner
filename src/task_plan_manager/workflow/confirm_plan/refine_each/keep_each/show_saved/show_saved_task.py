"""show_saved: 지식 후보 하나의 저장 결과를 보인다.
저장 단계는 코드라 메인 세션이 결과를 모르기 때문이다 (e2e4, 2026-11-19: "그대로 저장됐는지 확인하지 못했다").
저장한 본문을 함께 보여, 고친 말이 들어갔는지 볼 수 있게 한다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.show_request import ShowRequest


@TASKS.register_as("confirm_plan.show_saved")
class ShowSavedTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        # 저장 결과(새로 / 덧붙이기 / 저장 안 함)와 저장한 본문을 보인다
        return ShowRequest(build_saved_text(context.read("save_knowledge"), context.read("finalize_knowledge")))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})


def build_saved_text(saved: dict[str, Any], final: dict[str, Any]) -> str:
    if saved["action"] == "new":
        return f'지식 #{saved["memory_id"]} "{final["theme"]}" 을 새로 저장했습니다.\n\n{final["body"]}'
    if saved["action"] == "append":
        return f'지식 #{saved["memory_id"]} "{final["theme"]}" 에 덧붙였습니다.\n덧붙인 내용:\n\n{final["body"]}'
    return "이 후보는 지식으로 저장하지 않았습니다."
