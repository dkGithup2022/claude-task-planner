# Plan: model PlanNode

## 요청 스펙

사용자 지시 (2026-11-20): be 는 model 을 하나씩 먼저 만들고, 그다음 API 를 하나씩 만든다. 각각 만들기 전에 be-planner 를 실행한다. 모델은 끝까지 진행한다 ("모델을 끝까지 진행 해주세요").

이번 범위는 model 레이어의 계획 노드 하나다. api·usecase·infra 평가는 건너뛴다.

노드 데이터 (출처: `corbina/notes/2026-11-20-current-data.md` 1절)

```jsonc
{
  "node_id": 54,                       // 서버가 준다
  "title": "상위 기획 작성",
  "kind": "document",                  // document | research | code | hitl(사용자 확인)
  "persona_ids": [1],                  // hitl 이면 빈 배열
  "output_spec": "### 하는 일\n...\n\n### 산출물\n...\n\n### 그 외 설명\n...",   // 정의서 md
  "status": "done"                     // todo | running | done | failed | skipped
}
```

이 모델을 쓰는 API (출처: `2026-11-20-api.md` 5절)
- `POST /plans/{plan_id}/nodes`: 노드 하나 저장. 상태는 todo. 응답은 node_id, status
- `PATCH /plans/{plan_id}/nodes/{node_id}`: 바꿀 필드만. 고치기는 title, kind, persona_ids, output_spec, 실행은 status. 없으면 404
- `DELETE /plans/{plan_id}/nodes/{node_id}`: 닿은 간선도 지운다. 이미 없으면 아무것도 하지 않는다
- `GET /plans/{plan_id}`: 계획의 노드가 모두 나온다

## Phase 1: 평가

### assess-api

건너뜀. 이번 범위는 model 만이다.

### assess-usecase

건너뜀. 이번 범위는 model 만이다.

### assess-infra

건너뜀. 이번 범위는 model 만이다.

### assess-model

충족 여부: 미충족. 노드 도메인이 없다.

작업 계획

- 패턴: Bar. 조회 모델은 저장 모델을 그대로 옮긴다. 계획 조회가 노드 목록을 담을 때 id 가 None 이 아닌 조회 모델을 쓴다

- [신규] NodeKind (`model/plan_node/node_kind.py`)
  - 값: DOCUMENT = "document", RESEARCH = "research", CODE = "code", HITL = "hitl"
  - 소문자 값은 CLI 와 맞춘다 (번들 규칙의 대문자 대신)

- [신규] PlanNodeStatus (`model/plan_node/plan_node_status.py`)
  - 값: TODO = "todo", RUNNING = "running", DONE = "done", FAILED = "failed", SKIPPED = "skipped"
  - 서버는 상태를 어떤 순서로 바꾸는지 검사하지 않는다. 계획 상태와 같은 이유다: 흐름을 LLM 이 돌리므로 사용자가 대화로 상태를 되돌려 고칠 수 있어야 한다

- [신규] PlanNode (`model/plan_node/plan_node.py`)
  - 필드: node_id: int | None, plan_id: int, title: str, kind: NodeKind, persona_ids: tuple[int, ...], output_spec: str, status: PlanNodeStatus, created_at, updated_at
  - plan_id: 어느 계획의 노드인지. API 응답에는 넣지 않는다 (CLI 노드 모양 그대로)
  - 팩토리: create(plan_id, title, kind, persona_ids, output_spec). 상태는 todo
  - 상태 변경: with_update(title, kind, persona_ids, output_spec, status). 바꾸지 않는 필드는 service 가 지금 값으로 채운다
  - 검사하지 않는 것: 확인 노드가 아닌데 담당 페르소나가 없는 경우. CLI 가 확정·실행 전에 `Plan.problems` 로 본다. 서버는 받은 그대로 저장한다
  - to_read() -> PlanNodeRead

- [신규] PlanNodeRead (`model/plan_node/plan_node_read.py`)
  - 필드: node_id: int, plan_id, title, kind, persona_ids, output_spec, status, created_at, updated_at

- [신규] PlanNodeIdentity (`model/plan_node/plan_node_identity.py`)
  - 필드: node_id: int

- [신규] PlanNodeNotFoundException (`exception/plan_node/plan_node_not_found_exception.py`)
  - 기본 메시지 (404). 노드 고치기가 쓴다. 다른 계획의 노드 id 를 보내도 없음으로 본다

## Phase 2: 구현 계획

사용자가 모델을 끝까지 진행하라고 함 (2026-11-20). 계획을 따로 묻지 않고 진행한다.

[구현 계획]
1. add-model: NodeKind, PlanNodeStatus, PlanNode, PlanNodeRead, PlanNodeIdentity, PlanNodeNotFoundException

## Phase 3: 구현 진행

### add-model (2026-11-20)

만든 파일
- `packages/model/src/task_plan_server/model/plan_node/`: `__init__.py`, `plan_node.py`, `plan_node_read.py`, `plan_node_identity.py`, `node_kind.py`, `plan_node_status.py`
- `packages/exception/src/task_plan_server/exception/plan_node/`: `__init__.py`, `plan_node_not_found_exception.py`
- `specs/models.md` 에 plan_node 절을 더함

검증
- ruff, mypy(64 파일), lint-imports(계약 2개): 통과
- 직접 실행: create 한 노드의 상태가 todo, with_update 로 done 으로 바꾼 뒤 to_read 의 상태가 done
