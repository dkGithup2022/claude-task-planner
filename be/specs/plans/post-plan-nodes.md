# Plan: POST /api/plans/{plan_id}/nodes

## 요청 스펙

노드 하나 저장. 상태는 todo. 출처: `corbina/notes/2026-11-20-api.md` 5절.

요청 `{"title": "RDBMS 테이블 모델링", "kind": "document", "persona_ids": [1], "output_spec": "### 하는 일\n..."}`
응답 201 `{"node_id": 56, "status": "todo"}`

CLI 기준 코드: `to_new_node_body` 가 네 필드를 보내고, `add_node` 는 응답의 node_id 와 status 를 읽는다. CLI 포트 설명은 "계획이 없으면 PlanNotFoundError" 이므로 계획이 없으면 404 로 한다 (문서에는 오류가 적혀 있지 않다. 코드를 따른다).

## Phase 1: 평가

### assess-api

충족 여부: 미충족.
- service 신규: [Usecase] PlanNodeCreateUsecase.execute(command: PlanNodeCreateCommand) -> PlanNodeRead
- 작업 계획: POST /api/plans/{plan_id}/nodes. 요청 NodeCreateRequest(title: 빈 값 불가, kind: NodeKind, persona_ids: list[int], output_spec: str). 응답 NodeCreateResponse(node_id, status). 201. 노드 API 는 경로가 계획 아래라 plan_router 에 둔다

### assess-usecase

충족 여부: 미충족. 노드 service 가 없다.
- [신규] PlanNodeWriter.create(command) -> PlanNodeIdentity
- [신규] PlanNodeCreateCommand(plan_id, title, kind, persona_ids, output_spec)
- [신규] PlanNodeCreateUsecase.execute(command) -> PlanNodeRead: 계획이 있는지 PlanRepository.find_write_by_id 로 보고(없으면 404) → writer.create → 다시 읽어 to_read. @transactional
- 다른 도메인(계획)의 Repository 를 주입한다 (허용)
- infrastructure 신규: PlanNodeRepository.save(node) -> PlanNode, find_write_by_id(identity: PlanNodeIdentity) -> PlanNode | None

### assess-infra

충족 여부: 부분 충족. PlanNodeRepository 에 메서드를 더한다. 어댑터(DefaultPlanNodeRepository)도 같이 고친다.
- save(node: PlanNode) -> PlanNode: 신규·수정. 수정 때 담당 페르소나 목록을 통째로 바꾼다
- find_write_by_id(identity: PlanNodeIdentity) -> PlanNode | None: 지운 노드는 없음

### assess-model

충족 여부: 충족.

## Phase 2: 구현 계획

1. add-infrastructure: PlanNodeRepository 에 save, find_write_by_id
2. add-query: PlanNodeEntityQuery 에 find_by_id_and_active, get, add, flush. DefaultPlanNodeRepository 구현
3. add-usecase: PlanNodeWriter, DefaultPlanNodeWriter, PlanNodeCreateCommand, PlanNodeCreateUsecase, PlanNodeProvider 갱신
4. add-api: POST, NodeCreateRequest, NodeCreateResponse
5. 시험: 201·응답 모양, GET 에 나옴, 없는 계획 404, 틀린 kind 400

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: PlanNodeRepository 에 save, find_write_by_id
- add-query: PlanNodeEntityQuery 에 find_by_id_and_active, get, add, flush. DefaultPlanNodeRepository 구현 (수정 때 personas 통째 교체)
- add-usecase: `service/plan_node/` PlanNodeWriter, DefaultPlanNodeWriter, PlanNodeCreateCommand, PlanNodeCreateUsecase. PlanNodeProvider 에 writer, create_usecase
- add-api: plan_router 에 POST /{plan_id}/nodes, NodeCreateRequest, NodeCreateResponse
- 검증: ruff, lint-imports, mypy(137 파일) 통과
- 시험: 3개 더해 모두 14개 통과 (201·응답 모양·GET 에 그대로 나옴, 없는 계획 404, 틀린 kind 400)
