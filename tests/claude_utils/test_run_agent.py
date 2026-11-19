import json
import stat

import pytest

from task_plan_manager.claude_utils.agent.agent_call_error import AgentCallError
from task_plan_manager.claude_utils.agent.run_agent import run_agent


def _fake_claude(tmp_path, monkeypatch, body: str):
    """claude 대신 도는 가짜 실행 파일. 받은 인자와 실행 위치를 args.txt 에 남긴다."""
    exe = tmp_path / "fake-claude"
    exe.write_text(f'#!/bin/bash\nprintf "%s\\n" "$@" > {tmp_path}/args.txt\npwd >> {tmp_path}/args.txt\n' + body)
    exe.chmod(exe.stat().st_mode | stat.S_IEXEC)
    monkeypatch.setenv("TASK_PLAN_MANAGER_CLAUDE_BIN", str(exe))


def test_should_run_in_work_dir_with_given_tools_and_no_hooks(tmp_path, monkeypatch):
    out = {"result": "## 전체 작업과 이 노드의 목표\n본문", "total_cost_usd": 0.4}
    _fake_claude(tmp_path, monkeypatch, f"cat > /dev/null\necho '{json.dumps(out, ensure_ascii=False)}'")
    work = tmp_path / "work"
    work.mkdir()

    result = run_agent("시스템", "입력", ("Read", "Grep"), work, model="opus", timeout_seconds=5)

    assert result.text == "## 전체 작업과 이 노드의 목표\n본문" and result.cost_usd == 0.4
    args = (tmp_path / "args.txt").read_text().splitlines()
    assert args[args.index("--tools") + 1] == "Read,Grep"
    assert args[args.index("--allowedTools") + 1] == "Read,Grep"
    assert args[args.index("--settings") + 1] == '{"disableAllHooks": true}'
    assert args[-1] == str(work.resolve())


@pytest.mark.parametrize(
    "body",
    [
        "cat > /dev/null\nexit 1",
        'cat > /dev/null\necho \'{"is_error": true, "result": "한도"}\'',
        'cat > /dev/null\necho \'{"result": "  "}\'',
        "cat > /dev/null\necho 'not json'",
    ],
)
def test_should_raise_when_claude_fails(tmp_path, monkeypatch, body):
    _fake_claude(tmp_path, monkeypatch, body)
    with pytest.raises(AgentCallError, match="claude 실패"):
        run_agent("시스템", "입력", ("Read",), tmp_path, model="opus", timeout_seconds=5)


def test_should_raise_on_timeout(tmp_path, monkeypatch):
    _fake_claude(tmp_path, monkeypatch, "sleep 5")
    with pytest.raises(AgentCallError, match="시간 초과"):
        run_agent("시스템", "입력", ("Read",), tmp_path, model="opus", timeout_seconds=1)
