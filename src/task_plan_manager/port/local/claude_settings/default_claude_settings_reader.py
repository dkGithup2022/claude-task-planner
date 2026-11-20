"""Claude Code 설정 읽기 구현."""

from __future__ import annotations

from task_plan_manager.common import files
from task_plan_manager.port.local.claude_settings.claude_settings_location import user_settings_file
from task_plan_manager.port.local.claude_settings.claude_settings_reader import ClaudeSettingsReader


class DefaultClaudeSettingsReader(ClaudeSettingsReader):
    def user_statusline_command(self) -> str | None:
        # 사용자 설정의 statusLine.command. 파일이 없거나 모양이 다르면 None
        try:
            settings = files.read_json(user_settings_file())
        except (OSError, ValueError):
            return None
        statusline = settings.get("statusLine") if isinstance(settings, dict) else None
        command = statusline.get("command") if isinstance(statusline, dict) else None
        return command if isinstance(command, str) and command.strip() else None
