"""계획 폴더나 그 안의 파일이 없음."""

from __future__ import annotations


class PlanFolderMissingError(FileNotFoundError):
    """읽으려는 계획 폴더의 파일이 없다. 메시지에 경로를 담는다."""
