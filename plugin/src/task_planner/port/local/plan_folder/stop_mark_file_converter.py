"""StopMark ↔ stop.json."""

from __future__ import annotations

from typing import Any

from task_planner.port.local.plan_folder.dto.stop_mark import StopMark


class StopMarkFileConverter:
    def to_file(self, mark: StopMark) -> dict[str, Any]:
        return {"run_id": mark.run_id, "reason": mark.reason, "node_ids": list(mark.node_ids), "message": mark.message}

    def to_data(self, stop_json: dict[str, Any]) -> StopMark:
        return StopMark(
            run_id=str(stop_json["run_id"]),
            reason=str(stop_json["reason"]),
            node_ids=tuple(int(node_id) for node_id in stop_json.get("node_ids") or ()),
            message=str(stop_json.get("message") or ""),
        )
