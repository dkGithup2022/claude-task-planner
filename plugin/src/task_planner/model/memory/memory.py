"""지식 하나. 작업 이름(theme) 아래 md 본문(body). 덧붙일 때마다 본문과 근거가 뒤에 붙는다."""

from __future__ import annotations

from dataclasses import dataclass, replace

from task_planner.model.memory.memory_kind import MemoryKind
from task_planner.model.memory.memory_source import MemorySource

APPENDED_MARK = "****** KNOWLEDGE APPENDED {number} ********"  # 덧붙인 본문의 머리 (사용자, 2026-11-19)


@dataclass(frozen=True, slots=True)
class Memory:
    memory_id: int
    kind: MemoryKind
    theme: str  # 작업 이름. 가능하면 "{대상} {행위}"
    body: str  # md. 설명과 예시
    persona_ids: tuple[int, ...]
    sources: tuple[MemorySource, ...]

    def append(self, body: str, sources: tuple[MemorySource, ...]) -> Memory:
        """본문 뒤에 '****** KNOWLEDGE APPENDED <n> ********' 머리를 달아 덧붙이고, 근거를 뒤에 붙인 새 지식."""
        number = self.body.count("****** KNOWLEDGE APPENDED ") + 1
        appended_body = f"{self.body}\n\n{APPENDED_MARK.format(number=number)}\n{body}"
        return replace(self, body=appended_body, sources=self.sources + sources)
