# Usecase (service)

`packages/service/src/task_plan_server/service/`. 이 서비스에는 로그인 사용자가 없다. 그래서 Command 에 `request_user_id` 가 없고 `execute` 에 user_id 인자가 없다.

## plan

### PlanReader (`plan/plan_reader.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| get_by_id(identity: PlanIdentity) | PlanRead | 계획, 노드, 간선을 각 Repository 로 읽어 묶는다. 없으면 PlanNotFoundException. 트랜잭션을 열지 않는다 |

### PlanWriter (`plan/plan_writer.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| create(command: PlanCreateCommand) | PlanIdentity | 새 계획. 상태는 drafting |
| change_status(command: PlanStatusChangeCommand) | Plan | 상태를 바꾼다. 순서는 검사하지 않는다. 없으면 PlanNotFoundException |

### Command

- `PlanCreateCommand(title: str, request: str, persona_ids: tuple[int, ...])`
- `PlanStatusChangeCommand(plan_id: int, status: PlanStatus)`

### Usecase

| Usecase | execute | 설명 |
|---|---|---|
| PlanCreateUsecase | execute(command: PlanCreateCommand) -> PlanRead | 만들고 다시 읽어 노드·간선이 빈 PlanRead 를 돌려준다. @transactional, 부수효과 없음 |
| PlanStatusChangeUsecase | execute(command: PlanStatusChangeCommand) -> PlanRead | 상태를 바꾸고 PlanReader 로 다시 읽는다. 한 트랜잭션 |

### DI

- `PlanProvider`: PlanEntityQuery, DefaultPlanRepository → PlanRepository, DefaultPlanReader → PlanReader, DefaultPlanWriter → PlanWriter, PlanCreateUsecase, PlanStatusChangeUsecase
- `PlanNodeProvider`: PlanNodeEntityQuery, DefaultPlanNodeRepository → PlanNodeRepository
- `PlanEdgeProvider`: PlanEdgeEntityQuery, DefaultPlanEdgeRepository → PlanEdgeRepository

## plan_node

### PlanNodeWriter (`plan_node/plan_node_writer.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| create(command: PlanNodeCreateCommand) | PlanNodeIdentity | 새 노드. 상태는 todo |
| delete(identity: PlanNodeIdentity) | None | 노드를 지운다. 없으면 404. 간선은 지우지 않는다 |
| update(command: PlanNodeUpdateCommand) | PlanNode | 값이 있는 필드만 바꾼다. 없거나 다른 계획의 노드면 PlanNodeNotFoundException |

### Command

- `PlanNodeCreateCommand(plan_id: int, title: str, kind: NodeKind, persona_ids: tuple[int, ...], output_spec: str)`
- `PlanNodeUpdateCommand(plan_id, node_id, title | None, kind | None, persona_ids | None, output_spec | None, status | None)`: None 은 바꾸지 않음

### Usecase

| Usecase | execute | 설명 |
|---|---|---|
| PlanNodeCreateUsecase | execute(command) -> PlanNodeRead | 계획이 없으면 PlanNotFoundException(404). 만들고 다시 읽는다. PlanRepository 주입 |
| PlanNodeUpdateUsecase | execute(command) -> PlanNodeRead | Writer.update 를 감싼다 |
| PlanNodeDeleteUsecase | execute(plan_id, node_id) -> None | 노드와 닿은 간선을 한 트랜잭션으로 지운다. 없거나 다른 계획의 노드면 아무것도 하지 않는다. PlanEdgeRepository 주입 |

## plan_edge

### PlanEdgeWriter (`plan_edge/plan_edge_writer.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| create(command: PlanEdgeCreateCommand) | PlanEdgeIdentity | 새 간선 |
| delete(identity: PlanEdgeIdentity) | None | 간선을 지운다. 없으면 404 |

### Command·결과

- `PlanEdgeCreateCommand(plan_id: int, from_node_id: int, to_node_id: int)`
- `PlanEdgeCreated(edge: PlanEdgeRead, created: bool)`: 같은 간선이 있었으면 created=False

### Usecase

| Usecase | execute | 설명 |
|---|---|---|
| PlanEdgeCreateUsecase | execute(command) -> PlanEdgeCreated | 계획 없음 404, 양 끝 노드가 그 계획에 없음 400, 같은 간선이면 그것을 돌려준다. 자기 자신 잇기·순환은 막지 않는다. PlanRepository, PlanNodeRepository 주입 |
| PlanEdgeDeleteUsecase | execute(plan_id, edge_id) -> None | 없거나 다른 계획의 간선이면 아무것도 하지 않는다 |

## memory

### MemoryReader (`memory/memory_reader.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| get_by_id(identity: MemoryIdentity) | MemoryRead | 없으면 MemoryNotFoundException |
| search(search_param: SearchParam) | list[MemorySearchHit] | 검색어를 `query_terms_of` 로 낱말로 나눈다. 낱말이 없으면 (검색어가 비었거나 숫자, 기호, 조사만) 벡터 검색을 켜도 []. 벡터 검색을 끄면 전문 검색만 (`_full_text_search`: KnowledgeSearcher 에 위임). 켜면 `_hybrid_search`: 전문 검색 30 개 + 벡터 검색 30 개를 `reciprocal_rank_fusion` 으로 합쳐 앞에서 limit 개, 점수는 RRF 점수 (2026-11-21) |
| get_list(condition: MemoryListCondition) | MemoryList(items, total) | 웹 목록. 고친 시각 최근 순 |

