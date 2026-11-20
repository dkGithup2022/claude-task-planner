# Plan: PATCH /api/memories/{memory_id}

## 요청 스펙

지식 고치기. 바꿀 필드만 보낸다. 출처: `corbina/notes/2026-11-20-api.md` 3절 (body, source), `2026-11-20-ui.md` 3절 (theme, kind, persona_ids 로 넓힘).
- CLI 의 덧붙이기: GET 으로 읽고, 덧붙임 머리와 글, 근거를 붙인 결과 전체를 body, source 로 보낸다. 서버는 받은 것을 저장만 한다
- 웹의 수정: body, theme, kind, persona_ids 를 바꿀 필드만 보낸다
- 응답 `{"memory_id": 1}`. 없으면 404

CLI 기준 코드: 아직 `POST /memories/{id}/append` 를 부른다. CLI 세션이 `PATCH` 로 바꾼다 (지시서 11절). 문서를 따른다.

## Phase 1: 평가

### assess-api

미충족. [Usecase] MemoryUpdateUsecase.execute(command) -> MemoryIdentity. 요청 MemoryUpdateRequest — kind, theme, body, persona_ids, source 모두 생략 가능. 빠지거나 null 이면 바꾸지 않는다. theme·body 는 보낼 때 빈 값 불가. 응답 MemoryIdResponse. 200.

### assess-usecase

부분 충족.
- [신규] MemoryWriter.update(command) -> Memory: find_write_by_id 선검증(없으면 404), 빠진 필드는 지금 값으로 채워 with_update → save. 고친 시각(updated_at)이 바뀐다 (웹의 최근 지식이 쓴다)
- [신규] MemoryUpdateCommand(memory_id, kind, theme, body, persona_ids, sources — None 이면 바꾸지 않음)
- [신규] MemoryUpdateUsecase. @transactional
- 본문을 고치거나 덧붙임 머리를 만들지 않는다 (지시서 6절)
- infrastructure: 기존 save, find_write_by_id

### assess-infra

충족.

### assess-model

충족. Memory.with_update 가 있다.

## Phase 2: 구현 계획

1. add-usecase → 2. add-api → 3. 시험: CLI 덧붙이기 모양(body+source)만 보내면 kind·theme·persona_ids 그대로, 웹 모양(theme, kind, persona_ids), 덧붙인 횟수가 늘어난 본문이 그대로 저장, updated_at 이 바뀜, 없는 지식 404, 빈 theme 400

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-usecase: MemoryWriter.update (빠진 필드는 지금 값으로), `dto/memory_update_command.py`, `usecase/memory_update_usecase.py`, MemoryProvider 에 update_usecase
- add-api: PATCH /{memory_id}, `dto/memory_update_request.py`
- 검증: ruff, lint-imports, mypy(182 파일) 통과
- 시험: 3개 더함 (CLI 덧붙이기 모양은 kind·theme·persona_ids 그대로이고 본문·근거는 받은 그대로이며 updated_at 이 늘어남, 웹 모양, 없는 지식 404·빈 theme 400)
