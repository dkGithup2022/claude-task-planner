# 계획: 페르소나·지식 데이터와 접근 인터페이스를 선언한다 (mock 구현과 서버 구현을 함께)

## 요청

"re_code.html 데이터·API 탭에 다른 mock 정보들이 있을 거야. 이거 model, port 를 플래너로 해서 넣고 default_, mock_ 을 각각 넣어서 planner 로 견적을 봐 줄 수 있니?" (사용자, 2026-11-19)

근거: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-task-plan-manager-data-api.md "지식과 페르소나" (지식 spec, GET /personas, POST /memories/search, POST /memories, POST /memories/{memory_id}/append). 이 문서는 "응답 예시가 곧 mock 데이터다"라고 정했다.

## 1. 평가

### 나누기

- 포트
  1. 페르소나 목록 읽기 (GET /personas)
  2. 지식 검색 (POST /memories/search)
  3. 지식 만들기 (POST /memories)
  4. 지식 덧붙이기 (POST /memories/{memory_id}/append)
  5. (선택) 계획 저장소의 서버 구현. 이미 있는 `port/plan_api/` 에 `Default` 구현만 더한다
- 공통 기능: 서버 구현 셋 이상이 같은 HTTP 호출(주소, 시간 제한, JSON 주고받기, 실패 예외)을 쓴다. 번들 규칙상 두 곳 이상이 같이 쓰고 도메인 지식이 없으면 공통 기능이다 → `common/` 에 HTTP JSON 호출 함수 하나 (tool-add-common)
- 구현을 고르는 곳: 지금은 mock, 서버가 생기면 서버 구현. 포트마다 고르는 함수 하나를 둔다 (아래 "구현 고르기")
- 워크플로로 넘길 것: 없음. 이 포트들을 쓰는 곳은 make_plan 의 register_plan(페르소나), split_plan 의 나누기(지식 검색), B·C 흐름(지식 만들기·덧붙이기)

### tool-assess-port

**판정**: 미충족 (페르소나·지식 포트가 없다)

**접근별 판정**

| 접근 | 판정 | 포트 | 메서드 |
|---|---|---|---|
| 페르소나 목록 | 미충족 | persona_api (신규) | PersonaApiReader.list_personas() -> tuple[Persona, ...] |
| 지식 검색 | 미충족 | memory_api (신규) | MemoryApiReader.search(query) -> tuple[MemorySearchHit, ...] |
| 지식 만들기 | 미충족 | memory_api | MemoryApiWriter.create(new_memory) -> int |
| 지식 덧붙이기 | 미충족 | memory_api | MemoryApiWriter.append(memory_id, addition) -> int |
| 계획 저장소 서버 구현 (선택) | 부분 충족 | plan_api (있음) | 인터페이스는 그대로, `DefaultPlanApiReader`, `DefaultPlanApiWriter` 를 더함 |

**포트 계획**

- [신규] port/persona_api/
  - PersonaApiReader.list_personas() -> tuple[Persona, ...] — 없으면 빈 튜플, 서버 실패면 PersonaApiError
  - 구현
    - `MockPersonaApiReader`: `.mockData/personas.json` 을 읽는다. 파일이 없으면 데이터·API 문서의 응답 예시(1 dankim-persona, 2 be-developer)로 만들어 둔다 (mock 기본 페르소나)
    - `DefaultPersonaApiReader`: `GET {서버 주소}/personas`
  - 변환기: `PersonaApiConverter.to_persona(body) -> Persona` (서버 응답), `MockPersonaFileConverter` (`to_file` / `to_data`)
  - 예외: PersonaApiError

- [신규] port/memory_api/
  - MemoryApiReader.search(query: MemorySearchQuery) -> tuple[MemorySearchHit, ...] — 점수 높은 순, limit 개까지. 없으면 빈 튜플
  - MemoryApiWriter.create(new_memory: NewMemory) -> int — 새 memory_id
  - MemoryApiWriter.append(memory_id: int, addition: MemoryAddition) -> int — 본문 뒤에 body, 근거 뒤에 source. 지식이 없으면 MemoryApiError
  - 구현
    - `MockMemoryApiReader`, `MockMemoryApiWriter`: `.mockData/memories.json` (지식 전부), id 는 `.mockData/ids.json` 의 `memory`. 파일이 없으면 응답 예시의 지식 두 개(테이블 설계)로 만들어 둔다
      - mock 검색: kind 가 같고, persona_ids 가 겹치고, theme 이 주어지면 같은 것 가운데, query 의 낱말이 theme·body 에 들어 있는 수로 점수를 매겨 높은 순 (서버의 의미 검색을 흉내만 낸다)
    - `DefaultMemoryApiReader`, `DefaultMemoryApiWriter`: `POST {서버 주소}/memories/search`, `POST /memories`, `POST /memories/{memory_id}/append`
  - 변환기: `MemoryApiConverter` (`to_search_hit`, `to_search_body`, `to_create_body`, `to_append_body`), `MockMemoryFileConverter`
  - 예외: MemoryApiError
  - dto
    - MemorySearchQuery(kind: MemoryKind, query: str, persona_ids: tuple[int, ...], theme: str | None, limit: int)
    - MemorySearchHit(memory_id: int, kind: MemoryKind, theme: str, body: str, score: float) — 검색 응답 모양. persona_ids 와 근거가 없어 model 이 아니라 dto
    - NewMemory(kind: MemoryKind, theme: str, body: str, persona_ids: tuple[int, ...], sources: tuple[MemorySource, ...])
    - MemoryAddition(body: str, sources: tuple[MemorySource, ...])

