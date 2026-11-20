# Plan: POST /api/memories

## 요청 스펙

지식 하나 만들기 (확정의 "새 지식으로 저장"). 출처: `corbina/notes/2026-11-20-api.md` 3절.

요청 `{"kind": "plan", "theme": "...", "body": "...", "persona_ids": [1], "source": [{"quote": "...", "plan_id": 11}]}`
응답 `{"memory_id": 7}`

CLI 기준 코드: `memory_api_converter.py` `to_create_body` 가 다섯 필드를 보내고, `to_memory_id` 로 응답의 memory_id 만 읽는다. 다른 점: 없음. 근거 필드 이름은 API 에서 `source`, 모델에서 `sources`.

## Phase 1: 평가

### assess-api

미충족.
- service 신규: [Usecase] MemoryCreateUsecase.execute(command: MemoryCreateCommand) -> MemoryIdentity
- 작업 계획: 요청 MemoryCreateRequest(kind: MemoryKind, theme: 빈 값 불가, body: 빈 값 불가, persona_ids: list[int], source: list[SourceItem(quote, plan_id)]). 응답 MemoryCreateResponse(memory_id). 201

### assess-usecase

미충족.
- [신규] MemoryWriter.create(command) -> MemoryIdentity
- [신규] MemoryCreateCommand(kind, theme, body, persona_ids, sources: tuple[MemorySource, ...])
- [신규] MemoryCreateUsecase: writer.create 를 감싼다. @transactional
- infrastructure 신규: MemoryRepository.save, find_write_by_id

### assess-infra

미충족.
- [신규] MemoryRepository (Pattern Bar 로 시작): save(memory) -> Memory, find_write_by_id(identity) -> Memory | None

Entity 와 테이블
- memories: id, kind(VARCHAR), theme(Text), body(Text), 공통 4컬럼. created_at·updated_at 은 웹의 최근 지식에 쓴다
- memory_personas: id, memory_id(인덱스), persona_id, position
- memory_sources: id, memory_id(인덱스), quote(Text), plan_id, position. 근거는 덧붙일 때마다 뒤에 붙으므로 순서를 지킨다

### assess-model

충족. Memory, MemorySource, MemoryKind, MemoryIdentity 가 있다.

## Phase 2: 구현 계획

1. add-infrastructure: MemoryRepository
2. add-entity-specs: MemoryEntity, MemoryPersonaEntity, MemorySourceEntity, migration `memory`
3. add-query: MemoryEntityQuery, DefaultMemoryRepository
4. add-usecase: MemoryWriter, DefaultMemoryWriter, MemoryCreateCommand, MemoryCreateUsecase, MemoryProvider
5. add-api: memory_router POST, MemoryCreateRequest, SourceItem, MemoryCreateResponse
6. 시험: 201·응답 모양·DB 에 근거 순서대로, 틀린 kind 400, 빈 theme 400

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: `infrastructure/memory/memory_repository.py` (save, find_write_by_id)
- add-entity-specs: MemoryEntity (memories), MemoryPersonaEntity (memory_personas), MemorySourceEntity (memory_sources), migration `20261120_5054c231fd89_memory.py`. 자식 테이블 FK 제약을 손으로 지움. `alembic check` 통과, DB FK 제약 0개
- add-query: MemoryEntityQuery, DefaultMemoryRepository (수정 때 personas, sources 통째 교체)
- add-usecase: `service/memory/` MemoryWriter, DefaultMemoryWriter, MemoryCreateCommand, MemoryCreateUsecase, `app/providers/memory_provider.py`, DOMAIN_PROVIDERS 에 MemoryProvider()
- add-api: `api/memory/memory_router.py` POST, MemoryCreateRequest, SourceItem, MemoryIdResponse, ROUTERS 에 memory_router
- 검증: ruff, lint-imports, mypy(176 파일) 통과
- 시험: `test_memory_api.py` 2개 (201·근거 순서가 DB 에 그대로, 틀린 kind·빈 theme 400). 모두 31개 통과
