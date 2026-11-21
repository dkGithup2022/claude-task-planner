"""진행 기록 한 줄을 Claude Code 상태 줄의 글로 바꾼다. 장면: corbina 설계 문서 "진행 표시" 6 절.
첫 줄은 다섯 단계와 지금 단계, 둘째 줄부터는 그 단계에서 할 일이나 하는 일이다.
글이 정해지지 않은 순간(후보 뽑기, 저장할지 고르기, 본문 확인, 최종 정리, 작업 지시, 확인 노드, 실패 처리)은
첫 줄만 그린다 (사용자, 2026-11-20). 웹 주소가 정해지기 전이라 "진행 상황 보기" 링크는 넣지 않는다."""

from __future__ import annotations

from datetime import datetime

from task_planner.model.progress.closed_progress import ClosedProgress
from task_planner.model.progress.feedback_progress import FeedbackProgress
from task_planner.model.progress.planning_progress import PlanningProgress
from task_planner.model.progress.progress_event import ProgressDetail, ProgressEvent
from task_planner.model.progress.reinforce_phase import ReinforcePhase
from task_planner.model.progress.reinforce_progress import ReinforceProgress
from task_planner.model.progress.run_node import RunNode
from task_planner.model.progress.run_phase import RunPhase
from task_planner.model.progress.run_progress import RunProgress

STAGES = ("계획 입력", "계획 세우기", "계획 피드백", "지식 강화", "실행")
COMMAND_PREFIX = "/task-planner:"


def statusline_text(event: ProgressEvent, now: datetime) -> list[str]:
    """상태 줄에 찍을 줄들. 계획이 닫혔으면(불허) 빈 목록."""
    detail = event.detail
    if isinstance(detail, ClosedProgress):
        return []
    return [_stage_line(event.plan_id, detail), *_detail_lines(event.plan_id, detail, now)]


def _stage_line(plan_id: int, detail: ProgressDetail) -> str:
    """예: 계획 11 │ 계획 입력 ✓ › [계획 세우기] › 계획 피드백 › 지식 강화 › 실행. 실행을 마치면 모두 ✓."""
    current = _current_stage(detail)
    marked = [_mark_stage(name, index, current) for index, name in enumerate(STAGES)]
    return f"계획 {plan_id} │ " + " › ".join(marked)


def _current_stage(detail: ProgressDetail) -> int:
    """STAGES 안의 지금 단계 번호. 실행을 마쳤으면 STAGES 의 길이 (모든 단계가 지난 것)."""
    if isinstance(detail, PlanningProgress):
        return 1
    if isinstance(detail, FeedbackProgress):
        return 2
    if isinstance(detail, ReinforceProgress):
        return 3
    if isinstance(detail, RunProgress) and detail.phase is RunPhase.FINISHED:
        return len(STAGES)
    return 4


def _detail_lines(plan_id: int, detail: ProgressDetail, now: datetime) -> list[str]:
    """첫 줄 아래의 줄들. 글이 정해지지 않은 순간이면 빈 목록."""
    if isinstance(detail, PlanningProgress):
        return [f"계획 세우기 - 적합한 크기의 계획 세우는 중... ({elapsed_text(detail.started_at, now)})"]
    if isinstance(detail, FeedbackProgress):
        return _feedback_lines(plan_id, detail, now)
    if isinstance(detail, ReinforceProgress) and detail.phase is ReinforcePhase.DRAFT:
        return _draft_lines(plan_id, detail, now)
    if isinstance(detail, RunProgress):
        return _run_lines(plan_id, detail, now)
    return []


def _feedback_lines(plan_id: int, detail: FeedbackProgress, now: datetime) -> list[str]:
    if detail.editing_since is None:
        guide = "고칠 곳이 있으면 대화로 말하세요. 다 됐으면 아래 명령을 실행하세요"
    else:
        guide = f"계획을 고치는 중입니다 ({elapsed_text(detail.editing_since, now)})"
    commands = f"확정: {COMMAND_PREFIX}plan-go {plan_id}   ·   취소: {COMMAND_PREFIX}plan-cancel {plan_id}"
    return [guide, commands]


def _draft_lines(plan_id: int, detail: ReinforceProgress, now: datetime) -> list[str]:
    working = "본문 초안을 쓰는 중입니다"
    if detail.started_at is not None:
        working += f" ({elapsed_text(detail.started_at, now)})"
    return [
        f"지식 후보 - {detail.index}번째 / {detail.total}개 중 : {detail.theme}",
        working,
        f"그만두기: {COMMAND_PREFIX}plan-cancel {plan_id}",
    ]


def _run_lines(plan_id: int, detail: RunProgress, now: datetime) -> list[str]:
    if detail.phase is RunPhase.READY:
        return ["승인했습니다. 실행하려면 아래 명령을 실행하세요", f"실행: {COMMAND_PREFIX}plan-run {plan_id}"]
    if detail.phase is RunPhase.FINISHED:
        return ["계획을 마쳤습니다"]
    if detail.phase is RunPhase.NODES and detail.nodes:
        return _running_nodes_lines(detail, now)
    return []


def _running_nodes_lines(detail: RunProgress, now: datetime) -> list[str]:
    """예: 노드 실행 - 6번째 / 10개 중 : 50 API 문서 작성 외 1개. 걸린 시간은 가장 먼저 시작한 노드 기준."""
    first = _earliest_started(detail.nodes)
    others = f" 외 {len(detail.nodes) - 1}개" if len(detail.nodes) > 1 else ""
    waiting = "노드를 실행하는 중입니다. 기다리세요"
    if first.started_at is not None:
        waiting += f" ({elapsed_text(first.started_at, now)})"
    return [f"노드 실행 - {detail.done + 1}번째 / {detail.total}개 중 : {first.node_id} {first.title}{others}", waiting]


def _earliest_started(nodes: tuple[RunNode, ...]) -> RunNode:
    """시작 시각이 가장 이른 노드. 시각이 없는 노드는 뒤로."""
    return min(nodes, key=lambda node: (node.started_at is None, node.started_at or ""))


def elapsed_text(started_at: str, now: datetime) -> str:
    """걸린 시간. 1 분 전은 "35초째", 1 분부터는 "3분째" 처럼 분만."""
    seconds = max(0, int((now - datetime.fromisoformat(started_at)).total_seconds()))
    return f"{seconds}초째" if seconds < 60 else f"{seconds // 60}분째"


def _mark_stage(name: str, index: int, current: int) -> str:
    if index < current:
        return f"{name} ✓"
    return f"[{name}]" if index == current else name
