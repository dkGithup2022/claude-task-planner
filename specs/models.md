# model

## plan

계획, 노드, 간선. 원본은 계획 저장소(`port/plan_api/`)다.

### Plan (`model/plan/plan.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| plan_id | int | 계획 저장소가 준다 |
| title | str | |
| request | str | 명령서 본문 (md) |
| persona_ids | tuple[int, ...] | 참여 페르소나 id |
| status | PlanStatus | |
| created_at | str | ISO 8601 |
| nodes | tuple[PlanNode, ...] | |
| edges | tuple[PlanEdge, ...] | |

동작: `node(node_id) -> PlanNode` (없으면 KeyError), `prerequisites(node_id) -> tuple[int, ...]` (간선으로 바로 이어진 앞 노드 id)

실행 순서 계산 (`model/plan/plan_schedule.py`, 순수 함수, 노드 상태와 간선만 봄. 끝남 = done·skipped):
- `runnable_nodes(plan, limit) -> tuple[PlanNode, ...]`: todo, 확인 노드 아님, 선행 노드가 모두 끝남. node_id 순 limit 개
- `waiting_confirm_nodes(plan) -> tuple[PlanNode, ...]`: 확인 노드, todo, 선행 노드가 모두 끝남
- `nodes_to_skip(plan, node_id) -> tuple[int, ...]`: 그 노드와, 들어오는 간선이 모두 건너뛴 노드에서 오는 뒤 노드 (완료·실행 중 제외)
- `plan_progress(plan) -> PlanProgress`

### PlanProgress (`model/plan/plan_progress.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| counts | dict[PlanNodeStatus, int] | 상태마다 노드 수 |
| finished | bool | 모든 노드가 완료·건너뜀 |
| blocked | bool | 안 끝났는데 실행할 노드, 확인 노드, 실행 중, 실패한 노드가 모두 없음 |

### PlanNode (`model/plan/plan_node.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| node_id | int | 계획 저장소가 준다 |
| title | str | |
| kind | NodeKind | |
| persona_ids | tuple[int, ...] | 확인 노드면 빈 튜플 |
| output_spec | str | md. `### 하는 일`, `### 산출물`, `### 그 외 설명` |
| status | PlanNodeStatus | |

선행 노드는 필드로 두지 않는다. `Plan.prerequisites` 로 간선에서 계산한다.

### NodeSpec (`model/plan/node_spec.py`)
노드의 정의서(`PlanNode.output_spec` md)를 절로 읽고 쓴다. 저장은 지금처럼 md 하나다.
| 필드 | 타입 | 뜻 |
|---|---|---|
| does | str | 하는 일 |
| output_form | str | 산출물 형태. 없으면 "" |
| output_contents | str | 산출물에 담을 것. 없으면 "" |
| notes | str | 그 외 설명. 없으면 "" |
| extra_md | str | 세 절 밖의 절. md 로 되돌릴 때 뒤에 붙인다 |

- `NodeSpec.from_md(md)`: `### 이름` 머리로 절을 나눈다. 산출물 첫 줄 `- 형태: ` 를 형태로 본다
- `to_md()`: make_plan 과 같은 모양. 형태가 없으면 "(정하지 않음)", 설명이 없으면 "(없음)"

### PlanEdge (`model/plan/plan_edge.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| edge_id | int | |
| from_node_id | int | 이 노드가 끝나야 |
| to_node_id | int | 이 노드를 시작한다 |

### PlanStatus (`model/plan/plan_status.py`)
DRAFTING = "drafting", REVIEWING = "reviewing", APPROVED = "approved", REJECTED = "rejected", RUNNING = "running", DONE = "done"

동작: `can_move_to(to) -> bool`. 허용: drafting → reviewing, reviewing → approved 또는 rejected, approved → running, running → done. 흐름 도식 B 절의 가안이다.

### PlanNodeStatus (`model/plan/plan_node_status.py`)
TODO = "todo", RUNNING = "running", DONE = "done", FAILED = "failed", SKIPPED = "skipped"

번들 engine 의 `NodeStatus` 와 다른 것이다.

### NodeKind (`model/plan/node_kind.py`)
DOCUMENT = "document", RESEARCH = "research", CODE = "code", HITL = "hitl"

## node_run

노드 하나의 로컬 실행 기록. 계획 폴더의 `nodes/<node_id>/run.json` 에 저장한다 (`port/local/plan_folder/`).

### NodeRun (`model/node_run/node_run.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| round | int | 몇 번째 실행인지 |
| status | PlanNodeStatus | 원본은 계획 저장소 |
| started_at | str \| None | |
| finished_at | str \| None | |
| read_inputs | tuple[ReadInput, ...] | 이 회차에 읽은 선행 노드와 그 회차 |
| confirm | str \| None | 확인 노드면 사용자가 한 말 |
| skipped_reason | str \| None | 건너뛴 이유 |

동작: `start(now, read_inputs) -> NodeRun`, `finish(status, now) -> NodeRun`, `back_to_todo() -> NodeRun` (끊긴 노드를 다시 실행할 때. 회차 그대로)

### ReadInput (`model/node_run/read_input.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| node_id | int | 선행 노드 |
| round | int | 읽은 결과의 회차 |

## persona

### Persona (`model/persona/persona.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| persona_id | int | 계획 저장소(서버)가 준다 |
| name | str | 예: dankim-persona |
| description | str | |

## memory

지식. 작업 이름(theme) 아래 md 본문(body).

### Memory (`model/memory/memory.py`)
| 필드 | 타입 | 뜻 |
|---|---|---|
| memory_id | int | |
| kind | MemoryKind | |
| theme | str | 작업 이름 |
| body | str | md. 덧붙일 때마다 `****** KNOWLEDGE APPENDED <n> ********` 머리를 달고 뒤에 붙는다 |
| persona_ids | tuple[int, ...] | |
| sources | tuple[MemorySource, ...] | 근거 |

동작: `append(body, sources) -> Memory`

### MemorySource (`model/memory/memory_source.py`)
quote: str, plan_id: int

### MemoryKind (`model/memory/memory_kind.py`)
KNOWLEDGE = "knowledge", ATTITUDE = "attitude", PLAN = "plan"
