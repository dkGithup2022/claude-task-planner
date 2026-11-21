"""끝 알림의 노드 수 줄과 노드별 표. 읽기·쓰기 없이 계획과 run.json 기록만으로 만든다."""

from __future__ import annotations

from pathlib import Path

from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_node import PlanNode
from task_planner.model.plan.plan_node_status import PlanNodeStatus
from task_planner.port.local.plan_folder.plan_folder_location import result_file

STATUS_LABELS = {
    PlanNodeStatus.DONE: "완료",
    PlanNodeStatus.SKIPPED: "건너뜀",
    PlanNodeStatus.FAILED: "실패",
    PlanNodeStatus.RUNNING: "실행 중",
    PlanNodeStatus.TODO: "할 일",
}  # 노드 수 줄도 이 순서로 적는다
CONFIRM_PREVIEW = 60  # 확인한 말은 첫 줄을 이 길이까지 보인다


def count_line(plan: Plan) -> str:
    """노드 수와 상태별 개수. 예: "노드 5개: 완료 4, 건너뜀 1". 0 인 상태는 뺀다."""
    parts = []
    for status, label in STATUS_LABELS.items():
        count = sum(1 for node in plan.nodes if node.status is status)
        if count:
            parts.append(f"{label} {count}")
    total = f"노드 {len(plan.nodes)}개"
    return f"{total}: {', '.join(parts)}" if parts else total


def node_table(plan: Plan, node_runs: dict[int, NodeRun | None]) -> str:
    """노드마다 한 줄: 노드 id, 제목, 상태, 회차, 결과 / 이유. 계획의 노드 순서."""
    header = ["| 노드 | 제목 | 상태 | 회차 | 결과 / 이유 |", "|---|---|---|---|---|"]
    rows = [table_row(plan.plan_id, node, node_runs.get(node.node_id)) for node in plan.nodes]
    return "\n".join(header + rows)


def table_row(plan_id: int, node: PlanNode, run: NodeRun | None) -> str:
    round_text = str(run.round) if run else "-"
    detail = result_or_reason(plan_id, node, run)
    return f"| {node.node_id} | {node.title} | {STATUS_LABELS[node.status]} | {round_text} | {detail} |"


def result_or_reason(plan_id: int, node: PlanNode, run: NodeRun | None) -> str:
    """완료면 확인한 말이나 결과 파일, 건너뜀·실패면 이유, 그 밖은 빈칸."""
    if node.status is PlanNodeStatus.DONE:
        return done_detail(plan_id, node, run)
    if node.status is PlanNodeStatus.SKIPPED:
        return skipped_detail(run)
    if node.status is PlanNodeStatus.FAILED:
        return failed_detail(run)
    return ""


def done_detail(plan_id: int, node: PlanNode, run: NodeRun | None) -> str:
    """확인 노드면 사용자가 한 말, 아니면 결과 파일 위치 (작업 폴더 기준)."""
    if run and run.confirm:
        return f'확인: "{first_line_preview(run.confirm)}"'
    return str(result_file(plan_id, node.node_id).relative_to(Path.cwd()))


def skipped_detail(run: NodeRun | None) -> str:
    """건너뛴 이유. 실패한 뒤 건너뛰었으면 실패 이유를 괄호로."""
    reason = (run.skipped_reason if run else None) or ""
    if run and run.failed_reason:
        reason += f" (실패 이유: {one_line(run.failed_reason)})"
    return reason


def failed_detail(run: NodeRun | None) -> str:
    return f"실패 이유: {one_line(run.failed_reason)}" if run and run.failed_reason else ""


def one_line(text: str) -> str:
    """표 칸 안에 넣을 수 있게 줄바꿈을 빈칸으로, 칸 나눔 기호 | 를 \\| 로 바꾼다.
    claude -p 가 오류로 끝나면 실패 이유에 여러 줄의 stderr 가 들어간다 (run_agent.py)."""
    return " ".join(text.split()).replace("|", "\\|")


def first_line_preview(words: str) -> str:
    """확인한 말의 첫 줄을 60자까지. 넘으면 … 를 붙인다."""
    lines = words.strip().splitlines()
    first_line = lines[0] if lines else ""
    return first_line if len(first_line) <= CONFIRM_PREVIEW else first_line[:CONFIRM_PREVIEW] + "…"
