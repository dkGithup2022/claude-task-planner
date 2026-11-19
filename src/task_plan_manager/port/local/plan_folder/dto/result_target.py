"""서브에이전트가 결과를 쓸 위치."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ResultTarget:
    result_path: Path  # result.md 의 절대 경로
    files_dir: Path  # 결과가 여러 파일일 때 쓸 files/ 의 절대 경로
