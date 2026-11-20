"""plan show 와 plan edit 명령이 부르는 기능. 결과는 명령이 그대로 출력하는 JSON 모양의 dict."""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from task_plan_manager.claude_utils.prompt.call_prompt import call_prompt
from task_plan_manager.claude_utils.prompt.prompt_call_error import PromptCallError
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_plan_manager.port.plan_api.plan_not_found_error import PlanNotFoundError
from task_plan_manager.workflow.make_plan.prepare_show.plan_summary import build_summary
from task_plan_manager.workflow.plan_edit.edit_graph import EditGraph
from task_plan_manager.workflow.plan_edit.op.edit_op_reader import read_ops
from task_plan_manager.workflow.plan_edit.plan_edit_refused_error import PlanEditRefusedError
from task_plan_manager.workflow.plan_edit.send_edit import send_edit
from task_plan_manager.workflow.plan_edit.show_progress import showing_edit
from task_plan_manager.workflow.relink_edges.relink_edges import PromptCaller, relink_edges


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


def edit_plan(plan_id: int, data: Any, caller: PromptCaller = call_prompt) -> dict[str, Any]:
    """plan edit: 묶음 동작을 미리 적용하고, 나누기·합치기·넣기·빼기가 있으면 간선을 다시 정해 점검한다.
    통과하면 계획 저장소에 보낸 뒤 새 계획 표를 돌려준다. 도는 동안 상태 줄에 "계획을 고치는 중" 을 보인다."""
    with showing_edit(plan_id):
        return _edit_plan(plan_id, data, caller)


def _edit_plan(plan_id: int, data: Any, caller: PromptCaller) -> dict[str, Any]:
    try:
        before, graph = _prepare(plan_id, data, caller)
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


def _prepare(plan_id: int, data: Any, caller: PromptCaller) -> tuple[Plan, EditGraph]:
    """계획을 읽고 동작을 메모리에서 적용한 뒤 간선을 다시 정한다. 검토 중이 아니거나 새 문제가 생기면 거절한다."""
    try:
        before = plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError as error:
        raise PlanEditRefusedError(str(error)) from error
    if before.status is not PlanStatus.REVIEWING:
        raise PlanEditRefusedError(f"계획 {plan_id} 는 검토 중이 아니라({before.status.value}) 고치지 않습니다")
    graph = EditGraph(before)
    graph.apply_all(read_ops(data))
    _relink(graph, caller)
    graph.changes += _edge_changes(before, graph)
    new_problems = _new_problems(before, graph.as_plan())
    if new_problems:
        raise PlanEditRefusedError("고치면 생기는 문제: " + " / ".join(new_problems))
    return before, graph


def _relink(graph: EditGraph, caller: PromptCaller) -> None:
    """나누기·합치기·넣기·빼기가 있었으면 바뀐 노드와 앞뒤 노드 사이의 간선을 claude -p 로 다시 정한다.
    호출이 실패하면 고치지 않고 거절한다 (사용자, 2026-11-19)."""
    request = graph.relink_request()
    if request is None:
        return
    try:
        result = relink_edges(request, caller)
    except PromptCallError as error:
        raise PlanEditRefusedError(f"간선을 다시 정하지 못해 고치지 않았습니다: {error}") from error
    graph.apply_relinked(request, result.edges)


def _edge_changes(before: Plan, graph: EditGraph) -> list[str]:
    """고치기 전과 후의 간선을 비교한 이음·끊음 줄. 새 노드의 임시 id 는 보낸 뒤 진짜 id 로 바뀐다."""
    old = {(edge.from_node_id, edge.to_node_id) for edge in before.edges}
    lines = []
    for label, edges in (("이음", sorted(graph.edges - old, key=_edge_order)), ("끊음", sorted(old - graph.edges))):
        if edges:
            lines.append(f"{label}: " + ", ".join(f"{{{from_id}}} → {{{to_id}}}" for from_id, to_id in edges))
    return lines


def _edge_order(edge: tuple[int, int]) -> tuple[int, int]:
    """기존 노드(양수 id)를 앞에, 새 노드(음수 임시 id)는 만든 순서(-1, -2, …)대로 뒤에."""
    return tuple(node_id if node_id >= 0 else 10**9 - node_id for node_id in edge)  # type: ignore[return-value]


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
