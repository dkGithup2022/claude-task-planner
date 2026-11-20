# Plan: DELETE /api/plans/{plan_id}/edges/{edge_id}

## 요청 스펙

간선 하나 지우기. 이미 없으면 아무것도 하지 않는다. 응답 204. 출처: `corbina/notes/2026-11-20-api.md` 5절. CLI `delete_edge` 는 응답을 읽지 않는다. 다른 점: 없음.

## Phase 1: 평가

### assess-api

미충족. [Usecase] PlanEdgeDeleteUsecase.execute(plan_id, edge_id) -> None. DELETE, 204.

### assess-usecase

부분 충족.
- [신규] PlanEdgeWriter.delete(identity) -> None (없으면 404, 번들 관례)
- [신규] PlanEdgeDeleteUsecase: 간선이 없거나 다른 계획의 간선이면 아무것도 하지 않는다. 있으면 writer.delete. @transactional
- infrastructure 신규: PlanEdgeRepository.find_write_by_id, delete_by_id

### assess-infra

부분 충족.
- find_write_by_id(identity: PlanEdgeIdentity) -> PlanEdge | None (지운 간선 제외)
- delete_by_id(identity: PlanEdgeIdentity) -> None (soft-delete, 이미 지웠으면 no-op)

### assess-model

충족.

## Phase 2: 구현 계획

1. add-infrastructure → 2. add-query → 3. add-usecase (PlanEdgeWriter.delete, PlanEdgeDeleteUsecase) → 4. add-api (DELETE) → 5. 시험: 지우면 GET 에서 빠짐, 다시·없는 간선 204, 다른 계획 경로로는 지워지지 않음

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: PlanEdgeRepository.find_write_by_id, delete_by_id
- add-query: PlanEdgeEntityQuery.find_by_id_and_active·get, DefaultPlanEdgeRepository 구현
- add-usecase: PlanEdgeWriter.delete, `usecase/plan_edge_delete_usecase.py`, PlanEdgeProvider 에 delete_usecase
- add-api: DELETE /{plan_id}/edges/{edge_id} (204)
- 검증: ruff, lint-imports, mypy(153 파일) 통과
- 시험: 3개 더해 모두 29개 통과

### 리뷰 (별도 에이전트, 2026-11-20) — 계획·노드·간선 8개 API
- 버그 없음. CLI 의 DefaultPlanApiWriter·Reader 를 그대로 import 해 띄운 서버에 8개 API 를 불러 계약이 맞음을 확인
- 위험 (CLI 가 요청을 차례로 보내므로 지금은 드러나지 않음, 고치지 않음)
  1. 간선 중복 검사가 SELECT 뿐이라 같은 간선 POST 가 동시에 오면 둘 다 저장될 수 있다
  2. 간선 저장과 노드 지우기가 동시에 오면 지운 노드를 가리키는 간선이 남을 수 있다
  3. GET /plans/{id} 는 계획·노드·간선을 따로 읽어 한 시점을 보장하지 않는다
  4. 자식 Entity 의 ForeignKey 선언과 migration(FK 없음)이 다르다. `alembic check` 는 env.py 필터로 통과하지만 autogenerate 는 테이블 생성문 안에 FK 를 다시 넣는다 (migration 마다 손으로 지움)
- 테스트 공백 중 두 가지를 더함: 노드 담당 비우기·kind 만 바꾸기, 노드·간선이 있는 계획의 상태 바꾸기 응답
