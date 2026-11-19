"""도구를 쓰는 claude -p. 작업 지시 만들기(읽기 도구)와 노드 실행(쓰기 도구)이 쓴다.

call_prompt 와 달리 사용자 작업 폴더에서 돌고, 출력 모양을 정하지 않는다 (답 글 그대로).
켠 도구만 쓸 수 있고(--tools), 그 도구는 묻지 않고 쓴다(--allowedTools).
이 플러그인의 훅이 자식 안에서 돌지 않게 훅을 끄고, 요금제로 돌도록 ANTHROPIC_API_KEY 를 지운다.
기존: persona-enhancer-pg2/plugin/client/plan/claude.py:120-148 (run_agent).
"""

from __future__ import annotations

import contextlib
import json
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from task_plan_manager.claude_utils.agent.agent_call_error import AgentCallError
from task_plan_manager.claude_utils.agent.dto.agent_result import AgentResult

NO_HOOKS = '{"disableAllHooks": true}'


def run_agent(
    system_prompt: str, user_input: str, tools: tuple[str, ...], work_dir: Path, model: str, timeout_seconds: int
) -> AgentResult:
    """성공하면 AgentResult(답 글, 비용, 걸린 초). 실패(종료 코드, 시간 초과, 오류 답, 빈 답)면 AgentCallError."""
    tool_list = ",".join(tools)
    argv = [
        os.environ.get("TASK_PLAN_MANAGER_CLAUDE_BIN", "claude"), "-p", "--model", model,
        "--output-format", "json", "--system-prompt", system_prompt,
        "--tools", tool_list, "--allowedTools", tool_list,
        "--setting-sources", "project", "--settings", NO_HOOKS, "--no-session-persistence",
    ]  # fmt: skip
    started = time.monotonic()
    timed_out, stdout, stderr, exit_code = _run(argv, user_input, work_dir, timeout_seconds)
    seconds = round(time.monotonic() - started, 1)
    if timed_out:
        raise AgentCallError(f"claude 시간 초과 ({timeout_seconds}초)")
    parsed = _parse_json(stdout)
    text = str(parsed.get("result") or "").strip()
    if exit_code != 0 or parsed.get("is_error") or not text:
        raise AgentCallError(f"claude 실패 (exit {exit_code}): {(stderr or stdout)[:300]}")
    return AgentResult(text=text, cost_usd=float(parsed.get("total_cost_usd") or 0), seconds=seconds)


def _parse_json(stdout: str) -> dict[str, Any]:
    """claude -p --output-format json 의 출력. JSON 이 아니면 빈 dict."""
    parsed: Any = None
    with contextlib.suppress(ValueError):
        parsed = json.loads(stdout)
    return parsed if isinstance(parsed, dict) else {}


def _run(argv: list[str], user_input: str, work_dir: Path, timeout_seconds: int) -> tuple[bool, str, str, int]:
    """작업 폴더에서 새 프로세스 그룹으로 띄우고, 시간이 넘으면 그룹째 끝낸다.
    (시간 초과, stdout, stderr, 종료 코드)."""
    env = {key: value for key, value in os.environ.items() if key != "ANTHROPIC_API_KEY"}
    process = subprocess.Popen(argv, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, cwd=work_dir, env=env, start_new_session=True)  # fmt: skip
    try:
        out, err = process.communicate(user_input, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        return True, "", "", -1
    return False, out or "", err or "", process.returncode
