"""만들려는 계획 폴더가 다른 내용으로 이미 있음."""

from __future__ import annotations


class PlanFolderExistsError(FileExistsError):
    """같은 계획 id 의 폴더에 다른 명령서가 이미 있다. 덮어쓰지 않는다."""
