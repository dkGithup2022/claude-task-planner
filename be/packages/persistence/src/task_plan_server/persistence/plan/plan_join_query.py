from dataclasses import dataclass

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class PlanNodeCountsRow:
    plan_id: int
    todo: int
    running: int
    done: int
    failed: int
    skipped: int


class PlanJoinQuery:
    """계획 목록에 붙일 노드 상태별 수. 노드 테이블에 걸치므로 SQL 로 한 번에 센다."""

    _NODE_COUNTS = text(
        """
        SELECT n.plan_id,
               count(*) FILTER (WHERE n.status = 'todo')    AS todo,
               count(*) FILTER (WHERE n.status = 'running') AS running,
               count(*) FILTER (WHERE n.status = 'done')    AS done,
               count(*) FILTER (WHERE n.status = 'failed')  AS failed,
               count(*) FILTER (WHERE n.status = 'skipped') AS skipped
        FROM plan_nodes n
        WHERE n.plan_id IN :plan_ids AND n.is_deleted = false
        GROUP BY n.plan_id
        """
    ).bindparams(bindparam("plan_ids", expanding=True))

    def __init__(self, session: Session) -> None:
        self._session = session

    def count_nodes_by_status(self, plan_ids: list[int]) -> list[PlanNodeCountsRow]:
        """노드가 없는 계획은 행이 없다."""
        if not plan_ids:
            return []
        rows = self._session.execute(self._NODE_COUNTS, {"plan_ids": plan_ids}).mappings().all()
        return [PlanNodeCountsRow(**row) for row in rows]
