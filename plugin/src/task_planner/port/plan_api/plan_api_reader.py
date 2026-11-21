"""계획 저장소 읽기. 지금은 mock, 나중에 서버 API."""

from __future__ import annotations

from abc import ABC, abstractmethod

from task_planner.model.plan.plan import Plan


class PlanApiReader(ABC):
    @abstractmethod
    def get_plan(self, plan_id: int) -> Plan:
        """노드와 간선까지 담은 계획 (GET /plans/{plan_id}). 없으면 PlanNotFoundError."""
