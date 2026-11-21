"""진행 기록 읽기 구현. 계획마다 progress.jsonl 의 끝만 읽는다."""

from __future__ import annotations

import json
from pathlib import Path

from task_planner.model.progress.progress_event import ProgressEvent
from task_planner.port.local.plan_folder.plan_folder_location import plan_root, progress_file
from task_planner.port.local.progress_log.progress_event_file_converter import ProgressEventFileConverter
from task_planner.port.local.progress_log.progress_log_reader import ProgressLogReader

TAIL_BYTES = 64 * 1024  # 파일 끝에서 읽을 양. 기록 한 줄은 이보다 훨씬 작다


class DefaultProgressLogReader(ProgressLogReader):
    def latest_for_session(self, session_id: str) -> ProgressEvent | None:
        # 계획마다 이 세션이 쓴 마지막 줄을 찾고, 그 가운데 가장 최근 것을 고른다
        found = [event for path in _progress_files() if (event := _last_event_of(path, session_id)) is not None]
        return max(found, key=lambda event: event.at, default=None)


def _progress_files() -> list[Path]:
    root = plan_root()
    if not root.is_dir():
        return []
    candidates = [progress_file(int(folder.name)) for folder in root.iterdir() if folder.name.isdigit()]
    return [path for path in candidates if path.is_file()]


def _last_event_of(path: Path, session_id: str) -> ProgressEvent | None:
    """파일 끝에서부터 이 세션이 쓴 줄을 찾는다. 쓰는 중이라 반쯤 잘린 줄은 건너뛴다."""
    converter = ProgressEventFileConverter()
    for line in reversed(_tail_lines(path)):
        try:
            row = json.loads(line)
            if row.get("session_id") == session_id:
                return converter.to_data(row)
        except (ValueError, KeyError, TypeError):
            continue
    return None


def _tail_lines(path: Path) -> list[str]:
    """파일 끝 TAIL_BYTES 안의 온전한 줄들. 맨 앞의 잘렸을 수 있는 줄은 뺀다."""
    with path.open("rb") as file:
        size = file.seek(0, 2)
        start = max(0, size - TAIL_BYTES)
        file.seek(start)
        text = file.read().decode("utf-8", errors="ignore")
    # 기록 사이는 "\n" 으로만 나눈다. splitlines 는 제목 안의 U+2028 같은 문자에서도 줄을 나눠 기록을 깨뜨린다
    lines = [line for line in text.split("\n") if line.strip()]
    return lines[1:] if start > 0 else lines
