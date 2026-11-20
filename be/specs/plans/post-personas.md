# Plan: POST /api/personas

## 요청 스펙

페르소나 만들기 (웹 4번 화면의 [+ 새 페르소나]). 요청 이름, 설명. 출처: `corbina/notes/2026-11-20-ui.md` 4절. 이름 중복은 409 로 막는다 (사용자, 2026-11-20).

정한 모양: 요청 `{"name": "be-developer", "description": "백엔드 개발 역할"}` (name 1~255자, description 은 빈 값 허용). 응답 201 `{"persona_id": 2}`. 같은 이름이 있으면 409 PersonaNameDuplicatedException.

## Phase 1: 평가

### assess-api

미충족. [Usecase] PersonaCreateUsecase.execute(command) -> PersonaIdentity.

### assess-usecase

미충족.
- [신규] PersonaWriter.create(command) -> PersonaIdentity: 지우지 않은 페르소나 가운데 같은 이름이 있으면 PersonaNameDuplicatedException(409). 없으면 Persona.create → save
- [신규] PersonaCreateCommand(name, description), PersonaCreateUsecase (@transactional)
- infrastructure 신규: PersonaRepository.save, exists_by_name(name, exclude: PersonaIdentity | None)
- 같은 이름 POST 가 동시에 오면 선검사를 둘 다 지날 수 있다. 그때는 부분 유일 인덱스가 둘째를 막는다 (500). 웹에서 사람이 누르는 동작이라 받아들인다

### assess-infra

부분 충족. save(persona) -> Persona, exists_by_name(name: str, exclude: PersonaIdentity | None) -> bool (고치기에서 자기 자신을 빼고 볼 때 exclude).

### assess-model

충족. Persona.create, PersonaNameDuplicatedException 이 있다.

## Phase 2: 구현 계획

1. add-infrastructure → 2. add-query (PersonaEntityQuery.exists_by_name_and_active·add·flush) → 3. add-usecase → 4. add-api → 5. 시험: 201 과 목록에 나옴, 같은 이름 409, 지운 페르소나의 이름은 다시 쓸 수 있음(지우기 API 뒤에 시험), 빈 이름 400

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- PersonaRepository.save, exists_by_name (port·어댑터), PersonaEntityQuery.exists_by_name_and_active·add·flush
- `service/persona/` PersonaWriter, DefaultPersonaWriter, PersonaCreateCommand, PersonaCreateUsecase, PersonaProvider 갱신
- POST "", PersonaCreateRequest, PersonaIdResponse
- 검증: ruff, lint-imports, mypy(215 파일) 통과. 시험 3개 더해 모두 51개 통과 (201·목록, 같은 이름 409·메시지, 빈 이름 400)