### MemoryWriter (`memory/memory_writer.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| create(command: MemoryCreateCommand) | MemoryIdentity | 새 지식. 본문과 근거는 받은 그대로. 검색용 낱말을 만들어 같이 저장. 벡터 검색을 켰으면 벡터도 (끄면 벡터를 비움) |
| delete(identity: MemoryIdentity) | None | 지식을 지운다. 없으면 404 |
| update(command: MemoryUpdateCommand) | Memory | 값이 있는 필드만 받은 그대로 바꾼다. 검색용 낱말을 다시 만들어 같이 저장. 벡터 검색을 켰으면 벡터도 (끄면 벡터를 비움). 없으면 404 |

### Command

- `MemoryCreateCommand(kind, theme, body, persona_ids: tuple[int, ...], sources: tuple[MemorySource, ...])`
- `MemoryUpdateCommand(memory_id, kind | None, theme | None, body | None, persona_ids | None, sources | None)`

### Usecase

| Usecase | execute | 설명 |
|---|---|---|
| MemoryCreateUsecase | execute(command) -> MemoryIdentity | Writer.create 를 감싼다 |
| MemoryUpdateUsecase | execute(command) -> MemoryIdentity | Writer.update 를 감싼다 |
| MemoryDeleteUsecase | execute(identity) -> None | Writer.delete 를 감싼다. 없으면 404 |
| MemorySearchTermsRefreshUsecase | execute() -> int | 검색용 낱말이 빈 지식(지운 것 뺌)을 채운다. 고친 시각 그대로. 채운 수. 라우터 없음, 서버가 시작할 때 app lifespan 이 부른다 (2026-11-21) |
| MemoryEmbeddingRefreshUsecase | execute() -> int | 검색용 벡터가 비었거나 다른 모델로 만든 지식(지운 것 뺌)의 벡터를 다시 만든다. 고친 시각 그대로. 다시 만든 수, 꺼져 있으면 0. 라우터 없음, 서버가 시작할 때 app lifespan 이 부른다 (2026-11-21) |

## persona

### PersonaReader (`persona/persona_reader.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| get_all() | list[PersonaRead] | 지우지 않은 페르소나 전부. persona_id 순 |

### PersonaWriter (`persona/persona_writer.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| create(command: PersonaCreateCommand) | PersonaIdentity | 같은 이름이 있으면 PersonaNameDuplicatedException(409) |

- `PersonaCreateCommand(name, description)`
- PersonaCreateUsecase.execute(command) -> PersonaIdentity
- PersonaWriter.update(command: PersonaUpdateCommand) -> Persona: 값이 있는 필드만. 없으면 404, 다른 페르소나와 이름이 같으면 409
- `PersonaUpdateCommand(persona_id, name | None, description | None)`, PersonaUpdateUsecase.execute(command) -> PersonaIdentity
- PersonaWriter.delete(identity) -> None: 없으면 404
- PersonaDeleteUsecase.execute(identity) -> None: 쓰는 지식·계획이 있으면 PersonaInUseException(409, "지식 n개, 계획 m개가 이 페르소나를 씁니다")
- PlanReader.get_summaries(status, limit) -> list[PlanSummary]

## 공통: 페르소나 id 검사 (`service/persona/persona_check.py`)

`require_personas(repository, persona_ids)`: 없는(지운) 페르소나가 있으면 UnknownPersonaException(400, "페르소나 n 가 없습니다"). MemoryCreate, MemoryUpdate, PlanCreate, PlanNodeCreate, PlanNodeUpdate Usecase 가 Writer 전에 부른다. None·빈 목록은 보지 않는다 (사용자, 2026-11-20)

### memory 검색용 낱말 (`memory/search_terms/`, 2026-11-21)

저장(인덱싱)과 검색이 같은 규칙으로 낱말을 만든다. tokenizer 는 `TextTokenizer` (구현 KiwiTextTokenizer, Scope.APP)
- `memory_search_terms_of(tokenizer, theme, body) -> MemorySearchTerms`: 작업 이름과 본문을 따로 나눈다. DefaultMemoryWriter 의 create·update, MemorySearchTermsRefreshUsecase 가 쓴다
- `query_terms_of(tokenizer, query) -> tuple[str, ...]`: 검색어 낱말. 겹친 것은 처음 것만. DefaultMemoryReader.search 가 쓴다
- `embedding_of(embedder, theme, body) -> MemoryEmbedding`: 저장할 지식의 벡터. 작업 이름과 본문을 줄바꿈으로 잇는다 (2026-11-21)
- DefaultMemoryWriter(tx, repository, tokenizer, embedder), DefaultMemoryReader(repository, searcher, tokenizer, embedder). embedder 는 `TextEmbedder` (Scope.APP, 설정 `memory_search_vector` 로 FastembedTextEmbedder 또는 DisabledTextEmbedder)

### memory 검색 결과 합치기 (`memory/search_rank/`, 2026-11-21)
- `reciprocal_rank_fusion(*rankings) -> list[MemorySearchHit]`: 지식마다 1 / (60 + 순위) 를 더한 점수 순. 같으면 먼저 넘긴 목록에서 먼저 나온 것이 앞
- `CANDIDATE_COUNT = 30` (DefaultMemoryReader): 켰을 때 전문 검색과 벡터 검색이 각각 가져올 후보 수
