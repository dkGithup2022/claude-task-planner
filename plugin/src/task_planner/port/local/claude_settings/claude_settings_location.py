"""Claude Code 설정 파일의 경로."""

from __future__ import annotations

import os
from pathlib import Path


def project_local_settings_file() -> Path:
    """이 작업 폴더의 개인 설정. git 에 넣지 않는 파일이다."""
    return Path.cwd() / ".claude" / "settings.local.json"


def user_settings_file() -> Path:
    """사용자 설정. CLAUDE_CONFIG_DIR 이 있으면 그 아래."""
    config_dir = os.environ.get("CLAUDE_CONFIG_DIR")
    return (Path(config_dir) if config_dir else Path.home() / ".claude") / "settings.json"