- [부분 충족, 선택] port/plan_api/
  - `DefaultPlanApiReader`, `DefaultPlanApiWriter`: 데이터·API 문서의 계획·노드·간선 API 를 HTTP 로. 변환기 `PlanApiConverter` (응답 모양이 mock 파일과 같으므로 `MockPlanFileConverter` 의 노드·간선 변환을 같이 쓸 수 있는지 만들 때 본다)
  - 계획 상태 바꾸기는 `PATCH /plans/{plan_id}/status` (가안. 데이터·API 문서에 아직 없다)

- 서버 구현의 공통 설정
  - 서버 주소: 환경 변수 `TASK_PLANNER_API_URL` (번들 규칙 `{PKG}_{서비스}_URL`). 서비스가 하나라 이름을 하나로 둔다
  - 시간 제한 30 초, 실패하면 그 포트의 예외에 요청 경로·상태 코드·응답 글을 담는다
  - 새 라이브러리 없이 표준 라이브러리(`urllib.request`, `json`)로 한다
  - 시험: 진짜 서버를 부르지 않는다. 시험 안에서 `http.server` 로 가짜 서버를 띄우거나 호출 함수를 바꿔 끼운다

**구현 고르기 (사용자 확인 필요)**

포트를 쓰는 쪽(워크플로 단계)이 `Mock…` 이나 `Default…` 를 직접 고르지 않게, 포트 폴더마다 고르는 함수 하나를 둔다.

```python
# port/persona_api/persona_api_choice.py
def persona_api_reader() -> PersonaApiReader:
    """TASK_PLANNER_API_URL 이 있으면 서버 구현, 없으면 mock."""
```

- 안 가: 서버 주소 환경 변수가 있으면 서버, 없으면 mock (위 모양)
- 안 나: 별도 환경 변수 `TASK_PLANNER_API=mock|server`
- 안 다: 고르는 함수 없이 단계가 직접 Mock 을 쓰고, 서버를 만들 때 바꾼다 (지금 plan_api 를 쓰는 save_graph 시험은 이 모양)

**model 층 요청**

- 대상: persona (신규)
- 클래스: Persona (persona/persona.py)
- 필드: persona_id: int, name: str, description: str
- 쓰는 곳: PersonaApiReader.list_personas
- 이유: 계획과 노드가 persona_ids 로 가리키는 도메인 데이터

- 대상: memory (신규)
- 클래스: Memory (memory/memory.py), MemorySource (memory/memory_source.py), MemoryKind (memory/memory_kind.py)
- 필드: Memory(memory_id: int, kind: MemoryKind, theme: str, body: str, persona_ids: tuple[int, ...], sources: tuple[MemorySource, ...]), MemorySource(quote: str, plan_id: int)
- 쓰는 곳: mock 저장 파일, NewMemory·MemoryAddition 의 근거
- 이유: 지식은 이 도구가 쌓는 주된 데이터

**사용자 확인 필요**

1. 구현 고르기 (가 / 나 / 다)
2. 계획 저장소의 서버 구현(`DefaultPlanApi…`)도 이번에 같이 만들지
3. mock 검색의 흉내 방식 (낱말이 들어 있는 수로 점수)
4. 공통 HTTP 함수를 `common/` 에 더하는 것 (tool-add-common)

### tool-assess-model

**판정**: 미충족

**클래스별 계획**

- [신규] model/persona/persona.py — Persona
  - 필드: persona_id: int, name: str, description: str
- [신규] model/memory/memory_kind.py — MemoryKind(StrEnum): KNOWLEDGE = "knowledge", ATTITUDE = "attitude", PLAN = "plan"
- [신규] model/memory/memory_source.py — MemorySource
  - 필드: quote: str, plan_id: int
- [신규] model/memory/memory.py — Memory
  - 필드: memory_id: int, kind: MemoryKind, theme: str, body: str, persona_ids: tuple[int, ...], sources: tuple[MemorySource, ...]
  - 동작: append(body: str, sources: tuple[MemorySource, ...]) -> Memory (본문 뒤에 빈 줄 하나를 두고 덧붙이고, 근거를 뒤에 붙인 새 객체. mock 덧붙이기가 쓴다)

