"""저장 전 노드의 선행 작업 하나. 정의서의 needs 가운데 출처가 다른 작업인 것."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Prerequisite:
    local_id: str  # 선행 작업의 local_id
    what: str  # 그 작업에서 받을 것. 간선 정리 입력에 근거로 넣는다
