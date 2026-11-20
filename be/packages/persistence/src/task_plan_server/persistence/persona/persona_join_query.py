from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True, slots=True)
class PersonaWithCountsRow:
    id: int
    name: str
    description: str
    created_at: datetime
    updated_at: datetime
    # 다른 aggregate 에서 센 수
    memory_count: int
    plan_count: int


class PersonaJoinQuery:
    """페르소나마다 쓰는 지식 수와 계획 수. 지식·계획·노드 테이블에 걸치므로 SQL 로 쓴다.

    계획은 참여 페르소나(plan_personas)에 있거나, 지우지 않은 노드의 담당에 있으면 센다.
    """

    _SELECT = """
        SELECT p.id, p.name, p.description, p.created_at, p.updated_at,
               (SELECT count(*) FROM memories m
                 WHERE m.is_deleted = false
                   AND EXISTS (SELECT 1 FROM memory_personas mp
                                WHERE mp.memory_id = m.id AND mp.persona_id = p.id)
               ) AS memory_count,
               (SELECT count(*) FROM plans pl
                 WHERE pl.is_deleted = false
                   AND (EXISTS (SELECT 1 FROM plan_personas pp
                                 WHERE pp.plan_id = pl.id AND pp.persona_id = p.id)
                        OR EXISTS (SELECT 1 FROM plan_nodes n
                                     JOIN plan_node_personas np ON np.node_id = n.id
                                    WHERE n.plan_id = pl.id AND n.is_deleted = false
                                      AND np.persona_id = p.id))
               ) AS plan_count
        FROM personas p
    """
    _ALL = text(_SELECT + " WHERE p.is_deleted = false ORDER BY p.id")
    _BY_ID = text(_SELECT + " WHERE p.id = :id AND p.is_deleted = false")

    def __init__(self, session: Session) -> None:
        self._session = session

    def find_all_with_counts(self) -> list[PersonaWithCountsRow]:
        rows = self._session.execute(self._ALL).mappings().all()
        return [PersonaWithCountsRow(**row) for row in rows]

    def find_by_id_with_counts(self, id: int) -> PersonaWithCountsRow | None:
        row = self._session.execute(self._BY_ID, {"id": id}).mappings().one_or_none()
        return PersonaWithCountsRow(**row) if row is not None else None
