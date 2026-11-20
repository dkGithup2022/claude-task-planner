# Plan: POST /api/plans

## 요청 스펙

계획 만들기. 상태는 drafting, 노드와 간선은 없다. 출처: `corbina/notes/2026-11-20-api.md` 4절.

요청

```jsonc
{
  "title": "계산기 웹 서비스 개발 전 문서 6종 작성 (...)",
  "request": "# 명령\n...",
  "persona_ids": [1]
}
```

응답 (201)

```jsonc
{ "plan_id": 11, "status": "drafting", "created_at": "2026-11-20T04:16:15Z" }
```

CLI 기준 코드: `task-plan-manager/src/task_plan_manager/port/plan_api/`
- `plan_api_request_converter.py` `to_new_plan_body`: title, request, persona_ids(list) 를 보낸다
- `default_plan_api_writer.py` `create_plan`: 응답의 plan_id 만 읽고 `GET /plans/{plan_id}` 로 다시 읽는다

문서와 코드가 다른 점: 없음.

정한 것: 경로는 `/api` 로 시작한다. CLI 서버 주소는 `http://localhost:8000/api` (사용자, 2026-11-20).

## Phase 1: 평가

### assess-api

충족 여부: 미충족. API 가 하나도 없다.

하위 레이어에 필요한 기능
- service 신규: [Usecase] PlanCreateUsecase.execute(command: PlanCreateCommand) -> PlanRead
  - Command: PlanCreateCommand(title, request, persona_ids: tuple[int, ...])
  - 이 서비스에는 로그인 사용자가 없다. 그래서 번들 관례의 `request_user_id` 첫 필드와 `execute(user_id, ...)` 인자를 두지 않는다
- model: 기존 Plan, PlanRead 로 충분

현재 레이어 작업 계획
- [신규] POST /api/plans (Pattern Foo 의 생성. 인증 없음)
- Request PlanCreateRequest: title: str (min_length=1), request: str, persona_ids: list[int]
- Response PlanCreateResponse: plan_id: int, status: PlanStatus, created_at: str
  - created_at 은 문서 예시대로 초 단위 UTC 문자열 `2026-11-20T04:16:15Z`. CLI 는 이 값을 문자열 그대로 갖고 있으므로 모양을 문서에 맞춘다
- 상태 코드: 201

### assess-usecase

충족 여부: 미충족. service 가 없다.

하위 레이어에 필요한 기능
- infrastructure 신규
  - PlanRepository.save(plan: Plan) -> Plan (쓰기)
  - PlanRepository.find_write_by_id(identity: PlanIdentity) -> Plan | None (선검증, 만든 뒤 다시 읽기)
- model: 기존으로 충분

현재 레이어 작업 계획
- [신규] PlanWriter.create(command) -> PlanIdentity. Plan.create 로 만들어 저장
- [신규] PlanCreateUsecase.execute(command) -> PlanRead
  - writer.create → repository.find_write_by_id → to_read(nodes=(), edges=()). 새 계획은 노드와 간선이 없으므로 빈 튜플이 맞다
  - @transactional. 부수효과 없음
- 소유권 체크: 없음 (사용자 개념 없음)
- DI: PlanProvider 에 PlanEntityQuery, DefaultPlanRepository, DefaultPlanWriter, PlanCreateUsecase

### assess-infra

충족 여부: 미충족. PlanRepository 가 없다.

현재 레이어 작업 계획
- [신규] PlanRepository (Pattern Bar 로 시작. 이 API 에 필요한 두 메서드만)
  - save(plan: Plan) -> Plan: 저장 (신규·수정)
  - find_write_by_id(identity: PlanIdentity) -> Plan | None: Write 모델 조회
- 원자적 연산, Stats: 없음

Entity 와 테이블 (add-entity-specs 에서)
- plans: id, title(Text), request(Text), status(VARCHAR 255), 감사·soft-delete 4컬럼
- plan_personas: 계획의 참여 페르소나 자식 테이블. id, plan_id(인덱스), persona_id, position(순서). persona_ids 의 순서를 지킨다
- status 는 `Enum(PlanStatus, native_enum=False, values_callable=...)` 로 값(소문자)을 저장한다. SQLAlchemy 기본은 이름(대문자)을 저장하는데, 번들 규칙(값 = 이름)과 달리 이 서비스의 값은 소문자이기 때문이다. SQL 로 직접 읽을 때도 API 값과 같게 보인다

