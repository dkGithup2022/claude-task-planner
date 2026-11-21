"""작업 폴더의 Claude Code 설정 쓰기 구현."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from task_planner.common import files
from task_planner.port.local.claude_settings.claude_settings_location import project_local_settings_file
from task_planner.port.local.claude_settings.claude_settings_writer import ClaudeSettingsWriter
from task_planner.port.local.claude_settings.dto.statusline_setup import StatuslineSetup

OUR_COMMAND_ENDING = "/bin/task-planner statusline"


class DefaultClaudeSettingsWriter(ClaudeSettingsWriter):
    def ensure_statusline(self, command: str, refresh_seconds: int) -> StatuslineSetup:
        # 파일이 없으면 만들고, statusLine 이 비었거나 예전에 우리가 넣은 것이면 지금 명령으로 넣는다
        path = project_local_settings_file()
        settings = _read_settings(path) if path.exists() else {}
        if settings is None:
            return StatuslineSetup.LEFT_ALONE
        current = settings.get("statusLine")
        if _command_of(current) == command:
            return StatuslineSetup.ALREADY
        if current is not None and not _command_of(current).endswith(OUR_COMMAND_ENDING):
            return StatuslineSetup.LEFT_ALONE
        settings["statusLine"] = {"type": "command", "command": command, "refreshInterval": refresh_seconds}
        try:
            files.write_text(path, json.dumps(settings, ensure_ascii=False, indent=2) + "\n")
        except OSError:
            return StatuslineSetup.LEFT_ALONE  # 상태 줄은 부가 기능이라 쓰지 못해도 흐름을 멈추지 않는다
        return StatuslineSetup.WRITTEN


def _command_of(statusline: Any) -> str:
    """설정의 상태 줄 명령. 플러그인 버전이 바뀌면 이 명령의 실행 파일 경로만 달라진다."""
    return str(statusline.get("command", "")) if isinstance(statusline, dict) else ""


def _read_settings(path: Path) -> dict[str, Any] | None:
    """설정 파일의 내용. JSON 객체가 아니면 None (사용자 파일을 건드리지 않으려고)."""
    try:
        data = files.read_json(path)
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None
