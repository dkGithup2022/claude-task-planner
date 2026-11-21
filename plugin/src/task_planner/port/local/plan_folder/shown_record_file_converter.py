"""ShownRecord ↔ shown.json."""

from __future__ import annotations

from typing import Any

from task_planner.model.plan.shown_record import ShownRecord


class ShownRecordFileConverter:
    def to_file(self, record: ShownRecord) -> dict[str, Any]:
        return {"shown_at": record.shown_at, "transcript": record.transcript}

    def to_data(self, shown_json: dict[str, Any]) -> ShownRecord:
        return ShownRecord(shown_at=shown_json["shown_at"], transcript=shown_json.get("transcript"))
