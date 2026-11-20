# Plan: model PlanEdge

## 요청 스펙

사용자 지시 (2026-11-20): model 을 하나씩 먼저 만들고 끝까지 진행한다. 각각 만들기 전에 be-planner 를 실행한다.

이번 범위는 model 레이어의 계획 간선 하나다. api·usecase·infra 평가는 건너뛴다.

간선 데이터 (출처: `corbina/notes/2026-11-20-current-data.md` 1절)

```jsonc
{
  "edge_id": 102,                      // 서버가 준다
  "from_node_id": 54,                  // 이 노드가 끝나야
  "to_node_id": 55                     // 이 노드를 시작한다
}
```

이 모델을 쓰는 API (출처: `2026-11-20-api.md` 5절)
- `POST /plans/{plan_id}/edges`: 간선 하나 저장. 같은 간선이 있으면 그 간선을 돌려준다. 양 끝 노드가 계획에 없으면 400. 응답은 edge_id
- `DELETE /plans/{plan_id}/edges/{edge_id}`: 이미 없으면 아무것도 하지 않는다
- `DELETE /plans/{plan_id}/nodes/{node_id}`: 노드에 닿은 간선도 지운다
- `GET /plans/{plan_id}`: 계획의 간선이 모두 나온다

## Phase 1: 평가

### assess-api

건너뜀. 이번 범위는 model 만이다.

### assess-usecase

건너뜀. 이번 범위는 model 만이다.

### assess-infra

건너뜀. 이번 범위는 model 만이다.

### assess-model

충족 여부: 미충족. 간선 도메인이 없다.

작업 계획

- 패턴: Bar. 간선은 만들고 지우기만 하고 고치지 않는다. 계획 조회가 간선 목록을 담을 때 id 가 None 이 아닌 조회 모델을 쓴다

- [신규] PlanEdge (`model/plan_edge/plan_edge.py`)
  - 필드: edge_id: int | None, plan_id: int, from_node_id: int, to_node_id: int, created_at, updated_at
  - plan_id: 어느 계획의 간선인지. API 응답에는 넣지 않는다
  - 팩토리: create(plan_id, from_node_id, to_node_id)
  - 상태 변경: 없음 (고치기 API 가 없다)
  - 검사하지 않는 것: 자기 자신을 잇는 간선, 순환. CLI 가 확정·실행 전에 `Plan.problems` 로 본다. 서버는 양 끝 노드가 그 계획에 있는지만 본다 (service 에서)
  - to_read() -> PlanEdgeRead

- [신규] PlanEdgeRead (`model/plan_edge/plan_edge_read.py`)
  - 필드: edge_id: int, plan_id, from_node_id, to_node_id, created_at, updated_at

- [신규] PlanEdgeIdentity (`model/plan_edge/plan_edge_identity.py`)
  - 필드: edge_id: int

- [신규] PlanEdgeNotFoundException (`exception/plan_edge/plan_edge_not_found_exception.py`)
  - 기본 메시지 (404). 번들 규칙상 도메인마다 둔다. 간선 지우기는 없어도 아무것도 하지 않으므로 지금 API 에서는 쓰지 않는다

- [신규] PlanEdgeEndNotInPlanException (`exception/plan_edge/plan_edge_end_not_in_plan_exception.py`)
  - InvalidInputException 을 상속한다 (400)
  - 계획에 없는 노드 id 를 받아 메시지를 만든다: "노드 99 가 계획 11 에 없습니다"
  - 간선 저장 API 가 쓴다

## Phase 2: 구현 계획

사용자가 모델을 끝까지 진행하라고 함 (2026-11-20). 계획을 따로 묻지 않고 진행한다.

[구현 계획]
1. add-model: PlanEdge, PlanEdgeRead, PlanEdgeIdentity, PlanEdgeNotFoundException, PlanEdgeEndNotInPlanException

## Phase 3: 구현 진행

### add-model (2026-11-20)

만든 파일
- `packages/model/src/task_plan_server/model/plan_edge/`: `__init__.py`, `plan_edge.py`, `plan_edge_read.py`, `plan_edge_identity.py`
- `packages/exception/src/task_plan_server/exception/plan_edge/`: `__init__.py`, `plan_edge_not_found_exception.py`, `plan_edge_end_not_in_plan_exception.py`
- `specs/models.md` 에 plan_edge 절을 더함

검증
- ruff, mypy(71 파일), lint-imports(계약 2개): 통과
- 직접 실행: create → to_read 가 edge_id 102 를 돌려줌. PlanEdgeEndNotInPlanException(11, 99) 은 400 과 "노드 99 가 계획 11 에 없습니다"
