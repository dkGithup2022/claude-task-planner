"""check_edges: 확정하기 전에 계획의 노드와 간선을 검사한다. 문제가 있으면 목록을 담아 실패로 멈춘다.
지식 추출 전에 둔다. 고친 뒤 다시 불러도 지식을 다시 다루지 않게 하기 위해서다 (사용자, 2026-11-19).
불허(plan_cancel)에서는 이 단계를 두지 않는다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.confirm_plan.check_edges.plan_has_problems_error import PlanHasProblemsError


@TASKS.register_as("confirm_plan.check_edges")
class CheckEdgesTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 계획의 노드와 간선을 검사하고, 문제가 있으면 목록을 담아 실패로 멈춘다
        plan_id = context.read("find_plan")["plan_id"]
        problems = plan_api_reader().get_plan(plan_id).problems()
        if problems:
            raise PlanHasProblemsError(_problem_message(plan_id, problems))
        return TaskOutput({"problems": []})


def _problem_message(plan_id: int, problems: tuple[str, ...]) -> str:
    head = f"계획 {plan_id} 의 노드와 간선에 문제가 있어 확정하지 않았습니다."
    lines = "\n".join(f"- {problem}" for problem in problems)
    return f"{head}\n{lines}\n고친 뒤 같은 명령을 다시 불러 주세요."
