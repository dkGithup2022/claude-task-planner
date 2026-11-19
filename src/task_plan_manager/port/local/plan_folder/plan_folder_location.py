"""계획 폴더의 경로. CLI 를 부른 작업 폴더의 .plan/<plan_id>/ 아래 (실행 데이터 확정 탭 1 절)."""

from __future__ import annotations

from pathlib import Path


def plan_root() -> Path:
    """이 작업 폴더의 계획 폴더들이 모인 곳."""
    return Path.cwd() / ".plan"


def plan_dir(plan_id: int) -> Path:
    return plan_root() / str(plan_id)


def command_file(plan_id: int) -> Path:
    return plan_dir(plan_id) / "command.md"


def shown_file(plan_id: int) -> Path:
    """계획을 보여 준 기록."""
    return plan_dir(plan_id) / "shown.json"


def node_dir(plan_id: int, node_id: int) -> Path:
    return plan_dir(plan_id) / "nodes" / str(node_id)


def prompt_file(plan_id: int, node_id: int) -> Path:
    return node_dir(plan_id, node_id) / "prompt.md"


def result_file(plan_id: int, node_id: int) -> Path:
    return node_dir(plan_id, node_id) / "result.md"


def files_dir(plan_id: int, node_id: int) -> Path:
    return node_dir(plan_id, node_id) / "files"


def run_file(plan_id: int, node_id: int) -> Path:
    return node_dir(plan_id, node_id) / "run.json"


def round_dir(plan_id: int, node_id: int, round_no: int) -> Path:
    """다시 실행하기 전의 파일을 옮겨 두는 곳."""
    return node_dir(plan_id, node_id) / "runs" / str(round_no)
