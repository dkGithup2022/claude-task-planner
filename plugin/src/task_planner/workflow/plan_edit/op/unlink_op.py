"""간선 하나를 지운다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UnlinkOp:
    """간선 하나를 지운다."""

    from_node_id: int
    to_node_id: int
