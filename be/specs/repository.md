# Repository (Entity, 쿼리, 구현체)

`packages/persistence/src/task_plan_server/persistence/`.

공통: StrEnum 컬럼은 `Enum(X, native_enum=False, length=255, values_callable=...)` 로 값(소문자)을 저장한다.

## plan

- `PlanEntity` (plans): personas 자식을 `relationship(lazy="selectin", cascade="all, delete-orphan", order_by=position)` 로 가진다. to_domain, from_domain, soft_delete
- `PlanPersonaEntity` (plan_personas): plan_id, persona_id, position
- `to_persona_entities(persona_ids)`: persona_ids 를 순서를 담은 자식 Entity 로
- `PlanEntityQuery`: find_by_id_and_active, get, add, flush
- `DefaultPlanRepository(tx, entities)`: save (수정 때 personas 를 통째로 바꾼다), find_write_by_id

공통: `enum_column.py` 의 `value_enum(kind)` 로 StrEnum 컬럼을 만든다.

## plan_node

- `PlanNodeEntity` (plan_nodes): plan_id 는 값으로만 (계획과 다른 aggregate). personas 자식 relationship (position 순)
- `PlanNodePersonaEntity` (plan_node_personas), `to_node_persona_entities(persona_ids)`
- `PlanNodeEntityQuery`: find_by_plan_id_and_active (id 순)
- `DefaultPlanNodeRepository(tx, entities)`: find_by_plan_id

## plan_edge

- `PlanEdgeEntity` (plan_edges): plan_id, from_node_id, to_node_id 는 값으로만
- `PlanEdgeEntityQuery`: find_by_plan_id_and_active (id 순)
- `DefaultPlanEdgeRepository(tx, entities)`: find_by_plan_id

## memory

- `MemoryEntity` (memories): personas, sources 자식 relationship (position 순)
- `MemoryPersonaEntity`, `MemorySourceEntity`, `to_memory_persona_entities`, `to_memory_source_entities`
- `MemoryEntityQuery`: find_by_id_and_active, get, add, flush
- `DefaultMemoryRepository(tx, entities)`: save, find_write_by_id

## persona

- `PersonaEntity` (personas)
- `PersonaJoinQuery`: find_all_with_counts → PersonaWithCountsRow. memory_count 는 지우지 않은 지식 중 memory_personas 에 있는 것, plan_count 는 지우지 않은 계획 중 plan_personas 에 있거나 지우지 않은 노드의 담당에 있는 것
- `PersonaEntityQuery`: get
- `DefaultPersonaRepository(tx, entities, joins)`: find_all
- `PlanJoinQuery` (plan): count_nodes_by_status(plan_ids) → PlanNodeCountsRow. 지우지 않은 노드를 상태별로 센다
- `PlanEntityQuery.find_all_and_active(status, limit)`: 만든 시각 최근 순
