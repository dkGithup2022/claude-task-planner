"""ProgressEvent ↔ progress.jsonl 의 한 줄. detail 에는 종류 이름(kind)을 붙인다."""

from __future__ import annotations

from typing import Any

from task_planner.model.progress.closed_progress import ClosedProgress
from task_planner.model.progress.feedback_progress import FeedbackProgress
from task_planner.model.progress.planning_progress import PlanningProgress
from task_planner.model.progress.progress_event import ProgressDetail, ProgressEvent
from task_planner.model.progress.reinforce_phase import ReinforcePhase
from task_planner.model.progress.reinforce_progress import ReinforceProgress
from task_planner.model.progress.run_node import RunNode
from task_planner.model.progress.run_phase import RunPhase
from task_planner.model.progress.run_progress import RunProgress


class ProgressEventFileConverter:
    def to_file(self, event: ProgressEvent) -> dict[str, Any]:
        return {
            "at": event.at,
            "session_id": event.session_id,
            "plan_id": event.plan_id,
            "detail": _detail_to_file(event.detail),
        }

    def to_data(self, line: dict[str, Any]) -> ProgressEvent:
        return ProgressEvent(
            at=line["at"],
            session_id=line["session_id"],
            plan_id=line["plan_id"],
            detail=_detail_to_data(line["detail"]),
        )


def _detail_to_file(detail: ProgressDetail) -> dict[str, Any]:
    match detail:
        case PlanningProgress():
            return {"kind": "planning", "started_at": detail.started_at}
        case FeedbackProgress():
            return {"kind": "feedback", "editing_since": detail.editing_since}
        case ReinforceProgress():
            return {
                "kind": "reinforce",
                "phase": detail.phase.value,
                "index": detail.index,
                "total": detail.total,
                "theme": detail.theme,
                "started_at": detail.started_at,
            }
        case RunProgress():
            return {
                "kind": "run",
                "phase": detail.phase.value,
                "done": detail.done,
                "total": detail.total,
                "nodes": [_run_node_to_file(node) for node in detail.nodes],
            }
        case ClosedProgress():
            return {"kind": "closed"}


def _detail_to_data(detail: dict[str, Any]) -> ProgressDetail:
    kind = detail["kind"]
    if kind == "planning":
        return PlanningProgress(started_at=detail["started_at"])
    if kind == "feedback":
        return FeedbackProgress(editing_since=detail.get("editing_since"))
    if kind == "reinforce":
        return ReinforceProgress(
            phase=ReinforcePhase(detail["phase"]),
            index=detail.get("index"),
            total=detail.get("total"),
            theme=detail.get("theme"),
            started_at=detail.get("started_at"),
        )
    if kind == "run":
        return RunProgress(
            phase=RunPhase(detail["phase"]),
            done=detail["done"],
            total=detail["total"],
            nodes=tuple(_run_node_to_data(node) for node in detail.get("nodes", [])),
        )
    if kind == "closed":
        return ClosedProgress()
    raise ValueError(f"모르는 진행 기록 종류입니다: {kind}")


def _run_node_to_file(node: RunNode) -> dict[str, Any]:
    return {"node_id": node.node_id, "title": node.title, "started_at": node.started_at}


def _run_node_to_data(node: dict[str, Any]) -> RunNode:
    return RunNode(node_id=node["node_id"], title=node["title"], started_at=node.get("started_at"))
