# Plan: PATCH /api/plans/{plan_id}/nodes/{node_id}

## 요청 스펙

노드 하나 고치기. 바꿀 필드만 보낸다. 고치기는 title, kind, persona_ids, output_spec 을, 실행은 status 만 보낸다. 응답 `{"node_id": 47, "status": "done"}`. 노드가 없으면 404. 출처: `corbina/notes/2026-11-20-api.md` 5절.

CLI 기준 코드: `to_node_change_body` 가 값이 None 인 필드를 빼고 보낸다. `update_node` 는 응답을 읽지 않고 계획을 다시 읽는다. 문서와 코드가 다른 점: 없음.

## Phase 1: 평가

### assess-api

충족 여부: 미충족.
- service 신규: [Usecase] PlanNodeUpdateUsecase.execute(command: PlanNodeUpdateCommand) -> PlanNodeRead
- 작업 계획: 요청 NodeUpdateRequest — 다섯 필드 모두 생략 가능 (`| None = None`). 빠지거나 null 이면 바꾸지 않는다. title 은 보낼 때 빈 값 불가. 응답 NodeCreateResponse 모양을 그대로 쓴다 (node_id, status). 200

### assess-usecase

충족 여부: 부분 충족.
- [신규] PlanNodeWriter.update(command) -> PlanNode: find_write_by_id 선검증. 노드가 없거나 다른 계획의 노드면 PlanNodeNotFoundException(404). 빠진 필드는 지금 값으로 채워 with_update → save
- [신규] PlanNodeUpdateCommand(plan_id, node_id, title, kind, persona_ids, output_spec, status — 모두 None 이면 바꾸지 않음)
- [신규] PlanNodeUpdateUsecase.execute(command) -> PlanNodeRead. @transactional
- 상태 순서는 검사하지 않는다 (계획 상태와 같은 이유)
- infrastructure: 기존 save, find_write_by_id 로 충분

### assess-infra

충족 여부: 충족.

### assess-model

충족 여부: 충족. PlanNode.with_update 가 있다.

## Phase 2: 구현 계획

1. add-usecase: PlanNodeWriter.update, PlanNodeUpdateCommand, PlanNodeUpdateUsecase, Provider 갱신
2. add-api: PATCH, NodeUpdateRequest
3. 시험: 고치기 필드만 바꾸면 나머지 그대로, status 만 바꾸기, 다른 계획의 노드 404, 없는 노드 404, 빈 제목 400

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-usecase: PlanNodeWriter.update (빠진 필드는 지금 값으로), `dto/plan_node_update_command.py`, `usecase/plan_node_update_usecase.py`, PlanNodeProvider 에 update_usecase
- add-api: PATCH /{plan_id}/nodes/{node_id}, `dto/node_update_request.py`. 응답은 NodeCreateResponse 모양 (node_id, status)
- 검증: ruff, lint-imports, mypy(140 파일) 통과
- 시험: 4개 더해 모두 18개 통과 (보낸 필드만 바뀜·페르소나 순서, status 만 바꾸고 되돌리기, 다른 계획의 노드·없는 노드 404, 빈 제목 400)
