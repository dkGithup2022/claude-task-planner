# Plan: model Plan

## 요청 스펙

사용자 지시 (2026-11-20): model 을 하나씩 먼저 만들고 끝까지 진행한다. 각각 만들기 전에 be-planner 를 실행한다.

이번 범위는 model 레이어의 계획 하나다. api·usecase·infra 평가는 건너뛴다. 노드와 간선 모델은 먼저 만들었다 (`model-plan-node.md`, `model-plan-edge.md`).

계획 데이터 (출처: `corbina/notes/2026-11-20-current-data.md` 1절)

```jsonc
{
  "plan_id": 11,                       // 서버가 준다
  "title": "계산기 웹 서비스 개발 전 문서 6종 작성 (...)",
  "request": "# 명령\n...",            // 명령서 md
  "persona_ids": [1],                  // 참여 페르소나
  "status": "done",                    // drafting | reviewing | approved | rejected | running | done
  "created_at": "2026-11-20T04:16:15Z"
}
```

이 모델을 쓰는 API
- `POST /plans` (`2026-11-20-api.md` 4절): 상태는 drafting, 노드와 간선은 없다. 응답은 plan_id, status, created_at
- `GET /plans/{plan_id}`: 계획과 노드, 간선 전부. 없으면 404
- `PATCH /plans/{plan_id}/status`: 상태 바꾸기. 응답은 바뀐 계획 (조회와 같은 모양)
- `GET /plans` (`2026-11-20-ui.md` 6절, 웹): 모든 계획을 만든 시각 최근 것부터. 계획마다 상태별 노드 수 ("6/9 (실패 1)")

정한 것 (사용자, 2026-11-20)
- 서버는 계획 상태를 바꾸는 순서를 검사하지 않는다. 흐름을 LLM 이 돌리므로 사용자가 대화로 상태를 되돌려 고칠 수 있어야 한다
- 계획 상태에 "실패" 는 없다. 실패한 노드가 있어도 계획은 "실행 중" 이다

## Phase 1: 평가

### assess-api

건너뜀. 이번 범위는 model 만이다.

### assess-usecase

건너뜀. 이번 범위는 model 만이다.

### assess-infra

건너뜀. 이번 범위는 model 만이다.

### assess-model

충족 여부: 미충족. 계획 도메인이 없다.

작업 계획

- 패턴: Baz. 조회 모델이 노드와 간선 목록을 담고, 목록 화면용 요약이 상태별 노드 수를 담는다. 둘 다 to_read 의 인자로 받는다. 노드 수는 노드를 세어서 얻으므로 따로 저장하지 않는다

- [신규] PlanStatus (`model/plan/plan_status.py`)
  - 값: DRAFTING = "drafting", REVIEWING = "reviewing", APPROVED = "approved", REJECTED = "rejected", RUNNING = "running", DONE = "done"
  - 소문자 값은 CLI 와 맞춘다. CLI 의 `can_move_to` 는 옮기지 않는다 (서버는 검사하지 않음)

- [신규] Plan (`model/plan/plan.py`)
  - 필드: plan_id: int | None, title: str, request: str, persona_ids: tuple[int, ...], status: PlanStatus, created_at, updated_at
  - created_at 은 API 응답에 나간다 (CLI 가 읽는다). updated_at 은 서버 안에만 둔다
  - 팩토리: create(title, request, persona_ids). 상태는 drafting
  - 상태 변경: with_status(status). 순서를 검사하지 않는다
  - to_read(nodes: tuple[PlanNodeRead, ...], edges: tuple[PlanEdgeRead, ...]) -> PlanRead
  - to_summary(node_counts: PlanNodeCounts) -> PlanSummary

- [신규] PlanRead (`model/plan/plan_read.py`)
  - 필드: plan_id: int, title, request, persona_ids, status, nodes: tuple[PlanNodeRead, ...], edges: tuple[PlanEdgeRead, ...], created_at, updated_at

- [신규] PlanNodeCounts (`model/plan/plan_node_counts.py`)
  - 필드: todo, running, done, failed, skipped (모두 int)
  - 팩토리: of(statuses: Iterable[PlanNodeStatus]) — 노드 상태들을 세어 만든다
  - total 속성: 노드 수 합

- [신규] PlanSummary (`model/plan/plan_summary.py`)
  - 계획 목록의 한 줄. 노드와 간선은 담지 않는다
  - 필드: plan_id: int, title, status, persona_ids, node_counts: PlanNodeCounts, created_at, updated_at

- [신규] PlanIdentity (`model/plan/plan_identity.py`)
  - 필드: plan_id: int

- [신규] PlanNotFoundException (`exception/plan/plan_not_found_exception.py`)
  - 기본 메시지 (404). CLI 는 404 를 PlanNotFoundError 로 바꿔 읽는다

## Phase 2: 구현 계획

사용자가 모델을 끝까지 진행하라고 함 (2026-11-20). 계획을 따로 묻지 않고 진행한다.

[구현 계획]
1. add-model: PlanStatus, Plan, PlanRead, PlanNodeCounts, PlanSummary, PlanIdentity, PlanNotFoundException

## Phase 3: 구현 진행

### add-model (2026-11-20)

만든 파일
- `packages/model/src/task_plan_server/model/plan/`: `__init__.py`, `plan.py`, `plan_read.py`, `plan_summary.py`, `plan_node_counts.py`, `plan_identity.py`, `plan_status.py`
- `packages/exception/src/task_plan_server/exception/plan/`: `__init__.py`, `plan_not_found_exception.py`
- `specs/models.md` 에 plan 절을 더함

검증
- ruff, mypy(80 파일), lint-imports(계약 2개): 통과
- 직접 실행: create 한 계획이 drafting. 끝남 → 검토 중으로 되돌리는 상태 바꿈도 막지 않음. 완료 6, 실패 1, 할 일 2 를 세면 total 9. to_summary, to_read 가 저장된 id 로 동작
