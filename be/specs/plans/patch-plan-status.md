# Plan: PATCH /api/plans/{plan_id}/status

## 요청 스펙

계획 상태 바꾸기. 요청 `{"status": "approved"}`. 응답은 바뀐 계획 (GET /api/plans/{plan_id} 와 같은 모양). 없으면 404. 출처: `corbina/notes/2026-11-20-api.md` 4절.

CLI 기준 코드: `default_plan_api_writer.py` `set_plan_status` 가 `{"status": 값}` 을 보내고 응답은 읽지 않은 채 계획을 다시 읽는다. 문서와 코드가 다른 점: 없음.

정한 것 (사용자, 2026-11-20): 서버는 상태를 바꾸는 순서를 검사하지 않는다. 흐름을 LLM 이 돌리므로 사용자가 대화로 상태를 되돌려 고칠 수 있어야 한다. 값이 PlanStatus 여섯 가지 중 하나인지만 본다 (Pydantic, 틀리면 400).

## Phase 1: 평가

### assess-api

충족 여부: 미충족.
- service 신규: [Usecase] PlanStatusChangeUsecase.execute(command: PlanStatusChangeCommand) -> PlanRead
- 작업 계획: PATCH /api/plans/{plan_id}/status, 요청 PlanStatusChangeRequest(status: PlanStatus), 응답 PlanResponse (기존), 200

### assess-usecase

충족 여부: 부분 충족. PlanWriter, PlanReader 가 있다.
- [신규] PlanWriter.change_status(command) -> Plan: find_write_by_id 선검증(없으면 404) → with_status → save
- [신규] PlanStatusChangeCommand(plan_id: int, status: PlanStatus)
- [신규] PlanStatusChangeUsecase.execute(command) -> PlanRead: writer.change_status → reader.get_by_id. @transactional 이라 바꾸기와 다시 읽기가 한 트랜잭션이다 (같은 도메인 Reader 호출)
- infrastructure: 기존 save, find_write_by_id 로 충분

### assess-infra

충족 여부: 충족.

### assess-model

충족 여부: 충족. Plan.with_status 가 있다.

## Phase 2: 구현 계획

1. add-usecase: PlanWriter.change_status, PlanStatusChangeCommand, PlanStatusChangeUsecase, Provider 갱신
2. add-api: PATCH, PlanStatusChangeRequest
3. 시험: 바꾼 상태가 응답과 다시 읽기에 나옴, 끝난 계획을 검토 중으로 되돌리기도 됨, 없는 계획 404, 틀린 값 400

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-usecase: PlanWriter.change_status (DefaultPlanWriter), `dto/plan_status_change_command.py`, `usecase/plan_status_change_usecase.py`, PlanProvider 에 status_change_usecase
- add-api: PATCH /api/plans/{plan_id}/status, `dto/plan_status_change_request.py`
- 검증: ruff, lint-imports, mypy(127 파일) 통과
- 시험: 4개 더해 모두 11개 통과 (바꾼 상태가 응답·다시 읽기에 나옴, 끝남 → 검토 중 되돌리기 허용, 없는 계획 404, 계획 상태가 아닌 값 "failed" 400)
