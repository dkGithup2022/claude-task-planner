# Plan: GET /api/memories/{memory_id}

## 요청 스펙

지식 하나 조회. CLI 가 덧붙이기 전에 읽고, 웹 3번 화면(지식 조회)이 읽는다. 없으면 404. 출처: `corbina/notes/2026-11-20-api.md` 3절.

응답 `{"memory_id": 1, "kind": "knowledge", "theme": "테이블 설계", "body": "...", "persona_ids": [1], "source": [{"quote": "...", "plan_id": 1}]}`

CLI 기준 코드: 아직 없다 (CLI 세션이 `MemoryApiReader.get` 을 더한다). 문서를 따른다.

## Phase 1: 평가

### assess-api

미충족. [Reader] MemoryReader.get_by_id(identity) -> MemoryRead. 응답 MemoryResponse (문서의 여섯 필드. source 는 SourceItem 목록). 200.

### assess-usecase

미충족. MemoryReader 가 없다.
- [신규] MemoryReader.get_by_id: 없으면 MemoryNotFoundException
- infrastructure 신규: MemoryRepository.find_by_id(identity) -> MemoryRead | None

### assess-infra

부분 충족. find_by_id 를 더한다 (Memory.to_read 로 바꿔 돌려준다).

### assess-model

충족. MemoryRead 가 있다.

## Phase 2: 구현 계획

1. add-infrastructure: find_by_id → 2. add-query → 3. add-usecase: MemoryReader, DefaultMemoryReader, Provider → 4. add-api: GET, MemoryResponse → 5. 시험: 만든 지식이 그대로 나옴(근거 순서), 없는 지식 404

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure·add-query: MemoryRepository.find_by_id (to_read 로 바꿔 돌려준다)
- add-usecase: MemoryReader, DefaultMemoryReader, MemoryProvider 에 reader
- add-api: GET /{memory_id}, MemoryResponse
- 검증: ruff, lint-imports, mypy(179 파일) 통과. 시험 2개 더해 모두 33개 통과
