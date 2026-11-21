"""모든 경로는 여기서 정한다. 실행 데이터는 작업 폴더의 .task_planner/ 아래."""

from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    """실행 데이터 폴더. TASK_PLANNER_HOME 이 있으면 그곳 (시험용)."""
    return Path(os.environ.get("TASK_PLANNER_HOME") or Path.cwd() / ".task_planner")
