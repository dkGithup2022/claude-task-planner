# Plan: DELETE /api/memories/{memory_id}

## 요청 스펙

지식 지우기. 웹 3번 화면의 [삭제] (확인 창 뒤). 응답 204. 출처: `corbina/notes/2026-11-20-ui.md` 3절과 끝의 API 표 ("요청·응답 모양은 서버 세션에서 API 탭의 형식대로 정한다").

정할 것: 없는 지식을 지우려 할 때. 문서에 없다. 404 로 한다. 노드·간선 지우기는 CLI 가 다시 만들 때 여러 번 부르므로 "이미 없으면 아무것도 하지 않는다" 이지만, 지식 지우기는 웹의 사람이 한 번 누르는 동작이라 없는 대상을 알리는 편이 맞다. 번들 관례(Writer.delete 가 404)와도 같다.

## Phase 1: 평가

### assess-api

미충족. [Usecase] MemoryDeleteUsecase.execute(identity) -> None. DELETE, 204.

### assess-usecase

부분 충족.
- [신규] MemoryWriter.delete(identity): find_write_by_id 선검증(없으면 404) → delete_by_id
- [신규] MemoryDeleteUsecase. @transactional
- infrastructure 신규: MemoryRepository.delete_by_id (soft-delete)

### assess-infra

부분 충족. delete_by_id(identity) -> None. 이미 지웠으면 no-op.

### assess-model

충족.

## Phase 2: 구현 계획

1. add-infrastructure → 2. add-query → 3. add-usecase → 4. add-api → 5. 시험: 지우면 GET 404, 없는 지식 404

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- MemoryRepository.delete_by_id (port·어댑터), MemoryWriter.delete, `usecase/memory_delete_usecase.py`, MemoryProvider 에 delete_usecase, DELETE /{memory_id}
- 검증: ruff, lint-imports, mypy 통과. 시험 2개 더함 (지우면 조회 404, 다시 지우기·없는 지식 404)
