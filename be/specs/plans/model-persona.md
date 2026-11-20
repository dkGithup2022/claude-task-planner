# Plan: model Persona

## 요청 스펙

사용자 지시 (2026-11-20): be 는 model 을 하나씩 먼저 만들고, 그다음 API 를 하나씩 만든다. 각각 만들기 전에 be-planner 를 실행한다.

이번 범위는 model 레이어의 페르소나 하나다. API, service, infrastructure, Entity 는 이번에 만들지 않는다. 그래서 Phase 1 의 api·usecase·infra 평가는 건너뛰고 model 평가만 한다.

페르소나 데이터 (출처: `corbina/notes/2026-11-20-current-data.md` 1절)

```jsonc
{
  "persona_id": 1,                     // 서버가 준다
  "name": "dankim-persona",
  "description": "사용자의 기본 작업 역할"
}
```

나중에 붙는 기능 (출처: `corbina/notes/2026-11-20-ui.md` 4절)
- `GET /personas`: CLI 용 목록. 웹 때문에 페르소나마다 지식 수와 계획 수를 더한다
- `POST /personas`: 이름, 설명으로 만든다
- `PATCH /personas/{persona_id}`: 이름, 설명을 고친다
- `DELETE /personas/{persona_id}`: 그 페르소나를 쓰는 지식이나 계획이 있으면 409 로 거절하고 그 수를 알린다

## Phase 1: 평가

### assess-api

건너뜀. 이번 범위는 model 만이다.

### assess-usecase

건너뜀. 이번 범위는 model 만이다.

### assess-infra

건너뜀. 이번 범위는 model 만이다.

### assess-model

충족 여부: 미충족. model 패키지가 비어 있고 `specs/models.md` 도 없다.

작업 계획

- 패턴: Bar 를 바탕으로 하고, 조회 모델에 지식 수와 계획 수를 더한다. 이 두 수는 지식과 계획을 세어서 얻으므로 to_read 의 인자로 받는다. 수를 따로 저장하는 통계 테이블은 두지 않는다. 페르소나는 몇 개뿐이고 수를 자주 바꾸지 않기 때문이다.

- [신규] Persona (`model/persona/persona.py`)
  - 필드: persona_id: int | None, name: str, description: str, created_at: datetime, updated_at: datetime
  - 팩토리: create(name, description)
  - 상태 변경: with_profile(name, description). 고치기 API 는 바꿀 필드만 받는다. 빠진 필드를 지금 값으로 채우는 일은 service 가 한다
  - to_read(memory_count: int, plan_count: int) -> PersonaRead

- [신규] PersonaRead (`model/persona/persona_read.py`)
  - 필드: persona_id: int, name: str, description: str, memory_count: int, plan_count: int, created_at: datetime, updated_at: datetime

- [신규] PersonaIdentity (`model/persona/persona_identity.py`)
  - 필드: persona_id: int

- [신규] PersonaNotFoundException (`exception/persona/persona_not_found_exception.py`)
  - 기본 메시지를 쓴다 (404, "해당 리소스를 찾을 수 없습니다")

- [신규] PersonaInUseException (`exception/persona/persona_in_use_exception.py`)
  - ConflictException 을 상속한다 (409)
  - 지식 수와 계획 수를 받아 메시지를 만든다: "지식 7개, 계획 10개가 이 페르소나를 씁니다"
  - 지우기 API 가 쓴다. 웹 화면이 이 메시지를 그대로 보인다

- [신규] PersonaNameDuplicatedException (`exception/persona/persona_name_duplicated_exception.py`)
  - ConflictException 을 상속한다 (409)
  - 이름을 받아 메시지를 만든다: "이름이 dankim-persona 인 페르소나가 이미 있습니다"
  - 만들기와 고치기 API 가 쓴다

StrEnum, 하위 VO, 통계 모델: 없음.

사용자가 정한 것 (2026-11-20)
1. 시각 필드: created_at, updated_at 을 둔다. 서버 안에만 두고 API 응답에는 넣지 않는다. CLI 가 읽는 응답 모양은 그대로다
2. 이름 중복: 막는다. 같은 이름이 이미 있으면 만들기와 고치기를 409 로 거절한다

## Phase 2: 구현 계획

[평가 결과]
- api, service, infra: 이번 범위 밖 (건너뜀)
- model: 미충족. 페르소나 도메인을 새로 만든다

[설계 결정]
- 패턴: Bar 를 바탕으로, 조회 모델에 지식 수와 계획 수를 더한다 (to_read 인자)
- 시각 필드는 서버 안에만 둔다
- 이름 중복은 PersonaNameDuplicatedException(409) 로 거절한다. 검사는 나중에 service 가 하고, 테이블에도 이름 유일 조건을 건다 (Entity 단계)

[구현 계획]
1. add-model: Persona, PersonaRead, PersonaIdentity 와 예외 3개 (없음 404, 쓰는 곳 있음 409, 이름 중복 409)

Entity, 테이블, Repository, service, API 는 API 를 만들 때 한다.

## Phase 3: 구현 진행

### add-model (2026-11-20)

만든 파일
- `packages/model/src/task_plan_server/model/persona/`: `__init__.py`, `persona.py`, `persona_read.py`, `persona_identity.py`
- `packages/exception/src/task_plan_server/exception/persona/`: `__init__.py`, `persona_not_found_exception.py`, `persona_in_use_exception.py`, `persona_name_duplicated_exception.py`
- `specs/models.md` (새로 만듦)

검증
- `ruff check packages/model packages/exception`: 통과
- `mypy`: 통과 (46 파일)
- `lint-imports`: 계약 2개 지킴
- 직접 실행: create → with_profile → to_read(7, 10) 가 PersonaRead 를 돌려줌. 저장 전 to_read 는 ValueError. PersonaInUseException 은 409 와 "지식 7개, 계획 10개가 이 페르소나를 씁니다"