### assess-model

충족 여부: 충족. Plan, PlanRead, PlanIdentity, PlanStatus 가 있다 (`specs/models.md`).

## Phase 2: 구현 계획

[평가 결과]
- api: 미충족 — POST /api/plans 신규
- service: 미충족 — PlanWriter.create, PlanCreateUsecase 신규
- infra: 미충족 — PlanRepository 신규
- model: 충족

[설계 결정]
- 패턴: infra Bar / entity Baz(plan_personas 자식) / query Foo / service Bar + Baz / api Foo
- 트랜잭션: Usecase.execute 가 연다. Writer 와 Repository 는 합류한다
- 사용자 개념이 없으므로 Command 와 execute 에 user_id 를 두지 않는다
- 시험: 실제 Postgres(testcontainers)에 앱을 띄워 HTTP 로 부르는 시험을 `packages/app/tests/` 에 둔다

[구현 계획]
1. add-infrastructure: PlanRepository (save, find_write_by_id)
2. add-entity-specs: PlanEntity, PlanPersonaEntity, migration `plan`
3. add-query: PlanEntityQuery, DefaultPlanRepository
4. add-usecase: PlanWriter, DefaultPlanWriter, PlanCreateCommand, PlanCreateUsecase, PlanProvider
5. add-api: plan_router 의 POST, PlanCreateRequest, PlanCreateResponse, ROUTERS 등록
6. 시험: HTTP 시험 (만들기 성공, 빈 제목 400)

## Phase 3: 구현 진행

### add-infrastructure (2026-11-20)
- `infrastructure/plan/plan_repository.py`: PlanRepository (save, find_write_by_id)
- 검증: ruff, lint-imports, mypy 통과

### add-entity-specs (2026-11-20)
- `persistence/plan/plan_entity.py` (plans), `plan_persona_entity.py` (plan_personas), `entities.py` 에 두 줄
- migration `20261120_0edad69db71e_plan.py`
- autogenerate 가 `plan_personas` 생성문 안에 FK 제약(`sa.ForeignKeyConstraint`)을 넣었다. `env.py` 의 필터는 따로 만드는 FK 만 거르고 테이블 생성문 안의 FK 는 거르지 못한다. 손으로 지웠다. 앞으로 자식 테이블 migration 마다 같은 확인이 필요하다
- 검증: upgrade head 적용, `alembic check` "No new upgrade operations detected", DB 의 FK 제약 0개

### add-query (2026-11-20)
- `persistence/plan/plan_entity_query.py`: PlanEntityQuery (find_by_id_and_active, get, add, flush)
- `persistence/plan/plan_repository.py`: DefaultPlanRepository (save 는 참여 페르소나 목록을 통째로 바꾼다)
- JoinQuery 없음

### add-usecase (2026-11-20)
- `service/plan/plan_writer.py`, `impl/default_plan_writer.py`, `dto/plan_create_command.py`, `usecase/plan_create_usecase.py`
- `app/providers/plan_provider.py`, `di.py` 의 DOMAIN_PROVIDERS 에 PlanProvider()

### add-api (2026-11-20)
- `api/plan/plan_router.py` (POST), `dto/plan_create_request.py`, `dto/plan_create_response.py`, `api/common/time_format.py` (초 단위 UTC 문자열)
- `routers.py` 의 ROUTERS 에 plan_router
- 검증: ruff, lint-imports, mypy(103 파일), openapi 에 `/api/plans`

### 시험 (2026-11-20)
- 루트 `conftest.py` 에 `client` 픽스처: testcontainers Postgres 에 붙은 앱을 TestClient 로 부른다. 끝나면 테이블을 비운다
- `packages/app/tests/test_plan_api.py`: 4개 통과 (201 과 응답 모양, id 증가, 빈 제목 400, persona_ids 없음 400)
