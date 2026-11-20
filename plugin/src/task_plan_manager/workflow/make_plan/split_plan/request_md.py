"""명령서 md 에서 목차별 글을 꺼내고, 프롬프트 입력에 넣을 수 있게 목차를 한 단계 내린다."""

from __future__ import annotations

import re

_HEADING = re.compile(r"^# (.+)$", re.MULTILINE)


def section(request_md: str, heading: str) -> str:
    """'# <heading>' 아래의 글. 목차가 없으면 빈 글."""
    parts = _HEADING.split(request_md)  # [머리말, 제목1, 본문1, 제목2, 본문2, …]
    for title, body in zip(parts[1::2], parts[2::2], strict=True):
        if title.strip() == heading:
            return body.strip()
    return ""


def demoted(request_md: str) -> str:
    """md 의 모든 목차를 한 단계 내린 글. 입력의 '# 명령서' 아래에 넣을 때 목차가 섞이지 않게."""
    return re.sub(r"^(#+) ", r"#\1 ", request_md, flags=re.MULTILINE)
