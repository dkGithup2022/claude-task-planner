"""도구를 쓰는 claude -p. 작업 지시 만들기(읽기 도구)와 노드 실행(쓰기 도구)이 쓴다.

call_prompt 와 달리 사용자 작업 폴더에서 돌고, 출력 모양을 정하지 않는다 (답 글 그대로).
켠 도구만 쓸 수 있고(--tools), 그 도구는 묻지 않고 쓴다(--allowedTools).
이 플러그인의 훅이 자식 안에서 돌지 않게 훅을 끄고, 요금제로 돌도록 ANTHROPIC_API_KEY 를 지운다.
기존: persona-enhancer-pg2/plugin/client/plan/claude.py:120-148 (run_agent).

자식은 새 프로세스 그룹으로 띄워(시간 초과 때 그룹째 끝내려고) 우리 프로세스가 받는 신호가 전해지지 않는다.
그래서 띄운 그룹을 기록해 두고, 우리 프로세스가 SIGTERM·SIGINT 를 받거나 끝날 때 함께 끝낸다
(묶음 2 리뷰 지적, 12분 시험에서 명령이 실제로 강제로 끝남. 사용자 2026-11-20). SIGKILL 로 끝나면 막을 수 없다.
"""

from __future__ import annotations

import atexit
import contextlib
import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path
from typing import Any

from task_planner.claude_utils.agent.agent_call_error import AgentCallError
from task_planner.claude_utils.agent.dto.agent_result import AgentResult

NO_HOOKS = '{"disableAllHooks": true}'

_live_groups: set[int] = set()  # 돌고 있는 자식의 프로세스 그룹
_live_lock = threading.Lock()
_cleanup_installed = False


def install_child_cleanup() -> None:
    """우리 프로세스가 SIGTERM·SIGINT 를 받거나 끝날 때 돌고 있는 자식을 끝내게 한다.
    신호 처리기는 주 스레드에서만 걸 수 있으므로, 작업 스레드를 띄우기 전에 주 스레드에서 부른다.
    여러 번 불러도 한 번만 건다."""
    global _cleanup_installed
    if _cleanup_installed or threading.current_thread() is not threading.main_thread():
        return
    _cleanup_installed = True
    atexit.register(_kill_live_groups)
    for signal_number in (signal.SIGTERM, signal.SIGINT):
        signal.signal(signal_number, _kill_then_reraise)


def _kill_then_reraise(signal_number: int, frame: object) -> None:
    """자식을 끝낸 뒤, 원래대로 그 신호로 끝난다."""
    _kill_live_groups()
    signal.signal(signal_number, signal.SIG_DFL)
    os.kill(os.getpid(), signal_number)


def _kill_live_groups() -> None:
    with _live_lock:
        groups = list(_live_groups)
        _live_groups.clear()
    for group in groups:
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(group, signal.SIGKILL)


def run_agent(
    system_prompt: str,
    user_input: str,
    tools: tuple[str, ...],
    work_dir: Path,
    model: str,
    timeout_seconds: int,
    append: bool = False,
) -> AgentResult:
    """성공하면 AgentResult(답 글, 비용, 걸린 초). 실패(종료 코드, 시간 초과, 오류 답, 빈 답)면 AgentCallError.
    append 면 system_prompt 를 Claude Code 기본 시스템 프롬프트에 덧붙이고(노드 실행),
    아니면 바꾼다(작업 지시 만들기)."""
    tool_list = ",".join(tools)
    argv = [
        os.environ.get("TASK_PLANNER_CLAUDE_BIN", "claude"), "-p", "--model", model,
        "--output-format", "json", "--append-system-prompt" if append else "--system-prompt", system_prompt,
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
    with _live_lock:
        _live_groups.add(process.pid)
    try:
        out, err = process.communicate(user_input, timeout=timeout_seconds)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.communicate()
        return True, "", "", -1
    finally:
        with _live_lock:
            _live_groups.discard(process.pid)
    return False, out or "", err or "", process.returncode
