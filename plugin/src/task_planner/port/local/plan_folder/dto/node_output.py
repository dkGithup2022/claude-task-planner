"""노드의 마지막 회차 결과가 로컬에 놓인 모양. 제목과 상태는 담지 않는다 (원본은 계획 저장소)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class NodeOutput:
    round: int
    result_path: Path
    files: tuple[Path, ...]  # files/ 아래 파일 전부. 없으면 빈 튜플
