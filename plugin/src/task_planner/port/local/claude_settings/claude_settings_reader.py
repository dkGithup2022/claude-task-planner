"""Claude Code 설정 읽기."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ClaudeSettingsReader(ABC):
    @abstractmethod
    def user_statusline_command(self) -> str | None:
        """사용자 설정(~/.claude/settings.json)의 상태 줄 명령. 없거나 읽지 못하면 None.
        우리 상태 줄은 받은 입력을 이 명령에 넘긴다.
        작업 폴더 설정이 사용자 설정을 덮어써도 원래 상태 줄이 받던 데이터가 끊기지 않게 하려고."""
