"""나눈 노드들을 잇는 방법."""

from __future__ import annotations

from enum import StrEnum


class SplitOrder(StrEnum):
    """나눈 노드들을 잇는 방법."""

    SERIAL = "serial"  # 차례로: 앞 노드들 → 첫 → … → 끝 → 뒤 노드들
    PARALLEL = "parallel"  # 동시에: 앞 노드들 → 새 노드 각각 → 뒤 노드들
