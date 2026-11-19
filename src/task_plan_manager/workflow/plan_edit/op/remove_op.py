"""노드를 빼고 앞뒤를 바로 잇는다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RemoveOp:
    """노드를 빼고 앞뒤를 바로 잇는다."""

    node_id: int
