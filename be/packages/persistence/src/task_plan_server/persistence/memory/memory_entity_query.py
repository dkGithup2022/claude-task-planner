from sqlalchemy import ColumnElement, Select, func, literal, literal_column, or_, select, update
from sqlalchemy.dialects.postgresql import REGCONFIG
from sqlalchemy.orm import Session

from task_plan_server.model.memory.memory_kind import MemoryKind
from task_plan_server.model.memory.memory_list_condition import MemoryListCondition
from task_plan_server.model.memory.memory_search_terms import MemorySearchTerms

from .memory_entity import MemoryEntity
from .memory_persona_entity import MemoryPersonaEntity


class MemoryEntityQuery:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id_and_active(self, id: int) -> MemoryEntity | None:
        stmt = select(MemoryEntity).where(MemoryEntity.id == id, MemoryEntity.is_deleted.is_(False))
        return self._session.scalar(stmt)

    def get(self, id: int) -> MemoryEntity | None:
        return self._session.get(MemoryEntity, id)

    def add(self, entity: MemoryEntity) -> MemoryEntity:
        self._session.add(entity)
        self._session.flush()
        return entity

    def flush(self) -> None:
        self._session.flush()

    def find_for_search_and_active(
        self, kind: MemoryKind, persona_ids: list[int], theme: str | None
    ) -> list[MemoryEntity]:
        """검색 대상. kind 가 같고 페르소나가 겹치고, theme 을 주면 작업 이름이 같은 지식."""
        if not persona_ids:
            return []
        overlapping = select(MemoryPersonaEntity.memory_id).where(
            MemoryPersonaEntity.persona_id.in_(persona_ids)
        )
        stmt = select(MemoryEntity).where(
            MemoryEntity.kind == kind,
            MemoryEntity.id.in_(overlapping),
            MemoryEntity.is_deleted.is_(False),
        )
        if theme is not None:
            stmt = stmt.where(MemoryEntity.theme == theme)
        return list(self._session.scalars(stmt.order_by(MemoryEntity.updated_at.desc())).all())

    def find_for_search_by_terms_and_active(
        self,
        kind: MemoryKind,
        persona_ids: list[int],
        theme: str | None,
        query_terms: tuple[str, ...],
        limit: int,
    ) -> list[tuple[MemoryEntity, float]]:
        """검색 대상 가운데 낱말이 하나라도 맞는 지식과 그 점수 (ts_rank, 0~1).

        점수 높은 순, 같으면 고친 시각 최근 순으로 limit 개.
        거르기는 find_for_search_and_active 와 같다.
        """
        if not persona_ids or not query_terms:
            return []
        query = _any_term_query(query_terms)
        score = func.ts_rank(MemoryEntity.search_tokens, query, 32)
        overlapping = select(MemoryPersonaEntity.memory_id).where(
            MemoryPersonaEntity.persona_id.in_(persona_ids)
        )
        stmt = select(MemoryEntity, score).where(
            MemoryEntity.kind == kind,
            MemoryEntity.id.in_(overlapping),
            MemoryEntity.is_deleted.is_(False),
            MemoryEntity.search_tokens.op("@@")(query),
        )
        if theme is not None:
            stmt = stmt.where(MemoryEntity.theme == theme)
        stmt = stmt.order_by(score.desc(), MemoryEntity.updated_at.desc()).limit(max(0, limit))
        return [(entity, float(rank)) for entity, rank in self._session.execute(stmt).all()]

    def update_search_tokens_by_id_and_active(self, id: int, terms: MemorySearchTerms) -> None:
        """검색용 낱말만 바꾼다. updated_at 의 onupdate 가 돌지 않게 지금 값을 그대로 넣는다."""
        stmt = (
            update(MemoryEntity)
            .where(MemoryEntity.id == id, MemoryEntity.is_deleted.is_(False))
            .values(search_tokens=search_tokens_of(terms), updated_at=MemoryEntity.updated_at)
        )
        self._session.execute(stmt)

    def find_ids_without_search_tokens_and_active(self) -> list[int]:
        """검색용 낱말이 비어 있는 지식의 id. 지운 것은 뺀다."""
        stmt = select(MemoryEntity.id).where(
            func.length(MemoryEntity.search_tokens) == 0, MemoryEntity.is_deleted.is_(False)
        )
        return list(self._session.scalars(stmt.order_by(MemoryEntity.id)).all())

    def find_by_condition_and_active(self, condition: MemoryListCondition) -> list[MemoryEntity]:
        stmt = _where_condition(select(MemoryEntity), condition).order_by(
            MemoryEntity.updated_at.desc(), MemoryEntity.id.desc()
        )
        if condition.limit is not None:
            stmt = stmt.limit(condition.limit)
        return list(self._session.scalars(stmt).all())

    def count_by_condition_and_active(self, condition: MemoryListCondition) -> int:
        stmt = _where_condition(select(func.count()).select_from(MemoryEntity), condition)
        return int(self._session.scalar(stmt) or 0)


def _where_condition[T](stmt: Select[T], condition: MemoryListCondition) -> Select[T]:
    """웹 목록의 동적 조건. 비운 조건은 붙이지 않는다. 검색어의 % 와 _ 는 글자 그대로 찾는다."""
    stmt = stmt.where(MemoryEntity.is_deleted.is_(False))
    if condition.query:
        stmt = stmt.where(
            or_(
                MemoryEntity.theme.icontains(condition.query, autoescape=True),
                MemoryEntity.body.icontains(condition.query, autoescape=True),
            )
        )
    if condition.kind is not None:
        stmt = stmt.where(MemoryEntity.kind == condition.kind)
    if condition.persona_id is not None:
        using = select(MemoryPersonaEntity.memory_id).where(
            MemoryPersonaEntity.persona_id == condition.persona_id
        )
        stmt = stmt.where(MemoryEntity.id.in_(using))
    return stmt


# 낱말을 그대로 쓴다. 한국어 형태소 분석은 서버(kiwi)가 먼저 했다
SIMPLE = literal("simple", type_=REGCONFIG)
# setweight 의 무게는 "char" 타입이라 바인드 값(varchar)이 아닌 SQL 상수로 넣는다
WEIGHT_A: ColumnElement[str] = literal_column("'A'")
WEIGHT_B: ColumnElement[str] = literal_column("'B'")


def search_tokens_of(terms: MemorySearchTerms) -> ColumnElement[str]:
    """search_tokens 에 넣을 값. 작업 이름 낱말은 무게 A, 본문 낱말은 무게 B."""
    theme = func.setweight(func.to_tsvector(SIMPLE, " ".join(terms.theme)), WEIGHT_A)
    body = func.setweight(func.to_tsvector(SIMPLE, " ".join(terms.body)), WEIGHT_B)
    return theme.op("||")(body)


def _any_term_query(query_terms: tuple[str, ...]) -> ColumnElement[str]:
    """낱말 가운데 하나라도 맞으면 참인 질의.

    낱말마다 plainto_tsquery 로 따로 묶어 기호가 섞여도 안전하다.
    """
    queries = [func.plainto_tsquery(SIMPLE, term) for term in query_terms]
    combined: ColumnElement[str] = queries[0]
    for query in queries[1:]:
        combined = combined.op("||")(query)
    return combined
