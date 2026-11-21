"""카운터 파일 위치: <데이터 폴더>/counter.json."""

from __future__ import annotations

from pathlib import Path

from task_planner.common.paths import home


def counter_file() -> Path:
    return home() / "counter.json"
