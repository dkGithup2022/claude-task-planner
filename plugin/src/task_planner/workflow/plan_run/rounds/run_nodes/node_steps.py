"""노드 하나의 시작, 실행, 판정, 끝. 시작과 끝(기록 쓰기)은 루프를 도는 스레드에서만 부른다.
실행(execute_node)은 작업 스레드에서 돌고 기록을 쓰지 않는다 (mock 저장소가 파일이라 동시에 쓰면 덮일 수 있다)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Any

from task_planner.claude_utils.agent.agent_call_error import AgentCallError
from task_planner.claude_utils.agent.dto.agent_result import AgentResult
from task_planner.claude_utils.agent.run_agent import run_agent
from task_planner.common.clock import utc_now
from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.node_run.read_input import ReadInput
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_planner.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_planner.port.local.plan_folder.dto.result_target import ResultTarget
from task_planner.port.plan_api.dto.node_change import NodeChange
from task_planner.port.plan_api.plan_api_choice import plan_api_writer
from task_planner.workflow.plan_run.rounds.run_nodes.node_outcome import NodeOutcome
from task_planner.workflow.plan_run.rounds.run_nodes.node_run_input import node_run_input

HERE = Path(__file__).parent
RUN_TOOLS = ("Read", "Write", "Edit", "Glob", "Grep", "Bash", "WebSearch", "WebFetch")  # 사용자, 2026-11-20
MODEL = "opus"
NODE_TIMEOUT_SECONDS = 1800  # 노드 하나 30분 (사용자, 2026-11-19)
DONE_LINE = "status: done"


def start_node(plan: Plan, node_id: int) -> None:
    """run.json 에 시작(시각, 읽은 선행 노드와 그 회차)을 쓰고 노드 상태를 running 으로."""
    folder = DefaultPlanFolderReader()
    run = folder.read_run(plan.plan_id, node_id) or NodeRun(round=1, status=PlanNodeStatus.TODO)
    read_inputs = tuple(ReadInput(pre_id, _round_of(plan.plan_id, pre_id)) for pre_id in plan.prerequisites(node_id))
    DefaultPlanFolderWriter().save_run(plan.plan_id, node_id, run.start(utc_now(), read_inputs))
    plan_api_writer().update_node(plan.plan_id, node_id, NodeChange(status=PlanNodeStatus.RUNNING))


def execute_node(plan: Plan, node: PlanNode) -> NodeOutcome:
    """작업 스레드: 입력을 만들고 run_agent 로 실행한 뒤 판정만 한다. 기록하지 않는다."""
    folder = DefaultPlanFolderReader()
    prompt_text = folder.read_prompt(plan.plan_id, node.node_id)
    if prompt_text is None:
        return NodeOutcome(node.node_id, PlanNodeStatus.FAILED, "작업 지시 없음", "")
    target = folder.result_target(plan.plan_id, node.node_id)
    user_input = node_run_input(plan, node, prompt_text, target)
    try:
        answer = run_agent(
            node_run_message(), user_input, RUN_TOOLS, Path.cwd(), MODEL, NODE_TIMEOUT_SECONDS, append=True
        )
    except AgentCallError as error:
        return NodeOutcome(node.node_id, PlanNodeStatus.FAILED, str(error), "")
    return judge(node.node_id, answer, target)


def judge(node_id: int, answer: AgentResult, target: ResultTarget) -> NodeOutcome:
    """완료: 답 첫 줄이 "status: done" 이고 result.md 가 있음. 그 밖은 실패와 이유 (기존 plan-run SKILL.md:27-30)."""
    lines = answer.text.strip().splitlines()
    first_line = lines[0].strip() if lines else ""
    summary = "\n".join(lines[1:4]).strip()
    cost, seconds = answer.cost_usd, answer.seconds
    if first_line == "status: blocked":
        return NodeOutcome(node_id, PlanNodeStatus.FAILED, "막힘", summary, cost, seconds)
    if first_line != DONE_LINE:
        return NodeOutcome(
            node_id, PlanNodeStatus.FAILED, "답 첫 줄에 status 가 없음", answer.text[:300], cost, seconds
        )
    if not target.result_path.exists():
        return NodeOutcome(node_id, PlanNodeStatus.FAILED, "결과 파일 없음", summary, cost, seconds)
    return NodeOutcome(node_id, PlanNodeStatus.DONE, "", summary, cost, seconds)


def finish_node(plan_id: int, outcome: NodeOutcome) -> dict[str, Any]:
    """run.json 에 끝(상태, 시각, 실패면 이유와 요약)을 쓰고 노드 상태를 done / failed 로.
    이번 차례 기록 한 줄을 돌려준다.
    실패 이유를 run.json 에 남겨, 다음 차례나 다음 /plan-run 에서 실패 처리를 물을 때도 보인다."""
    run = DefaultPlanFolderReader().read_run(plan_id, outcome.node_id) or NodeRun(1, PlanNodeStatus.RUNNING)
    finished = run.finish(outcome.status, utc_now())
    if outcome.status is PlanNodeStatus.FAILED:
        finished = replace(finished, failed_reason=outcome.reason, failed_summary=outcome.summary)
    DefaultPlanFolderWriter().save_run(plan_id, outcome.node_id, finished)
    plan_api_writer().update_node(plan_id, outcome.node_id, NodeChange(status=outcome.status))
    return {
        "node_id": outcome.node_id,
        "status": outcome.status.value,
        "reason": outcome.reason,
        "summary": outcome.summary,
        "cost_usd": outcome.cost_usd,
        "seconds": outcome.seconds,
    }


def node_run_message() -> str:
    return (HERE / "node_run_message.md").read_text(encoding="utf-8").strip()


def _round_of(plan_id: int, node_id: int) -> int:
    """선행 노드의 마지막 회차. 실행 기록이 없으면(건너뛰기만 함 등) 1."""
    run = DefaultPlanFolderReader().read_run(plan_id, node_id)
    return run.round if run else 1
