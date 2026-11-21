"""NodeRun ↔ run.json."""

from __future__ import annotations

from typing import Any

from task_planner.model.node_run.node_run import NodeRun
from task_planner.model.node_run.read_input import ReadInput
from task_planner.model.plan.plan_node_status import PlanNodeStatus


class NodeRunFileConverter:
    def to_file(self, run: NodeRun) -> dict[str, Any]:
        return {
            "round": run.round,
            "status": run.status.value,
            "started_at": run.started_at,
            "finished_at": run.finished_at,
            "read_inputs": [
                {"node_id": read_input.node_id, "round": read_input.round} for read_input in run.read_inputs
            ],
            "confirm": run.confirm,
            "skipped_reason": run.skipped_reason,
            "failed_reason": run.failed_reason,
            "failed_summary": run.failed_summary,
        }

    def to_data(self, run_json: dict[str, Any]) -> NodeRun:
        return NodeRun(
            round=int(run_json["round"]),
            status=PlanNodeStatus(run_json["status"]),
            started_at=run_json.get("started_at"),
            finished_at=run_json.get("finished_at"),
            read_inputs=tuple(
                ReadInput(node_id=int(read_input["node_id"]), round=int(read_input["round"]))
                for read_input in run_json.get("read_inputs") or ()
            ),
            confirm=run_json.get("confirm"),
            skipped_reason=run_json.get("skipped_reason"),
            failed_reason=run_json.get("failed_reason"),
            failed_summary=run_json.get("failed_summary"),
        )
