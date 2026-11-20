# Plan: POST /api/memories/search

## 요청 스펙

지식 검색. 같은 종류이고, 대상 페르소나 가운데 하나라도 겹치는 지식을 검색어와 가까운 순으로 돌려준다. theme 이 있으면 작업 이름이 같은 것만. 출처: `corbina/notes/2026-11-20-api.md` 3절.

요청 `{"kind": "plan", "query": "기획 문서 작성", "persona_ids": [1], "theme": null, "limit": 10}`
응답 `{"items": [{"memory_id": 6, "kind": "plan", "theme": "...", "body": "...", "score": 0.032}]}`

정한 것 (지시서 5절): 서버 안에 `search_knowledge(searchParam: SearchParam)` 인터페이스를 두고 세부 구현(벡터, 글자 검색)은 나중에 짠다. 처음에는 가장 단순한 구현으로 둔다.

CLI 기준 코드: `to_search_body` 가 다섯 필드를 모두 보낸다 (theme 은 null 일 수 있다). `to_search_hits` 는 items 의 다섯 필드를 읽고 score 가 없으면 0 으로 본다. 다른 점: 없음.

## Phase 1: 평가

### assess-api

미충족. [Reader] MemoryReader.search(search_param: SearchParam) -> list[MemorySearchHit]. 요청 MemorySearchRequest(kind 필수, query: str, persona_ids: list[int], theme: str | None = None, limit: int = 10, 1~100). 응답 MemorySearchResponse(items). 200. POST 이지만 조회다.

### assess-usecase

부분 충족. MemoryReader 에 search 를 더한다. 검색 port 에 위임만 한다. 트랜잭션 없음.
- infrastructure 신규: KnowledgeSearcher.search_knowledge(search_param) -> list[MemorySearchHit]

### assess-infra

미충족. 검색 port 가 없다.
- [신규] `infrastructure/memory/knowledge_searcher.py` KnowledgeSearcher (ABC). 메서드 이름과 인자는 사용자가 정한 대로 `search_knowledge(search_param: SearchParam)`. 구현을 바꿔 끼울 수 있게 MemoryRepository 와 따로 둔다
- 처음 구현 `DefaultKnowledgeSearcher` (persistence): 글자 맞추기
  1. 거르기: 지우지 않은 지식 가운데 kind 가 같고, persona_ids 가 하나라도 겹치고, theme 을 주면 작업 이름이 같은 것 (EntityQuery, 서브쿼리)
  2. 점수: 검색어를 공백으로 나눈 낱말마다 작업 이름에 있으면 2, 본문에 있으면 1. 합을 (낱말 수 × 3) 으로 나눠 0~1. 대소문자 무시
  3. 점수가 0 보다 큰 것만, 점수 높은 순, 같으면 고친 시각 최근 순, limit 개
  4. 검색어에 낱말이 없으면 거른 지식을 고친 시각 최근 순으로 점수 0 과 함께 돌려준다
- 나중에 벡터 검색으로 바꿀 때 이 구현 하나만 갈아 끼운다

### assess-model

충족. SearchParam, MemorySearchHit 가 있다.

## Phase 2: 구현 계획

1. add-infrastructure: KnowledgeSearcher
2. add-query: MemoryEntityQuery.find_for_search_and_active, `persistence/memory/text_match_score.py`, DefaultKnowledgeSearcher
3. add-usecase: MemoryReader.search, MemoryProvider 에 searcher
4. add-api: POST /search, MemorySearchRequest, MemorySearchResponse
5. 시험: 종류·페르소나·작업 이름으로 거름, 점수 순, 지운 지식 빠짐, limit, 검색어와 안 맞는 지식 빠짐, 틀린 kind 400

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: `infrastructure/memory/knowledge_searcher.py` KnowledgeSearcher.search_knowledge
- add-query: MemoryEntityQuery.find_for_search_and_active (memory_personas 서브쿼리), `persistence/memory/text_match_score.py`, `persistence/memory/default_knowledge_searcher.py`
- add-usecase: MemoryReader.search (KnowledgeSearcher 주입), MemoryProvider 에 searcher
- add-api: POST /search, MemorySearchRequest, MemorySearchResponse·MemorySearchItem
- 검증: ruff, lint-imports, mypy(188 파일) 통과
- 시험: 3개 더해 모두 43개 통과 (종류·페르소나로 거르고 점수 순, theme·limit·지운 지식 빠짐, 틀린 kind 400)
