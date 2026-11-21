"""CounterWriter: 카운터 쓰기."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_planner.model.counter.counter import Counter


class CounterWriter(ABC):
    @abstractmethod
    def save(self, counter: Counter) -> None: ...
