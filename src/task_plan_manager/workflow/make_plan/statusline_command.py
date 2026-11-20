"""작업 폴더 설정의 statusLine 에 적을 명령. 지금 돌고 있는 플러그인의 실행 파일로 상태 줄을 그린다."""

from __future__ import annotations

from pathlib import Path

# 이 파일에서 저장소까지: make_plan/ → workflow/ → task_plan_manager/ → src/ → 저장소 (common/mock_data.py 와 같은 방식)
REPO_ROOT = Path(__file__).resolve().parents[4]


def statusline_command() -> str:
    """예: /…/task-plan-manager/plugin/bin/task_plan_manager statusline. 플러그인 버전 폴더가 바뀌면 경로도 바뀐다."""
    return f"{REPO_ROOT / 'plugin' / 'bin' / 'task_plan_manager'} statusline"