**사용자 확인 필요**

- 덧붙일 때 본문 사이 구분 (빈 줄 하나로 제안)

## 사용자 확인 (2026-11-19)

1. 구현 고르기: 나. 환경 변수 `TASK_PLANNER_API=mock|server` 로 고른다. 없으면 mock
2. 서버 구현(`Default…`)도 지금 HTTP 로 만든다. 페르소나, 지식, 계획 저장소 모두 (사용자: 어려운 게 아니니 지금 하자). 서버가 없으므로 시험은 가짜 서버로 한다
3. mock 검색은 검색어와 상관없이 정해진 결과를 돌려준다
4. 공통 HTTP 는 `common/http/` 에 둔다
5. 검색한 지식을 글로 보일 때(프롬프트 입력 등) 아래처럼 구분이 쉽게 쓴다. 지식에 덧붙일 때 본문 사이도 같은 모양으로 구분한다 (`****** KNOWLEDGE APPENDED <n> ********`)

   ```text
   ****** KNOWLEDGE SEARCHED 1 ********
   {내용}

   ****** KNOWLEDGE SEARCHED 2 ********
   {내용}
   ```

## 2. 구현 계획 (견적)

**평가 요약**
- port: 미충족 — persona_api, memory_api 신규. plan_api 는 서버 구현만 더함 (선택)
- model: 미충족 — persona, memory 신규
- 공통 기능: HTTP JSON 호출 하나 (서버 구현이 셋 이상이라)

**만드는 순서와 크기**

| 순서 | 스킬 | 만드는 것 | 파일 수 (대략) | 시험 |
|---|---|---|---|---|
| 1 | add-model | model/persona/ (Persona), model/memory/ (Memory, MemorySource, MemoryKind) | 4 | Memory.append 1 개 |
| 2 | add-common | common/http_json.py (주소 + 경로로 GET/POST/PATCH/DELETE, 시간 제한, 실패 예외) | 2 | 가짜 서버로 성공·실패 2 개 |
| 3 | add-port | port/persona_api/ (인터페이스, Mock, Default, 변환기 2, 위치, 예외, 고르는 함수) | 8 | mock 기본 페르소나, 서버 구현 각 1~2 개 |
| 4 | add-port | port/memory_api/ (인터페이스 2, Mock 2, Default 2, 변환기 2, mock 파일 함수, 위치, 예외, dto 4, 고르는 함수 2) | 17 | mock 검색·만들기·덧붙이기, 서버 구현 각 1~2 개 |
| 5 (선택) | add-port | port/plan_api/ 에 Default 2, 변환기, 고르는 함수 2 | 5 | 서버 구현 2~3 개 |
| 6 | 최종 검증 | ruff, lint-imports, mypy, pytest | | |

합계: 파일 약 31 개(선택 포함 36 개), 시험 약 12~15 개.

**만든 뒤 바뀌는 곳**
- split_plan 의 `Participant` 를 `Persona` model 로 바꾼다
- register_plan 이 `list_personas()` 의 첫 페르소나(mock 기본 dankim-persona)를 참여 페르소나로 넣는다
- split_tree 의 "검색 결과"를 지식 검색으로 채울 수 있다 (지금은 "없음". 연결은 따로 정한다)

## 3. 진행 기록


### 2026-11-19 만듦
- add-model: model/persona/persona.py, model/memory/(memory.py, memory_source.py, memory_kind.py), 시험 tests/model/memory/test_memory.py
- add-common: common/http/(http_json.py, http_json_error.py, api_choice.py), common/mock_data.py (mock 폴더와 mock id. plan_api 의 위치·id 함수를 여기로 옮김)
- add-port: port/persona_api/ (인터페이스, Mock, Default, 변환기, 예외, 고르기)
- add-port: port/memory_api/ (인터페이스 2, Mock 2, Default 2, 변환기, mock 파일 함수, 예외, dto 4, 고르기)
- add-port: port/plan_api/ 에 Default 2, 요청 변환기, 서버 호출 함수, 고르기. `MockPlanFileConverter` 를 `PlanJsonConverter` 로 이름을 바꿈 (응답과 mock 파일이 같은 모양이라 둘 다 씀)
- 시험: tests/port/conftest.py 에 가짜 서버(FakeApiServer), persona_api 4 개, memory_api 3 개, plan_api 서버 구현 3 개, api_choice 2 개
- 견적과 다른 점: mock 지식 id 는 ids.json 을 쓰지 않고 지금 있는 가장 큰 id + 1 로 한다 (처음 값의 id 와 겹치지 않게 하는 가장 단순한 방법)
- 검증: ruff, import 검사 계약 4개, mypy (303 파일), pytest 82개 통과

