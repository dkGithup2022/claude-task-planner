"""mock 계획 저장소의 파일 위치. mock 폴더(common.mock_data) 아래 plans/<plan_id>.json."""

from __future__ import annotations

from pathlib import Path

from task_plan_manager.common.mock_data import mock_dir


def plan_file(plan_id: int) -> Path:
    """계획 하나의 파일. 노드와 간선을 함께 담는다."""
    return mock_dir() / "plans" / f"{plan_id}.json"
