# Plan: GET /api/memories

## 요청 스펙

웹의 지식 목록. 2번 화면(지식 검색)과 5번 메인의 최근 지식이 쓴다. 출처: `corbina/notes/2026-11-20-ui.md` 2·5절, 끝의 API 표. "요청·응답 모양은 서버 세션에서 API 탭의 형식대로 정한다".

화면이 요구하는 것
- 검색어는 작업 이름과 본문에서 찾는다. 종류와 페르소나로 거른다
- 열: 번호, 종류, 작업 이름, 페르소나, 덧붙인 횟수, 근거가 나온 계획
- 메인: 고친 시각 기준 최근 5개, "새로 저장"(만든 시각 = 고친 시각) / "고침" 구분, 지식 종류별 개수

## 정한 모양 (서버 세션)

요청 (query string, 모두 생략 가능)
- `q`: 검색어. 작업 이름이나 본문에 이 글자가 들어 있는 지식 (대소문자 무시). 비우면 거르지 않는다
- `kind`: knowledge | attitude | plan
- `persona_id`: 이 페르소나를 쓰는 지식
- `limit`: 최대 개수 (1~200). 생략하면 전부

응답 200

```jsonc
{
  "items": [
    {
      "memory_id": 7, "kind": "plan", "theme": "서비스 설계 문서 작성", "persona_ids": [1],
      "appended_count": 0, "source_plan_ids": [11],
      "created_at": "2026-11-20T04:39:00Z", "updated_at": "2026-11-20T04:39:00Z", "edited": false
    }
  ],
  "total": 7
}
```

- 순서는 고친 시각 최근 것부터. 메인의 최근 지식은 `?limit=5`
- `total` 은 limit 을 빼고 조건에 맞는 개수. 메인의 종류별 개수는 `?kind=...` 의 total 이나 조건 없는 목록으로 웹이 센다
- `edited`: 만든 뒤 고친 적이 있으면 true ("고침"). 초 단위 문자열로는 같은 초 안의 고침을 가를 수 없어 서버가 정확히 비교해 준다
- 본문은 목록에 넣지 않는다 (한 지식이 길다. 조회 화면이 GET /{memory_id} 로 읽는다)

## Phase 1: 평가

### assess-api

미충족. [Reader] MemoryReader.get_list(condition: MemoryListCondition) -> MemoryList(items, total). 응답 MemoryListResponse.

### assess-usecase

부분 충족. MemoryReader 에 get_list. 트랜잭션 없음 (목록과 개수를 따로 읽는다).
- infrastructure 신규: MemoryRepository.find_by_condition(condition) -> list[MemoryRead], count_by_condition(condition) -> int

### assess-infra

부분 충족. 두 메서드를 더한다. 동적 조건이라 EntityQuery 에서 `if` 로 where 를 붙인다. 검색어는 `icontains(autoescape=True)` (% 와 _ 를 글자 그대로).

### assess-model

부분 충족. 미뤄 둔 조건 모델을 만든다.
- [신규] MemoryListCondition (`model/memory/memory_list_condition.py`): query: str = "", kind: MemoryKind | None = None, persona_id: int | None = None, limit: int | None = None

## Phase 2: 구현 계획

1. add-model: MemoryListCondition
2. add-infrastructure: find_by_condition, count_by_condition
3. add-query: MemoryEntityQuery.find_by_condition_and_active, count_by_condition_and_active, DefaultMemoryRepository
4. add-usecase: MemoryReader.get_list, `service/memory/dto/memory_list.py` (items, total)
5. add-api: GET "", MemoryListResponse·MemoryListItem
6. 시험: 고친 시각 순, q 가 작업 이름·본문을 찾음, kind·persona_id 로 거름, limit 과 total, edited, 지운 지식 빠짐, % 글자 그대로

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-model: `model/memory/memory_list_condition.py` MemoryListCondition
- add-infrastructure·add-query: MemoryRepository.find_by_condition, count_by_condition. MemoryEntityQuery 의 `_where_condition` 이 동적 조건을 붙인다 (icontains autoescape, memory_personas 서브쿼리)
- add-usecase: MemoryReader.get_list, `service/memory/dto/memory_list.py`
- add-api: GET "", MemoryListResponse·MemoryListItem (query 는 Annotated[..., Query()] 모양. ruff B008 때문)
- 검증: ruff, lint-imports, mypy(191 파일) 통과
- 시험: 3개 더해 모두 46개 통과 (고친 시각 순·덧붙인 횟수·근거 계획·edited·본문 없음, q·kind·persona_id·limit·total·지운 지식 빠짐, % 글자 그대로)
