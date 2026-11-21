"""불허한 계획. 상태 줄에 아무것도 보이지 않는다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClosedProgress:
    pass
