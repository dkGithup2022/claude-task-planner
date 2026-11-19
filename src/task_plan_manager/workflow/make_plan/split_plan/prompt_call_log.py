"""split_plan 단계 안에서 부른 claude -p 의 요청·응답을 남긴다.
engine 은 CODE 단계 안의 호출을 기록하지 않으므로, CLAUDE_P 단계의 calls/<n>/ 와 같은 모양으로 직접 남긴다."""

from __future__ import annotations

import threading
from pathlib import Path

from task_plan_manager.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_plan_manager.common import files


class PromptCallLog:
    def __init__(self, folder: Path) -> None:
        self.folder = folder  # 이 아래에 calls/<호출 묶음>/<n>/ 가 생긴다
        self._lock = threading.Lock()  # 동시 호출이 같은 번호를 쓰지 않게
        self._counts: dict[str, int] = {}

    def save(self, group: str, record: PromptCallRecord) -> None:
        """호출 묶음(split, spec, edges) 안에서 다음 번호의 폴더에 요청과 응답을 쓴다."""
        with self._lock:
            self._counts[group] = self._counts.get(group, 0) + 1
            call_dir = self.folder / "calls" / group / str(self._counts[group])
        files.write_json(call_dir / "request.json", record.request)
        files.write_json(call_dir / "response.json", record.response)
