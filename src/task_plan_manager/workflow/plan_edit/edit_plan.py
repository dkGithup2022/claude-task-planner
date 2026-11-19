"""plan show 와 plan edit 명령이 부르는 기능. 결과는 명령이 그대로 출력하는 JSON 모양의 dict."""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_plan_manager.port.plan_api.plan_not_found_error import PlanNotFoundError
from task_plan_manager.workflow.make_plan.prepare_show.plan_summary import build_summary
from task_plan_manager.workflow.plan_edit.edit_graph import EditGraph
from task_plan_manager.workflow.plan_edit.op.edit_op_reader import read_ops
from task_plan_manager.workflow.plan_edit.plan_edit_refused_error import PlanEditRefusedError
from task_plan_manager.workflow.plan_edit.send_edit import send_edit


def show_plan(plan_id: int) -> dict[str, Any]:
    """plan show: 지금 계획의 노드(정의서 포함)와 간선."""
    try:
        plan = plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError as error:
        return {"ok": False, "reason": str(error)}
    return {
        "ok": True, "plan_id": plan.plan_id, "title": plan.title, "status": plan.status.value,
        "persona_ids": list(plan.persona_ids),
        "nodes": [{"node_id": node.node_id, "title": node.title, "kind": node.kind.value,
                   "persona_ids": list(node.persona_ids), "output_spec": node.output_spec} for node in plan.nodes],
        "edges": [{"from": edge.from_node_id, "to": edge.to_node_id} for edge in plan.edges],
    }  # fmt: skip


def edit_plan(plan_id: int, data: Any) -> dict[str, Any]:
    """plan edit: 묶음 동작을 미리 적용해 점검하고, 통과하면 계획 저장소에 보낸 뒤 새 계획 표를 돌려준다."""
    try:
        before, graph = _prepare(plan_id, data)
    except PlanEditRefusedError as error:
        return {"ok": False, "reason": str(error)}
    sent: list[str] = []
    try:
        real_ids = send_edit(before, graph, plan_api_writer(), sent)
    except Exception as error:  # noqa: BLE001 — 보낸 것까지 알리고 되돌리지 않는다
        return {"ok": False, "changes": sent, "error": f"계획 저장소에 보내다 실패: {error}"}
    after = plan_api_reader().get_plan(plan_id)
    return {
        "ok": True,
        "changes": [_with_real_ids(change, real_ids) for change in graph.changes],
        "summary": build_summary(after, [], "고쳤습니다"),
        "problems": list(after.problems()),
    }


def _prepare(plan_id: int, data: Any) -> tuple[Plan, EditGraph]:
    """계획을 읽고 동작을 메모리에서 적용한다. 검토 중이 아니거나 새 문제가 생기면 거절한다."""
    try:
        before = plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError as error:
        raise PlanEditRefusedError(str(error)) from error
    if before.status is not PlanStatus.REVIEWING:
        raise PlanEditRefusedError(f"계획 {plan_id} 는 검토 중이 아니라({before.status.value}) 고치지 않습니다")
    graph = EditGraph(before)
    graph.apply_all(read_ops(data))
    new_problems = _new_problems(before, graph.as_plan())
    if new_problems:
        raise PlanEditRefusedError("고치면 생기는 문제: " + " / ".join(new_problems))
    return before, graph


def _new_problems(before: Plan, after: Plan) -> list[str]:
    """고치기 전에 없던 문제. 문제 글에 노드 제목이 들어가므로 제목을 지운 계획끼리 비교한다.
    그래야 이름만 바꾼 노드의 원래 문제를 새 문제로 보지 않는다."""
    old_keys = set(_untitled(before).problems())
    after_keys = _untitled(after).problems()  # after.problems() 와 같은 순서
    return [problem for key, problem in zip(after_keys, after.problems(), strict=True) if key not in old_keys]


def _untitled(plan: Plan) -> Plan:
    return replace(plan, nodes=tuple(replace(node, title="") for node in plan.nodes))


def _with_real_ids(change: str, real_ids: dict[int, int]) -> str:
    """바뀐 것 글의 {id} 를 진짜 id 로 바꾼다. 새 노드의 임시 id(음수)는 저장소가 준 id 로."""
    return re.sub(r"\{(-?\d+)\}", lambda match: str(real_ids.get(int(match.group(1)), int(match.group(1)))), change)
