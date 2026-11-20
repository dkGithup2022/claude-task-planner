"""작업 폴더의 Claude Code 설정 쓰기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_plan_manager.port.local.claude_settings.dto.statusline_setup import StatuslineSetup


class ClaudeSettingsWriter(ABC):
    @abstractmethod
    def ensure_statusline(self, command: str, refresh_seconds: int) -> StatuslineSetup:
        """작업 폴더의 .claude/settings.local.json 에 상태 줄을 넣는다. 다른 키는 그대로 둔다.
        사용자가 넣은 다른 상태 줄이 있으면 덮어쓰지 않는다. 예전 버전의 우리 상태 줄은 지금 명령으로 바꾼다.
        쓰지 못하면 LEFT_ALONE (상태 줄은 부가 기능이라 흐름을 멈추지 않는다)."""
