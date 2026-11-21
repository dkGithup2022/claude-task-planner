import json

import pytest

from task_planner.workflow.plan_run.find_plan.command_plan_id import command_plan_id
from task_planner.workflow.plan_run.find_plan.plan_not_runnable_error import PlanNotRunnableError


def _transcript(tmp_path, *contents: str):
    path = tmp_path / "t.jsonl"
    rows = [
        {"type": "user", "timestamp": f"2026-11-19T00:00:0{order}.000Z", "message": {"content": content}}
        for order, content in enumerate(contents)
    ]
    path.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in rows), encoding="utf-8")
    return path


def _command(name: str, args: str) -> str:
    return f"<command-name>{name}</command-name>\n<command-args>{args}</command-args>"


def test_should_read_last_plan_run_command(tmp_path):
    path = _transcript(
        tmp_path,
        _command("/task-planner:plan-run", "3"),
        _command("/task-planner:plan-go", "9"),
        _command("/task-planner:plan-run", "7"),
    )
    assert command_plan_id(path) == 7


def test_should_fail_when_no_plan_run_command(tmp_path):
    path = _transcript(tmp_path, _command("/task-planner:plan-go", "9"), "계획 7 실행해 줘")
    with pytest.raises(PlanNotRunnableError, match="명령에서 계획 id 를 찾지 못했습니다"):
        command_plan_id(path)
