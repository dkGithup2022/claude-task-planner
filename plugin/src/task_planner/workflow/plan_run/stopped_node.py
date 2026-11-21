"""이번 실행에서 멈춘 자리. 멈춘 뒤의 단계를 건너뛰는 조건(not_stopped)과 알림이 같이 쓴다.
멈추는 자리: 끊긴 노드 질문에서 멈추기 (묶음 1),
작업 지시를 만들지 못한 노드 (묶음 2: 멈추기를 골랐거나 다시 만들어도 실패),
노드 실행 중 실패 처리에서 멈추기·고쳐서 다시, 확인 노드에서 허가하지 않음 (묶음 4: 계획 폴더의 멈춤 표시)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_missing_error import OutputMissingError
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader

BROKEN = "broken"  # 끊긴 노드를 다시 실행하지 않기로 함
NO_PROMPT = "no_prompt"  # 작업 지시를 만들지 못함
IN_ROUNDS = "in_rounds"  # 노드 실행 중 사용자가 멈추기로 함 (멈춤 표시의 message 를 보인다)

# 멈출 수 있는 묶음, 흐름 순서대로. 조건은 자기보다 앞 묶음만 읽을 수 있다 (선언의 reads 검사)
RESUME = "resume"
PROMPTS = "prompts"
ROUNDS = "rounds"
STAGES = (RESUME, PROMPTS, ROUNDS)


@dataclass(frozen=True, slots=True)
class StopPoint:
    reason: str  # BROKEN | NO_PROMPT | IN_ROUNDS
    node_ids: tuple[int, ...]
    message: str = ""  # IN_ROUNDS 일 때 보일 글


def stop_point(context: FlowContext, upto: str = STAGES[-1]) -> StopPoint | None:
    """upto 묶음까지에서 멈춘 자리. 멈추지 않았으면 None. 건너뛴 단계는 멈추지 않은 것으로 본다.
    읽는 단계: resume 이면 check_broken·apply_rerun, prompts 면 retry_prompts 도. 부르는 쪽의 reads 에 적는다.
    rounds 면 계획 폴더의 멈춤 표시도 본다 (find_plan 을 reads 에 적는다)."""
    stages = STAGES[: STAGES.index(upto) + 1]
    rerun = _read_or_none(context, "apply_rerun")
    if RESUME in stages and rerun is not None and rerun["stopped"]:
        return StopPoint(BROKEN, _node_ids(context.read("check_broken")["nodes"]))
    retried = _read_or_none(context, "retry_prompts") if PROMPTS in stages else None
    if retried is not None and retried["failed"]:
        return StopPoint(NO_PROMPT, _node_ids(retried["failed"]))
    if ROUNDS in stages:
        mark = DefaultPlanFolderReader().read_stop(int(context.read("find_plan")["plan_id"]))
        if mark is not None and mark.run_id == context.state.run_id:
            return StopPoint(IN_ROUNDS, mark.node_ids, mark.message)
    return None


def _read_or_none(context: FlowContext, node_name: str) -> dict[str, Any] | None:
    try:
        return dict(context.read(node_name))
    except OutputMissingError:
        return None


def _node_ids(nodes: list[dict[str, Any]]) -> tuple[int, ...]:
    return tuple(int(node["node_id"]) for node in nodes)
