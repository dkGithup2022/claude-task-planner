# Plan: POST /api/plans/{plan_id}/edges

## 요청 스펙

간선 하나 저장. 같은 간선이 이미 있으면 그 간선을 돌려준다. 양 끝 노드가 계획에 없으면 400. 출처: `corbina/notes/2026-11-20-api.md` 5절.

요청 `{"from_node_id": 49, "to_node_id": 56}`, 응답 `{"edge_id": 108}`

CLI 기준 코드: `add_edge` 가 두 필드를 보내고 응답의 edge_id 만 읽는다. 상태 코드는 보지 않는다 (2xx 이면 된다). 문서와 코드가 다른 점: 없음.

## Phase 1: 평가

### assess-api

충족 여부: 미충족.
- service 신규: [Usecase] PlanEdgeCreateUsecase.execute(command) -> PlanEdgeCreated (간선과 새로 만들었는지)
- 작업 계획: 요청 EdgeCreateRequest(from_node_id: int, to_node_id: int), 응답 EdgeCreateResponse(edge_id). 새로 만들면 201, 같은 간선이 이미 있으면 200 (문서에 코드가 없어 만들기와 돌려주기를 나눴다)

### assess-usecase

충족 여부: 미충족. 간선 service 가 없다.
- [신규] PlanEdgeWriter.create(command) -> PlanEdgeIdentity
- [신규] PlanEdgeCreateCommand(plan_id, from_node_id, to_node_id)
- [신규] PlanEdgeCreateUsecase.execute(command) -> PlanEdgeCreated
  1. 계획이 없으면 PlanNotFoundException (404)
  2. 앞·뒤 노드가 없거나 다른 계획의 노드면 PlanEdgeEndNotInPlanException (400)
  3. 같은 계획에 같은 앞·뒤의 간선이 있으면 그것을 돌려준다 (created=False)
  4. 없으면 writer.create (created=True)
  - 자기 자신을 잇는 간선과 순환은 막지 않는다 (CLI 가 확정 전에 본다)
  - @transactional
- [신규] PlanEdgeCreated (service dto): edge: PlanEdgeRead, created: bool
- infrastructure 신규: PlanEdgeRepository.save, find_by_ends. 기존 PlanRepository.find_write_by_id, PlanNodeRepository.find_write_by_id 사용

### assess-infra

충족 여부: 부분 충족.
- PlanEdgeRepository.save(edge: PlanEdge) -> PlanEdge (쓰기. 간선은 고치지 않으므로 신규만)
- PlanEdgeRepository.find_by_ends(plan_identity, from_node_id: int, to_node_id: int) -> PlanEdge | None (지운 간선 제외)

### assess-model

충족 여부: 충족.

## Phase 2: 구현 계획

1. add-infrastructure: save, find_by_ends
2. add-query: PlanEdgeEntityQuery.find_by_ends_and_active·add, DefaultPlanEdgeRepository
3. add-usecase: PlanEdgeWriter, DefaultPlanEdgeWriter, PlanEdgeCreateCommand, PlanEdgeCreated, PlanEdgeCreateUsecase, PlanEdgeProvider 갱신
4. add-api: POST, EdgeCreateRequest, EdgeCreateResponse
5. 시험: 201 과 GET 에 나옴, 같은 간선은 200 과 같은 id, 다른 계획의 노드 400, 없는 노드 400, 없는 계획 404, 지운 간선은 다시 만들면 새 id

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: PlanEdgeRepository.save, find_by_ends
- add-query: PlanEdgeEntityQuery.find_by_ends_and_active·add, DefaultPlanEdgeRepository (save 는 신규만)
- add-usecase: `service/plan_edge/` PlanEdgeWriter, DefaultPlanEdgeWriter, PlanEdgeCreateCommand, PlanEdgeCreated, PlanEdgeCreateUsecase. PlanEdgeProvider 에 writer, create_usecase
- add-api: POST /{plan_id}/edges (새로 만들면 201, 같은 간선이면 200), EdgeCreateRequest, EdgeCreateResponse
- 검증: ruff, lint-imports, mypy(152 파일) 통과
- 시험: 5개 더해 모두 26개 통과 (201·GET 에 나옴, 같은 간선 200·같은 id, 다른 계획의 노드·없는 노드 400, 없는 계획 404, 지운 노드로 잇기 400)
