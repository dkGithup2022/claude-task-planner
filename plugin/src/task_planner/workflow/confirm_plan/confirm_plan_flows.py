"""plan_go, plan_cancel 워크플로 선언. 계획서: specs/plans/workflow-confirm_plan.md

두 흐름은 단계가 같고, 기록·알리기 단계의 결정 값(승인 / 불허)만 다르다 (사용자, 2026-11-19).
단계 목록을 만드는 함수 하나로 두 선언을 만든다. 불허는 간선 확인을 건너뛴다 (사용자, 2026-11-19).
find_plan → (승인만) check_edges → extract_knowledge → refine_each → record_decision → notify.
refine_each 안: find_existing → choose_action → (병합이면) choose_target 쪽마다 → keep_each.
"""

from __future__ import annotations

from task_planner.engine.builtin import answer_is  # noqa: F401
from task_planner.engine.definition.flow_definition import FlowDefinition
from task_planner.engine.definition.ref import Ref
from task_planner.engine.definition.unit.builders import group, task
from task_planner.engine.definition.unit.unit import Unit
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.workflow.confirm_plan.check_edges import check_edges_task  # noqa: F401
from task_planner.workflow.confirm_plan.extract_knowledge import extract_knowledge_task  # noqa: F401
from task_planner.workflow.confirm_plan.find_plan import find_plan_task  # noqa: F401
from task_planner.workflow.confirm_plan.notify import notify_task  # noqa: F401
from task_planner.workflow.confirm_plan.record_decision import record_decision_task  # noqa: F401
from task_planner.workflow.confirm_plan.refine_each import candidates_items, keeps_candidate  # noqa: F401
from task_planner.workflow.confirm_plan.refine_each.choose_action import choose_action_task  # noqa: F401
from task_planner.workflow.confirm_plan.refine_each.choose_action.action_choices import MERGE
from task_planner.workflow.confirm_plan.refine_each.choose_target import choose_target_task  # noqa: F401
from task_planner.workflow.confirm_plan.refine_each.choose_target.merge_target import TARGET_PAGES
from task_planner.workflow.confirm_plan.refine_each.choose_target.target_pages import NEXT_PAGE
from task_planner.workflow.confirm_plan.refine_each.find_existing import find_existing_task  # noqa: F401
from task_planner.workflow.confirm_plan.refine_each.keep_each.finalize_knowledge import (  # noqa: F401
    finalize_knowledge_task,
)
from task_planner.workflow.confirm_plan.refine_each.keep_each.review_knowledge import (  # noqa: F401
    review_knowledge_task,
)
from task_planner.workflow.confirm_plan.refine_each.keep_each.save_knowledge import save_knowledge_task  # noqa: F401
from task_planner.workflow.confirm_plan.refine_each.keep_each.show_saved import show_saved_task  # noqa: F401
from task_planner.workflow.confirm_plan.refine_each.keep_each.write_knowledge import (  # noqa: F401
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
    """C: 지식 후보마다 기존 지식 찾기 → 병합할지 묻기 → (병합이면) 대상 고르기
    → (넣지 않기가 아니면) 본문 쓰기 → 대화로 확인 → 최종 본문 → 저장 → 저장 결과 보이기."""
    keep_each = group("keep_each", ChildRun.IN_ORDER,
        task("write_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.write_knowledge"),
             reads=("find_plan", "find_existing", "extract_knowledge", *TARGET_PAGES)),
        task("review_knowledge", PerformedBy.MAIN_SESSION_TALK, Ref("confirm_plan.review_knowledge"),
             reads=("write_knowledge", "find_plan", "extract_knowledge", *TARGET_PAGES)),
        task("finalize_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.finalize_knowledge"),
             reads=("write_knowledge", "review_knowledge", "find_plan", "extract_knowledge")),
        task("save_knowledge", PerformedBy.CODE, Ref("confirm_plan.save_knowledge"),
             reads=("finalize_knowledge", "find_plan", *TARGET_PAGES)),
        task("show_saved", PerformedBy.MAIN_SESSION_SHOW, Ref("confirm_plan.show_saved"),
             reads=("save_knowledge", "finalize_knowledge")),
        run_if=Ref("confirm_plan.keeps_candidate"), reads=("choose_action",))  # fmt: skip
    return group("refine_each", ChildRun.FOR_EACH_ITEM,
        task("find_existing", PerformedBy.CODE, Ref("confirm_plan.find_existing"), reads=("find_plan",)),
        task("choose_action", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_action"),
             reads=("find_existing", "extract_knowledge", "find_plan")),
        _choose_target(),
        keep_each,
        for_each_item_in=Ref("confirm_plan.candidates"), reads=("extract_knowledge",))  # fmt: skip


def _choose_target() -> Unit:
    """병합이면 대상을 쪽마다 고른다. 앞 쪽에서 "다음 3개 보기"를 골랐을 때만 다음 쪽을 연다.
    쪽 수는 find_existing 이 찾는 10 개를 3 / 3 / 4 로 나눈 셋이다."""
    return group("choose_target", ChildRun.IN_ORDER,
        task("choose_target_1", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_target_1", {"page": 1}),
             reads=("find_existing",)),
        task("choose_target_2", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_target_2", {"page": 2}),
             run_if=_asked_next("choose_target_1"), reads=("find_existing", "choose_target_1")),
        task("choose_target_3", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_target_3", {"page": 3}),
             run_if=_asked_next("choose_target_2"), reads=("find_existing", "choose_target_2")),
        run_if=Ref("answer_is", {"node_name": "choose_action", "value": MERGE}), reads=("choose_action",))  # fmt: skip


def _asked_next(page_node: str) -> Ref:
    """앞 쪽에서 "다음 3개 보기"를 골랐는가. 앞 쪽을 건너뛰었으면 거짓."""
    return Ref("answer_is", {"node_name": page_node, "value": NEXT_PAGE})


PLAN_GO_FLOW = confirm_plan_flow("plan_go", "approved", "검토 중인 계획에서 지식을 다듬어 저장하고 승인으로 확정한다")
PLAN_CANCEL_FLOW = confirm_plan_flow(
    "plan_cancel", "rejected", "검토 중인 계획에서 지식을 다듬어 저장하고 불허로 확정한다"
)
