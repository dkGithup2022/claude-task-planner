# Plan: model Memory

## 요청 스펙

사용자 지시 (2026-11-20): be 는 model 을 하나씩 먼저 만들고, 그다음 API 를 하나씩 만든다. 각각 만들기 전에 be-planner 를 실행한다.

이번 범위는 model 레이어의 지식 하나다. API, service, infrastructure, Entity 는 이번에 만들지 않는다. 그래서 Phase 1 의 api·usecase·infra 평가는 건너뛰고 model 평가만 한다.

지식 데이터 (출처: `corbina/notes/2026-11-20-current-data.md` 1절)

```jsonc
{
  "memory_id": 6,                      // 서버가 준다
  "kind": "plan",                      // knowledge(작업 방법·규칙) | attitude(판단 방식) | plan(작업을 나누는 방식)
  "theme": "기획 문서 작성",            // 작업 이름
  "body": "기획 문서는 ...\n\n****** KNOWLEDGE APPENDED 1 ********\n1. 상위 기획에서 ...",
  "persona_ids": [1],                  // 적용할 페르소나
  "source": [                          // 근거. 덧붙일 때마다 뒤에 붙는다
    { "quote": "상위 기획과 하위 기획으로 나누어 생각하면 좋음.", "plan_id": 11 }
  ]
}
```

이 모델을 쓰는 API (출처: `2026-11-20-api.md` 3절, `2026-11-20-ui.md` 2·3·5절)
- `POST /memories/search`: 같은 종류이고 페르소나가 하나라도 겹치는 지식을 검색어와 가까운 순으로. theme 이 있으면 작업 이름이 같은 것만. 응답 항목은 memory_id, kind, theme, body, score
- `POST /memories`: 만들기
- `GET /memories/{memory_id}`: 조회
- `PATCH /memories/{memory_id}`: 바꿀 필드만 보낸다. CLI 의 덧붙이기는 body, source 를, 웹은 theme, kind, persona_ids, body 를 보낸다
- `DELETE /memories/{memory_id}`: 지우기
- `GET /memories`: 웹 목록. 검색어(작업 이름·본문), 종류, 페르소나 조건. 열에 덧붙인 횟수와 근거가 나온 계획이 있다. 메인 화면의 최근 지식은 고친 시각 순
- 시각: `created_at`, `updated_at` 을 서버가 채운다. 만든 시각과 고친 시각이 같으면 "새로 저장", 다르면 "고침"

정한 것 (서버 지시서 5절): 서버 안에 `search_knowledge(searchParam: SearchParam)` 인터페이스를 두고, 세부 구현은 나중에 짠다.

## Phase 1: 평가

### assess-api

건너뜀. 이번 범위는 model 만이다.

### assess-usecase

건너뜀. 이번 범위는 model 만이다.

### assess-infra

건너뜀. 이번 범위는 model 만이다.

### assess-model

충족 여부: 미충족. 지식 도메인이 없다. 지금 model 에는 페르소나만 있다.

작업 계획

- 패턴: Bar. 조회 모델에 덧붙인 횟수와 근거 계획 목록을 더하는데, 둘 다 지식 자신의 본문과 근거에서 계산되므로 to_read 는 인자가 없다

- [신규] MemoryKind (`model/memory/memory_kind.py`)
  - 값: KNOWLEDGE = "knowledge", ATTITUDE = "attitude", PLAN = "plan"
  - 번들 규칙은 값을 이름과 같게(대문자로) 두지만, CLI 가 소문자로 보내고 읽으므로 소문자로 둔다. CLI 코드가 기준이다

- [신규] MemorySource (`model/memory/memory_source.py`)
  - 필드: quote: str, plan_id: int
  - 사용자가 한 말과 그 말이 나온 계획

- [신규] Memory (`model/memory/memory.py`)
  - 필드: memory_id: int | None, kind: MemoryKind, theme: str, body: str, persona_ids: tuple[int, ...], sources: tuple[MemorySource, ...], created_at: datetime, updated_at: datetime
  - API 필드 이름은 `source` 이고 모델 필드 이름은 CLI model 과 같게 `sources` 로 둔다. 바꾸는 일은 api 레이어가 한다
  - 팩토리: create(kind, theme, body, persona_ids, sources)
  - 상태 변경: with_update(kind, theme, body, persona_ids, sources). 고치기 API 는 바꿀 필드만 받는다. 빠진 필드를 지금 값으로 채우는 일은 service 가 한다
  - to_read() -> MemoryRead

- [신규] MemoryRead (`model/memory/memory_read.py`)
  - 필드: memory_id: int, kind, theme, body, persona_ids, sources, appended_count: int, source_plan_ids: tuple[int, ...], created_at, updated_at
  - appended_count: 본문에 `****** KNOWLEDGE APPENDED ` 머리가 몇 번 나오는지. CLI 의 `Memory.append` 가 번호를 매기는 규칙과 같다. 서버는 본문을 읽어 세기만 하고 고치지 않는다
  - source_plan_ids: 근거의 plan_id 를 처음 나온 순서대로, 겹치지 않게

- [신규] MemoryIdentity (`model/memory/memory_identity.py`)
  - 필드: memory_id: int

- [신규] SearchParam (`model/memory/search_param.py`)
  - 필드: kind: MemoryKind, query: str, persona_ids: tuple[int, ...], theme: str | None = None, limit: int = 10
  - `search_knowledge(search_param: SearchParam)` 인터페이스의 인자. 이름은 사용자가 정한 대로 둔다. 인터페이스 자체는 infrastructure 레이어에 만든다

- [신규] MemorySearchHit (`model/memory/memory_search_hit.py`)
  - 필드: memory_id: int, kind: MemoryKind, theme: str, body: str, score: float
  - 검색 결과 한 줄. 점수가 높을수록 검색어와 가깝다

- [신규] MemoryNotFoundException (`exception/memory/memory_not_found_exception.py`)
  - 기본 메시지를 쓴다 (404)

미룬 것: 웹 목록(`GET /memories`)의 조건 모델. 요청 모양(정렬, 개수, 쪽 나누기)을 아직 정하지 않았으므로 그 API 를 만들 때 정한다.

StrEnum 외 하위 VO 는 MemorySource 하나. 통계 모델: 없음.

## Phase 2: 구현 계획

사용자 확정 (2026-11-20: "오케이 고고").

[평가 결과]
- api, service, infra: 이번 범위 밖 (건너뜀)
- model: 미충족. 지식 도메인을 새로 만든다

[구현 계획]
1. add-model: assess-model 산출물의 클래스 8개와 MemoryNotFoundException

## Phase 3: 구현 진행

### add-model (2026-11-20)

만든 파일
- `packages/model/src/task_plan_server/model/memory/`: `__init__.py`, `memory.py`, `memory_read.py`, `memory_identity.py`, `memory_kind.py`, `memory_source.py`, `search_param.py`, `memory_search_hit.py`
- `packages/exception/src/task_plan_server/exception/memory/`: `__init__.py`, `memory_not_found_exception.py`
- `specs/models.md` 에 memory 절을 더함

검증
- ruff, mypy(56 파일), lint-imports(계약 2개): 통과
- 직접 실행: 덧붙임 머리 2개, 근거 계획 1, 11, 1 인 지식의 to_read 가 appended_count 2, source_plan_ids (1, 11) 을 돌려줌
