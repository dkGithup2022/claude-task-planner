# Plan: PATCH /api/personas/{persona_id}

## 요청 스펙

페르소나 이름·설명 고치기 (웹 4번 화면의 [수정]). 출처: `corbina/notes/2026-11-20-ui.md` 4절. 정한 모양: 요청 `{"name"?, "description"?}` 바꿀 필드만 (빠지거나 null 이면 그대로). 응답 200 `{"persona_id": 1}`. 없으면 404, 다른 페르소나와 이름이 같으면 409.

## Phase 1: 평가

### assess-api

미충족. [Usecase] PersonaUpdateUsecase.execute(command) -> PersonaIdentity.

### assess-usecase

부분 충족.
- [신규] PersonaWriter.update(command) -> Persona: find_write_by_id 선검증(404) → 이름을 바꾸면 자기 자신을 뺀 같은 이름 검사(409) → with_profile → save
- [신규] PersonaUpdateCommand(persona_id, name | None, description | None), PersonaUpdateUsecase
- infrastructure 신규: PersonaRepository.find_write_by_id

### assess-infra

부분 충족. find_write_by_id(identity) -> Persona | None (지운 페르소나 제외).

### assess-model

충족. Persona.with_profile.

## Phase 2: 구현 계획

1. add-infrastructure → 2. add-query → 3. add-usecase → 4. add-api → 5. 시험: 이름만·설명만 바꾸기, 자기 이름 그대로 보내도 됨, 다른 페르소나 이름 409, 없는 페르소나 404

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- PersonaRepository.find_write_by_id (port·어댑터), PersonaEntityQuery.find_by_id_and_active
- PersonaWriter.update, PersonaUpdateCommand, PersonaUpdateUsecase, Provider 갱신
- PATCH /{persona_id}, PersonaUpdateRequest
- 검증: ruff, lint-imports, mypy(218 파일) 통과. 시험 2개 더해 모두 53개 통과
