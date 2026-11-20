"""Claude Code 상태 줄 명령(task_plan_manager statusline)이 하는 일.
Claude Code 는 작업 폴더 설정(.claude/settings.local.json)의 statusLine 으로 이 명령을 5 초마다 부르고,
세션 정보를 JSON 으로 표준 입력에 넣는다. 이 명령이 찍은 줄이 화면 아래 상태 줄에 보인다."""

from __future__ import annotations

import json
import os
import subprocess
from datetime import UTC, datetime
from typing import Any

from task_plan_manager.port.local.claude_settings.default_claude_settings_reader import DefaultClaudeSettingsReader
from task_plan_manager.port.local.claude_settings.default_claude_settings_writer import OUR_COMMAND_ENDING
from task_plan_manager.port.local.progress_log.default_progress_log_reader import DefaultProgressLogReader
from task_plan_manager.workflow.statusline.statusline_text import statusline_text

FORWARD_TIMEOUT_SECONDS = 2  # 원래 상태 줄 명령을 기다리는 최대 시간. 상태 줄이 늦게 뜨지 않게


def draw_statusline(stdin_text: str) -> list[str]:
    """상태 줄에 찍을 줄들. 이 세션이 남긴 진행 기록이 없으면 빈 목록."""
    forward_to_user_statusline(stdin_text)
    status = _parse_status(stdin_text)
    session_id = status.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        return []
    _move_to_work_folder(status)
    event = DefaultProgressLogReader().latest_for_session(session_id)
    return statusline_text(event, datetime.now(UTC)) if event is not None else []


def forward_to_user_statusline(stdin_text: str) -> None:
    """사용자 설정(~/.claude/settings.json)의 원래 상태 줄 명령에 같은 입력을 넘긴다.
    작업 폴더 설정이 사용자 설정을 덮어써도, 원래 명령이 받던 데이터(예: Orca 의 사용량)가 끊기지 않게 하려고.
    원래 명령이 찍은 글은 버린다. 원래 명령이 우리 명령이면 자기 자신을 다시 부르게 되므로 넘기지 않는다."""
    command = DefaultClaudeSettingsReader().user_statusline_command()
    if command is None or command.strip().endswith(OUR_COMMAND_ENDING):
        return
    try:
        subprocess.run(
            command, shell=True, input=stdin_text, text=True, capture_output=True, timeout=FORWARD_TIMEOUT_SECONDS
        )
    except (OSError, subprocess.SubprocessError):
        return


def _parse_status(stdin_text: str) -> dict[str, Any]:
    try:
        status = json.loads(stdin_text or "{}")
    except ValueError:
        return {}
    return status if isinstance(status, dict) else {}


def _move_to_work_folder(status: dict[str, Any]) -> None:
    """진행 기록은 작업 폴더의 .plan/ 아래에 있다. Claude Code 가 알려 준 작업 폴더로 옮긴다."""
    workspace = status.get("workspace")
    folder = workspace.get("current_dir") if isinstance(workspace, dict) else None
    folder = folder or status.get("cwd")
    if isinstance(folder, str) and os.path.isdir(folder):
        os.chdir(folder)
