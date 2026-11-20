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
| search(search_param: SearchParam) | list[MemorySearchHit] | KnowledgeSearcher 에 위임 |
| get_list(condition: MemoryListCondition) | MemoryList(items, total) | 웹 목록. 고친 시각 최근 순 |

### MemoryWriter (`memory/memory_writer.py`)

| 메서드 | 반환 | 설명 |
|---|---|---|
| create(command: MemoryCreateCommand) | MemoryIdentity | 새 지식. 본문과 근거는 받은 그대로 |
| delete(identity: MemoryIdentity) | None | 지식을 지운다. 없으면 404 |
| update(command: MemoryUpdateCommand) | Memory | 값이 있는 필드만 받은 그대로 바꾼다. 없으면 404 |

### Command

- `MemoryCreateCommand(kind, theme, body, persona_ids: tuple[int, ...], sources: tuple[MemorySource, ...])`
- `MemoryUpdateCommand(memory_id, kind | None, theme | None, body | None, persona_ids | None, sources | None)`

### Usecase

| Usecase | execute | 설명 |
|---|---|---|
| MemoryCreateUsecase | execute(command) -> MemoryIdentity | Writer.create 를 감싼다 |
| MemoryUpdateUsecase | execute(command) -> MemoryIdentity | Writer.update 를 감싼다 |
| MemoryDeleteUsecase | execute(identity) -> None | Writer.delete 를 감싼다. 없으면 404 |

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
