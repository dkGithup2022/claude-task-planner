"""상태 줄 설정을 넣은 결과."""

from __future__ import annotations

from enum import StrEnum


class StatuslineSetup(StrEnum):
    WRITTEN = "written"  # 새로 넣었다. Claude Code 가 설정을 다시 읽은 뒤부터 보인다
    ALREADY = "already"  # 이미 같은 명령이 있다
    LEFT_ALONE = "left_alone"  # 다른 상태 줄이 있거나 파일을 읽지 못해 건드리지 않았다
