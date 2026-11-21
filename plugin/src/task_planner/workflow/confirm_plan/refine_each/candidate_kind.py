"""지식 후보의 종류(plan, domain)를 지식 종류와 보일 이름으로 바꾼다."""

from __future__ import annotations

from task_planner.model.memory.memory_kind import MemoryKind


def memory_kind(candidate_type: str) -> MemoryKind:
    """plan 후보는 plan 지식, domain 후보는 knowledge 지식 (C 0 단계, 사용자 2026-11-18)."""
    return MemoryKind.PLAN if candidate_type == "plan" else MemoryKind.KNOWLEDGE


def type_label(candidate_type: str) -> str:
    """사용자에게 보일 종류 이름."""
    return "[계획]" if candidate_type == "plan" else "[도메인]"
