# Plan: DELETE /api/plans/{plan_id}/nodes/{node_id}

## 요청 스펙

노드 하나 지우기. 그 노드에 닿은 간선도 함께 지운다. 이미 없으면 아무것도 하지 않는다. 응답 204. 출처: `corbina/notes/2026-11-20-api.md` 5절.

CLI 기준 코드: `delete_node` 는 응답을 읽지 않는다. 포트 설명 "노드와 그 노드에 닿은 간선을 지운다. 이미 없으면 아무것도 하지 않는다". 문서와 코드가 다른 점: 없음.

## Phase 1: 평가

### assess-api

충족 여부: 미충족.
- service 신규: [Usecase] PlanNodeDeleteUsecase.execute(plan_id: int, node_id: int) -> None
- 작업 계획: DELETE, 204, 본문 없음

### assess-usecase

충족 여부: 부분 충족.
- [신규] PlanNodeWriter.delete(identity: PlanNodeIdentity) -> None. 번들 관례대로 없으면 404 를 던진다
- [신규] PlanNodeDeleteUsecase.execute(plan_id, node_id): 노드가 없거나 다른 계획의 노드면 아무것도 하지 않는다(204). 있으면 writer.delete → 닿은 간선을 PlanEdgeRepository.delete_by_node_id 로 지운다. @transactional 이라 노드와 간선이 함께 지워지거나 함께 남는다
- 다른 계획의 노드 id 를 보내면 지우지 않는다. 노드 고치기와 같은 기준이다
- infrastructure 신규: PlanNodeRepository.delete_by_id, PlanEdgeRepository.delete_by_node_id

### assess-infra

충족 여부: 부분 충족. 두 Repository 에 메서드를 더하고 어댑터도 고친다.
- PlanNodeRepository.delete_by_id(identity: PlanNodeIdentity) -> None: soft-delete. 이미 지웠으면 no-op
- PlanEdgeRepository.delete_by_node_id(node_identity: PlanNodeIdentity) -> None: 앞이나 뒤가 이 노드인 간선을 모두 soft-delete. 없으면 no-op

### assess-model

충족 여부: 충족.

## Phase 2: 구현 계획

1. add-infrastructure: 두 메서드
2. add-query: PlanNodeRepository.delete_by_id, PlanEdgeEntityQuery.find_by_node_id_and_active, DefaultPlanEdgeRepository.delete_by_node_id
3. add-usecase: PlanNodeWriter.delete, PlanNodeDeleteUsecase, Provider 갱신
4. add-api: DELETE
5. 시험: 노드와 닿은 간선이 사라지고 닿지 않은 간선은 남음, 다시 지워도 204, 다른 계획의 노드는 남음

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: PlanNodeRepository.delete_by_id, PlanEdgeRepository.delete_by_node_id
- add-query: DefaultPlanNodeRepository.delete_by_id, PlanEdgeEntityQuery.find_by_node_id_and_active·flush, DefaultPlanEdgeRepository.delete_by_node_id
- add-usecase: PlanNodeWriter.delete, `usecase/plan_node_delete_usecase.py`, PlanNodeProvider 에 delete_usecase
- add-api: DELETE /{plan_id}/nodes/{node_id} (204)
- 검증: ruff, lint-imports, mypy(141 파일) 통과
- 시험: 3개 더해 모두 21개 통과 (노드와 닿은 간선 두 개가 사라지고 닿지 않은 간선은 남음, 다시 지우기·없는 노드 204, 다른 계획 경로로 지우면 남음)
