# 도메인 모델

model 패키지(`packages/model/src/task_plan_server/model/`)와 도메인 예외(`packages/exception/src/task_plan_server/exception/`)의 정리본이다. add-model 이 도메인을 더할 때마다 고친다.

## persona

출처: `specs/plans/model-persona.md`

### Persona (`persona/persona.py`)

작업을 맡는 역할. 이름은 페르소나마다 다르다.

| 필드 | 타입 | 설명 |
|---|---|---|
| persona_id | int \| None | 서버가 준다. 저장 전에는 None |
| name | str | 예: dankim-persona. 같은 이름은 둘 수 없다 |
| description | str | |
| created_at | datetime | 서버 안에만 둔다. API 응답에 넣지 않는다 |
| updated_at | datetime | 서버 안에만 둔다. API 응답에 넣지 않는다 |

- `create(name, description)`: 새 페르소나
- `with_profile(name, description)`: 이름과 설명을 바꾼 새 페르소나
- `to_read(memory_count, plan_count) -> PersonaRead`: 지식 수와 계획 수는 부르는 쪽이 세어서 넘긴다

### PersonaRead (`persona/persona_read.py`)

persona_id: int, name, description, memory_count: int, plan_count: int, created_at, updated_at

### PersonaIdentity (`persona/persona_identity.py`)

persona_id: int

### 예외 (`exception/persona/`)

| 예외 | 코드 | 사용자에게 보이는 메시지 | 쓰는 곳 |
|---|---|---|---|
| PersonaNotFoundException | 404 | 해당 리소스를 찾을 수 없습니다 | 조회, 고치기, 지우기 |
| PersonaInUseException(persona_id, memory_count, plan_count) | 409 | 지식 {n}개, 계획 {m}개가 이 페르소나를 씁니다 | 지우기 |
| PersonaNameDuplicatedException(name) | 409 | 이름이 {name} 인 페르소나가 이미 있습니다 | 만들기, 고치기 |

## memory

출처: `specs/plans/model-memory.md`

### MemoryKind (`memory/memory_kind.py`)

KNOWLEDGE = "knowledge" (작업 방법·규칙), ATTITUDE = "attitude" (판단 방식), PLAN = "plan" (작업을 나누는 방식). 값은 CLI 와 같은 소문자다.

### MemorySource (`memory/memory_source.py`)

quote: str (사용자가 한 말), plan_id: int (그 말이 나온 계획)

### Memory (`memory/memory.py`)

| 필드 | 타입 | 설명 |
|---|---|---|
| memory_id | int \| None | 서버가 준다 |
| kind | MemoryKind | |
| theme | str | 작업 이름 |
| body | str | md. CLI 가 만든 그대로 저장한다 |
| persona_ids | tuple[int, ...] | 적용할 페르소나 |
| sources | tuple[MemorySource, ...] | 근거. API 필드 이름은 `source` |
| created_at, updated_at | datetime | 서버가 채운다 |

- `create(kind, theme, body, persona_ids, sources)`
- `with_update(kind, theme, body, persona_ids, sources)`: 바꾸지 않는 필드는 부르는 쪽이 지금 값으로 채운다
- `to_read() -> MemoryRead`
- `APPENDED_MARK_PREFIX = "****** KNOWLEDGE APPENDED "`: CLI 가 다는 덧붙임 머리의 앞부분

### MemoryRead (`memory/memory_read.py`)

Memory 의 필드 + appended_count: int (본문에 덧붙임 머리가 나온 횟수), source_plan_ids: tuple[int, ...] (근거의 계획. 처음 나온 순서, 겹치지 않음)

### MemoryIdentity (`memory/memory_identity.py`)

memory_id: int

### SearchParam (`memory/search_param.py`)

kind: MemoryKind, query: str, persona_ids: tuple[int, ...], theme: str | None = None, limit: int = 10. `search_knowledge(search_param)` 인터페이스의 인자.

### MemorySearchHit (`memory/memory_search_hit.py`)

memory_id: int, kind: MemoryKind, theme: str, body: str, score: float

### 예외 (`exception/memory/`)

| 예외 | 코드 | 쓰는 곳 |
|---|---|---|
| MemoryNotFoundException | 404 | 조회, 고치기, 지우기 |

## plan_node

출처: `specs/plans/model-plan-node.md`

### NodeKind (`plan_node/node_kind.py`)

DOCUMENT = "document", RESEARCH = "research", CODE = "code", HITL = "hitl" (사용자 확인). 값은 CLI 와 같은 소문자다.

### PlanNodeStatus (`plan_node/plan_node_status.py`)

TODO = "todo", RUNNING = "running", DONE = "done", FAILED = "failed", SKIPPED = "skipped". 서버는 바꾸는 순서를 검사하지 않는다.

### PlanNode (`plan_node/plan_node.py`)

