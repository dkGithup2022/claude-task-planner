"""mock 데이터 폴더와 mock id. 계획·페르소나·지식 mock 포트가 같이 쓴다.
폴더는 task-plan-manager 저장소의 .mockData/ (사용자, 2026-11-19)."""

from __future__ import annotations

import os
from pathlib import Path

from task_plan_manager.common import files

_REPO_ROOT = Path(__file__).resolve().parents[3]  # common/ → task_plan_manager/ → src/ → 저장소


def mock_dir() -> Path:
    """mock 데이터 폴더. TASK_PLAN_MANAGER_MOCK_DIR 이 있으면 그곳 (시험용)."""
    return Path(os.environ.get("TASK_PLAN_MANAGER_MOCK_DIR") or _REPO_ROOT / ".mockData")


def next_mock_id(id_kind: str) -> int:
    """서버처럼 종류(plan, node, edge, memory …)마다 1 부터 차례로 id 를 준다. 마지막 id 는 ids.json 에 남긴다."""
    ids_path = mock_dir() / "ids.json"
    last_ids = files.read_json(ids_path) if ids_path.exists() else {}
    new_id = int(last_ids.get(id_kind, 0)) + 1
    last_ids[id_kind] = new_id
    files.write_json(ids_path, last_ids)
    return new_id
