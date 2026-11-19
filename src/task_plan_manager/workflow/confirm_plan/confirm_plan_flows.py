"""plan_go, plan_cancel 워크플로 선언. 계획서: specs/plans/workflow-confirm_plan.md

두 흐름은 단계가 같고, 기록·알리기 단계의 결정 값(승인 / 불허)만 다르다 (사용자, 2026-11-19).
단계 목록을 만드는 함수 하나로 두 선언을 만든다. 불허는 간선 확인을 건너뛴다 (사용자, 2026-11-19).
find_plan → (승인만) check_edges → extract_knowledge → refine_each → record_decision → notify.
"""

from __future__ import annotations

from task_plan_manager.engine.definition.flow_definition import FlowDefinition
from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.unit.builders import group, task
from task_plan_manager.engine.definition.unit.unit import Unit
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.runner.child_run.child_run import ChildRun
from task_plan_manager.workflow.confirm_plan.check_edges import check_edges_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.extract_knowledge import extract_knowledge_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.find_plan import find_plan_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.notify import notify_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.record_decision import record_decision_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each import candidates_items, keeps_candidate  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.choose_action import choose_action_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.find_existing import find_existing_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.finalize_knowledge import (  # noqa: F401
    finalize_knowledge_task,
)
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.review_knowledge import (  # noqa: F401
    review_knowledge_task,
)
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.save_knowledge import save_knowledge_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.write_knowledge import (  # noqa: F401
    write_knowledge_task,
)


def confirm_plan_flow(name: str, decision: str, description: str) -> FlowDefinition:
    """plan_go(decision approved), plan_cancel(decision rejected) 의 선언. 간선 확인은 승인에만 둔다."""
    return FlowDefinition(name=name, description=description, root=group(name, ChildRun.IN_ORDER, *_units(decision)))


def _units(decision: str) -> list[Unit]:
    units: list[Unit] = [task("find_plan", PerformedBy.CODE, Ref("confirm_plan.find_plan"))]
    if decision == "approved":
        units.append(task("check_edges", PerformedBy.CODE, Ref("confirm_plan.check_edges"), reads=("find_plan",)))
    units.append(
        task("extract_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.extract_knowledge"), reads=("find_plan",))
    )
    units.append(_refine_each())
    units.append(
        task("record_decision", PerformedBy.CODE, Ref("confirm_plan.record_decision", {"decision": decision}),
             reads=("find_plan",))
    )  # fmt: skip
    units.append(
        task("notify", PerformedBy.MAIN_SESSION_SHOW, Ref("confirm_plan.notify", {"decision": decision}),
             reads=("find_plan", "extract_knowledge", "save_knowledge"))
    )  # fmt: skip
    return units


def _refine_each() -> Unit:
    """C: 지식 후보마다 기존 지식 찾기 → 고르기 → (넣지 않기가 아니면) 본문 쓰기 → 대화로 확인 → 최종 본문 → 저장."""
    keep_each = group("keep_each", ChildRun.IN_ORDER,
        task("write_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.write_knowledge"),
             reads=("find_plan", "choose_action", "find_existing")),
        task("review_knowledge", PerformedBy.MAIN_SESSION_TALK, Ref("confirm_plan.review_knowledge"),
             reads=("write_knowledge", "choose_action")),
        task("finalize_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.finalize_knowledge"),
             reads=("write_knowledge", "review_knowledge")),
        task("save_knowledge", PerformedBy.CODE, Ref("confirm_plan.save_knowledge"),
             reads=("finalize_knowledge", "find_plan", "choose_action")),
        run_if=Ref("confirm_plan.keeps_candidate"), reads=("choose_action",))  # fmt: skip
    return group("refine_each", ChildRun.FOR_EACH_ITEM,
        task("find_existing", PerformedBy.CODE, Ref("confirm_plan.find_existing"), reads=("find_plan",)),
        task("choose_action", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_action"),
             reads=("find_existing", "extract_knowledge")),
        keep_each,
        for_each_item_in=Ref("confirm_plan.candidates"), reads=("extract_knowledge",))  # fmt: skip


PLAN_GO_FLOW = confirm_plan_flow("plan_go", "approved", "검토 중인 계획에서 지식을 다듬어 저장하고 승인으로 확정한다")
PLAN_CANCEL_FLOW = confirm_plan_flow(
    "plan_cancel", "rejected", "검토 중인 계획에서 지식을 다듬어 저장하고 불허로 확정한다"
)