| 필드 | 타입 | 설명 |
|---|---|---|
| node_id | int \| None | 서버가 준다 |
| plan_id | int | 어느 계획의 노드인지. API 응답에는 넣지 않는다 |
| title | str | |
| kind | NodeKind | |
| persona_ids | tuple[int, ...] | 담당 페르소나. 확인 노드면 보통 비어 있다. 서버는 검사하지 않는다 |
| output_spec | str | 정의서 md |
| status | PlanNodeStatus | 만들 때 todo |
| created_at, updated_at | datetime | 서버 안에만 둔다 |

- `create(plan_id, title, kind, persona_ids, output_spec)`: 상태는 todo
- `with_update(title, kind, persona_ids, output_spec, status)`: 바꾸지 않는 필드는 부르는 쪽이 지금 값으로 채운다
- `to_read() -> PlanNodeRead`

### PlanNodeRead (`plan_node/plan_node_read.py`)

PlanNode 의 필드 그대로 (node_id: int)

### PlanNodeIdentity (`plan_node/plan_node_identity.py`)

node_id: int

### 예외 (`exception/plan_node/`)

| 예외 | 코드 | 쓰는 곳 |
|---|---|---|
| PlanNodeNotFoundException | 404 | 노드 고치기 |

## plan_edge

출처: `specs/plans/model-plan-edge.md`

### PlanEdge (`plan_edge/plan_edge.py`)

| 필드 | 타입 | 설명 |
|---|---|---|
| edge_id | int \| None | 서버가 준다 |
| plan_id | int | 어느 계획의 간선인지. API 응답에는 넣지 않는다 |
| from_node_id | int | 이 노드가 끝나야 |
| to_node_id | int | 이 노드를 시작한다 |
| created_at, updated_at | datetime | 서버 안에만 둔다 |

- `create(plan_id, from_node_id, to_node_id)`
- 고치는 메서드 없음. 자기 자신을 잇는 간선과 순환은 검사하지 않는다
- `to_read() -> PlanEdgeRead`

### PlanEdgeRead (`plan_edge/plan_edge_read.py`)

PlanEdge 의 필드 그대로 (edge_id: int)

### PlanEdgeIdentity (`plan_edge/plan_edge_identity.py`)

edge_id: int

### 예외 (`exception/plan_edge/`)

| 예외 | 코드 | 사용자에게 보이는 메시지 | 쓰는 곳 |
|---|---|---|---|
| PlanEdgeNotFoundException | 404 | 해당 리소스를 찾을 수 없습니다 | 지금 API 에서는 쓰지 않음 |
| PlanEdgeEndNotInPlanException(plan_id, node_id) | 400 | 노드 {node_id} 가 계획 {plan_id} 에 없습니다 | 간선 저장 |

## plan

출처: `specs/plans/model-plan.md`

### PlanStatus (`plan/plan_status.py`)

DRAFTING = "drafting", REVIEWING = "reviewing", APPROVED = "approved", REJECTED = "rejected", RUNNING = "running", DONE = "done". 서버는 바꾸는 순서를 검사하지 않는다. "실패" 는 없다.

### Plan (`plan/plan.py`)

| 필드 | 타입 | 설명 |
|---|---|---|
| plan_id | int \| None | 서버가 준다 |
| title | str | |
| request | str | 명령서 md |
| persona_ids | tuple[int, ...] | 참여 페르소나 |
| status | PlanStatus | 만들 때 drafting |
| created_at | datetime | API 응답에 나간다 |
| updated_at | datetime | 서버 안에만 둔다 |

- `create(title, request, persona_ids)`: 상태는 drafting
- `with_status(status)`: 순서를 검사하지 않는다
- `to_read(nodes, edges) -> PlanRead`
- `to_summary(node_counts) -> PlanSummary`

### PlanRead (`plan/plan_read.py`)

Plan 의 필드 + nodes: tuple[PlanNodeRead, ...], edges: tuple[PlanEdgeRead, ...]

### PlanNodeCounts (`plan/plan_node_counts.py`)

todo, running, done, failed, skipped (int). `of(statuses)` 로 노드 상태를 세어 만든다. `total` 은 합.

### PlanSummary (`plan/plan_summary.py`)

계획 목록의 한 줄. plan_id, title, status, persona_ids, node_counts: PlanNodeCounts, created_at, updated_at

### PlanIdentity (`plan/plan_identity.py`)

plan_id: int

### 예외 (`exception/plan/`)

| 예외 | 코드 | 쓰는 곳 |
|---|---|---|
| PlanNotFoundException | 404 | 계획 조회, 상태 바꾸기, 노드·간선 저장 |

### MemoryListCondition (`memory/memory_list_condition.py`)

웹 지식 목록의 조건. query: str = "", kind: MemoryKind | None, persona_id: int | None, limit: int | None (None 이면 전부). 출처: `specs/plans/get-memories.md`
