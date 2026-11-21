# Infrastructure (Repository port)

`packages/infrastructure/src/task_plan_server/infrastructure/` 의 ABC. service 는 이 문서의 시그니처에만 의존한다.

## plan — PlanRepository (`plan/plan_repository.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| save(plan: Plan) | Plan | 계획 저장 (신규·수정). 참여 페르소나 순서를 지킨다 |
| find_write_by_id(identity: PlanIdentity) | Plan \| None | 계획 Write 모델 조회. 지운 계획은 없음으로 본다 |

## plan_node — PlanNodeRepository (`plan_node/plan_node_repository.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| find_by_plan_id(plan_identity: PlanIdentity) | list[PlanNodeRead] | 계획의 노드 전부. 지운 노드는 뺀다. node_id 순 |

## plan_edge — PlanEdgeRepository (`plan_edge/plan_edge_repository.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| find_by_plan_id(plan_identity: PlanIdentity) | list[PlanEdgeRead] | 계획의 간선 전부. 지운 간선은 뺀다. edge_id 순 |
| save(node: PlanNode) | PlanNode | (plan_node) 노드 저장 (신규·수정). 담당 페르소나 순서를 지킨다 |
| find_write_by_id(identity: PlanNodeIdentity) | PlanNode \| None | (plan_node) 노드 Write 모델 조회. 지운 노드는 없음 |
| delete_by_id(identity: PlanNodeIdentity) | None | (plan_node) soft-delete. 이미 지웠으면 no-op. 간선은 지우지 않는다 |
| delete_by_node_id(node_identity: PlanNodeIdentity) | None | (plan_edge) 앞이나 뒤가 이 노드인 간선 모두 soft-delete |
| save(edge: PlanEdge) | PlanEdge | (plan_edge) 간선 저장. 신규만 (간선은 고치지 않는다) |
| find_by_ends(plan_identity, from_node_id: int, to_node_id: int) | PlanEdge \| None | (plan_edge) 계획에서 앞·뒤가 같은 간선. 지운 간선 제외 |
| find_write_by_id(identity: PlanEdgeIdentity) | PlanEdge \| None | (plan_edge) 간선 Write 모델 조회. 지운 간선 제외 |
| delete_by_id(identity: PlanEdgeIdentity) | None | (plan_edge) soft-delete. 이미 지웠으면 no-op |

## memory — MemoryRepository (`memory/memory_repository.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| save(memory: Memory, terms: MemorySearchTerms) | Memory | 지식 저장 (신규·수정). 페르소나와 근거의 순서를 지킨다. 검색용 낱말도 같이 저장 |
| save_search_terms(identity: MemoryIdentity, terms: MemorySearchTerms) | None | 검색용 낱말만 바꾼다. 고친 시각 그대로. 지운 지식이면 no-op |
| find_ids_without_search_terms() | list[MemoryIdentity] | 검색용 낱말이 빈 지식 (지운 것 뺌). 직접 넣은 데이터를 채울 때 |
| find_write_by_id(identity: MemoryIdentity) | Memory \| None | 지식 Write 모델 조회. 지운 지식은 없음 |
| find_by_id(identity: MemoryIdentity) | MemoryRead \| None | (memory) 지식 조회 (덧붙인 횟수, 근거 계획 포함). 지운 지식 없음 |
| delete_by_id(identity: MemoryIdentity) | None | (memory) soft-delete. 이미 지웠으면 no-op |

## memory — KnowledgeSearcher (`memory/knowledge_searcher.py`)

검색 port. 구현을 바꿔 끼울 수 있게 MemoryRepository 와 따로 둔다 (지시서 5절).

| 메서드 | 반환 | 설명 |
|---|---|---|
| search_knowledge(search_param: SearchParam, query_terms: tuple[str, ...]) | list[MemorySearchHit] | 같은 종류, 페르소나가 겹치는, theme 을 주면 작업 이름이 같은 지식을 검색어 낱말과 가까운 순으로 limit 개. 낱말이 없으면 고친 시각 최근 순 |

구현 `DefaultKnowledgeSearcher` (persistence): `memories.search_tokens` (tsvector, simple) 에 낱말 OR 질의로 `@@`, `ts_rank(…, 32)` 점수 순, 같으면 고친 시각 최근 순 (2026-11-21, 한국어 형태소 검색)

(memory — MemoryRepository 계속)

| 메서드 | 반환 | 설명 |
|---|---|---|
| find_by_condition(condition: MemoryListCondition) | list[MemoryRead] | 조건에 맞는 지식을 고친 시각 최근 순으로 limit 개 |
| count_by_condition(condition: MemoryListCondition) | int | 조건에 맞는 지식 수 (limit 무시) |

## persona — PersonaRepository (`persona/persona_repository.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| find_all() | list[PersonaRead] | 지우지 않은 페르소나 전부. persona_id 순. 쓰는 지식 수와 계획 수 |
| save(persona: Persona) | Persona | (persona) 저장 (신규·수정) |
| exists_by_name(name: str, exclude: PersonaIdentity \| None) | bool | (persona) 지우지 않은 페르소나 가운데 이 이름이 있는지. exclude 는 뺀다 |
| find_write_by_id(identity: PersonaIdentity) | Persona \| None | (persona) Write 모델 조회. 지운 페르소나 제외 |
| find_by_id(identity: PersonaIdentity) | PersonaRead \| None | (persona) 페르소나 하나와 쓰는 지식 수·계획 수 |
| delete_by_id(identity: PersonaIdentity) | None | (persona) soft-delete. 쓰는 곳 검사는 부르는 쪽 |
| find_summaries(status: PlanStatus \| None, limit: int \| None) | list[PlanSummary] | (plan) 계획 목록. 만든 시각 최근 순. 지우지 않은 노드의 상태별 수 |
| find_missing_ids(persona_ids: list[int]) | list[int] | (persona) 지우지 않은 페르소나에 없는 id. 받은 순서, 겹치지 않게 |

## memory — TextTokenizer (`memory/text_tokenizer.py`)

글을 검색용 낱말로 나누는 port (2026-11-21). 구현 `KiwiTextTokenizer` (persistence, kiwipiepy).

| 메서드 | 반환 | 설명 |
|---|---|---|
| tokens(text: str) | tuple[str, ...] | 검색에 쓸 낱말 (명사, 영문, 동사·형용사 어간). 나온 순서대로, 겹쳐도 그대로 |
