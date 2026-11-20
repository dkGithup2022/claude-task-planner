# 데이터 스펙

작성: 2026-11-20
입력: docs/data-inventory.md, 화면 6장(docs/design-export/*.dc.html), BE 스펙 `../be/specs/models.md`, `../be/specs/api.md`
상태: 검수 완료 (사용자 지시 "순차적으로 자유롭게 진행, API 데이터 관련만 질문" 에 따라 BE 스펙을 근거로 스스로 정함, 2026-11-20)

규칙
- 필드 이름은 BE 응답 그대로 snake_case 다 (BE). 화면 타입(`types/data`)도 같은 이름을 쓴다. 바꾸는 층을 두지 않는다
- enum 값은 번들 관례(SCREAMING_SNAKE_CASE) 대신 BE 의 소문자 값을 쓴다 (BE 와 CLI 가 그 값을 주고받는다)
- 시각은 BE 가 주는 UTC 문자열 `2026-11-20T04:16:15Z` 를 그대로 두고, 화면이 "11-20 13:16" (사용자 시간대)로 바꿔 보인다

## 결정 필요

없음.

## 보류

- 지식 검색 결과 (MemorySearchHit, `POST /api/memories/search`): CLI 가 쓰는 API 다. 웹 화면은 `GET /api/memories` 목록을 쓴다
- 노드 실행 기록 (회차, 시각, 결과, 실패 이유): 서버에 없다 (로컬에만 있다). 웹 UI 문서 1번 화면 "지금 못 보이는 것"

---

## 도메인

### Persona (페르소나)
작업을 맡는 역할 — Personas.dc.html, PlanGraph.dc.html, Memories.dc.html

| 필드 | 타입 | 필수 | 근거 |
|---|---|---|---|
| persona_id | number | 예 | BE. Personas.dc.html "#" 열 |
| name | string | 예 | BE. Personas.dc.html "dankim-persona". 페르소나마다 다르다 |
| description | string | 예 | BE. Personas.dc.html "사용자의 기본 작업 역할". 빈 문자열일 수 있다 |
| memory_count | number | 예 | BE (목록 응답). Personas.dc.html "지식 수 7" |
| plan_count | number | 예 | BE (목록 응답). Personas.dc.html "계획 수 1". 참여 또는 노드 담당인 계획 |

### Memory (지식)
작업할 때 쓰는 지식 하나 — Memories.dc.html, MemoryDetail.dc.html, Main.dc.html

| 필드 | 타입 | 필수 | 근거 |
|---|---|---|---|
| memory_id | number | 예 | BE. "지식 #1" |
| kind | MemoryKind | 예 | BE. "지식" · "계획" |
| theme | string | 예 | BE. "테이블 설계" (작업 이름) |
| body | string | 예 (조회만) | BE `GET /api/memories/{id}`. MemoryDetail.dc.html 본문. 덧붙임 머리 `****** KNOWLEDGE APPENDED <n> ********` 가 들어 있다. 목록 응답에는 없다 |
| persona_ids | number[] | 예 | BE. "dankim-persona" (이름은 페르소나 목록으로 바꾼다) |
| source | MemorySource[] | 예 (조회만) | BE `GET /api/memories/{id}`. MemoryDetail.dc.html 근거. 목록 응답에는 없다 |
| appended_count | number | 예 (목록만) | BE `GET /api/memories`. Memories.dc.html "덧붙임 3" |
| source_plan_ids | number[] | 예 (목록만) | BE `GET /api/memories`. Memories.dc.html "근거 계획 3, 11" |
| created_at | string | 예 (목록만) | BE. 만든 시각 UTC |
| updated_at | string | 예 (목록만) | BE. 고친 시각 UTC. 목록 순서 |
| edited | boolean | 예 (목록만) | BE. Main.dc.html "새로 저장"(false) / "고침"(true) |

관계: Memory → Persona (persona_ids), MemorySource → Plan (plan_id).
목록 한 줄(MemoryListItem)과 조회(MemoryDetail)는 필드가 다르므로 화면 타입도 둘로 둔다.

### Plan (계획)
작업 계획 — Plans.dc.html, PlanGraph.dc.html, Main.dc.html

| 필드 | 타입 | 필수 | 근거 |
|---|---|---|---|
| plan_id | number | 예 | BE. "계획 11" |
| title | string | 예 | BE. "계산기 웹 서비스 개발 전 문서 6종 작성 …" |
| request | string | 예 (조회만) | BE `GET /api/plans/{id}`. PlanGraph.dc.html "명령서 보기" (md) |
| persona_ids | number[] | 예 | BE. PlanGraph.dc.html "dankim-persona" |
| status | PlanStatus | 예 | BE. "● 완료" |
| created_at | string | 예 | BE. "2026-11-20 13:16" (UTC 를 사용자 시간대로) |
| nodes | PlanNode[] | 예 (조회만) | BE. PlanGraph.dc.html 그래프 |
| edges | PlanEdge[] | 예 (조회만) | BE. PlanGraph.dc.html 그래프 선 |
| node_counts | NodeCounts | 예 (목록만) | BE `GET /api/plans`. Plans.dc.html "10/10", "6/9 (실패 1)" |

관계: Plan → Persona (persona_ids). 노드와 간선은 조회 응답에 중첩으로 온다 (화면이 한 덩어리로 보인다).
목록 한 줄(PlanSummary)과 조회(PlanDetail)는 필드가 다르므로 화면 타입도 둘로 둔다.

### PlanNode (노드)
계획의 작업 하나 — PlanGraph.dc.html

| 필드 | 타입 | 필수 | 근거 |
|---|---|---|---|
| node_id | number | 예 | BE. 노드 상자 "49" |
| title | string | 예 | BE. "도메인 문서 작성" |
| kind | NodeKind | 예 | BE. "document", 확인 노드는 "hitl" |
| persona_ids | number[] | 예 | BE. "담당 dankim-persona". 확인 노드는 보통 빈 목록 |
| output_spec | string | 예 | BE. 패널의 하는 일 · 산출물 · 그 외 설명 (md 하나. 화면이 절로 나눈다) |
| status | PlanNodeStatus | 예 | BE. "● 완료" |

관계: PlanNode → Persona (persona_ids). 앞 노드·뒤 노드는 PlanEdge 에서 계산한다.

### PlanEdge (간선)
앞 노드가 끝나야 뒤 노드를 시작한다 — PlanGraph.dc.html

| 필드 | 타입 | 필수 | 근거 |
|---|---|---|---|
| edge_id | number | 예 | BE |
| from_node_id | number | 예 | BE. 패널 "받는 산출물 (앞 노드)" |
| to_node_id | number | 예 | BE. 패널 "넘기는 곳 (뒤 노드)" |

## 값 타입

### MemorySource (근거)
사용자가 한 말과 그 말이 나온 계획 — MemoryDetail.dc.html

| 필드 | 타입 | 필수 |
|---|---|---|
| quote | string | 예 |
| plan_id | number | 예 |

### NodeCounts (상태별 노드 수)
계획 목록의 노드 열 — Plans.dc.html, Main.dc.html

| 필드 | 타입 | 필수 |
|---|---|---|
| todo | number | 예 |
| running | number | 예 |
| done | number | 예 |
| failed | number | 예 |
| skipped | number | 예 |
| total | number | 예 |

### NodeSpecSections (정의서의 절)
노드 패널이 output_spec md 에서 나눠 보이는 것. 저장하지 않는다 — PlanGraph.dc.html

| 필드 | 타입 | 필수 |
|---|---|---|
| does | string | 예 (없으면 "") |
| output_form | string | 예 (없으면 "") |
| output_contents | string | 예 (없으면 "") |
| notes | string | 예 (없으면 "") |

나누는 규칙은 CLI 의 NodeSpec 과 같다: `### 하는 일`, `### 산출물` (첫 줄이 `- 형태: ` 면 형태), `### 그 외 설명`. "(정하지 않음)", "(없음)" 은 빈 값.

## 기능 데이터 (enum)

값은 BE 의 소문자 값 (BE), 라벨은 화면 문구.

### PlanStatus — Main.dc.html, Plans.dc.html, PlanGraph.dc.html
- 쓰는 곳: Plan.status

| 값 | 라벨 |
|---|---|
| drafting | 만드는 중 |
| reviewing | 검토 중 |
| approved | 승인 |
| rejected | 불허 |
| running | 실행 중 |
| done | 완료 |

### PlanNodeStatus — PlanGraph.dc.html
- 쓰는 곳: PlanNode.status

| 값 | 라벨 |
|---|---|
| todo | 할 일 |
| running | 실행 중 |
| done | 완료 |
| failed | 실패 |
| skipped | 건너뜀 |

### NodeKind — PlanGraph.dc.html
- 쓰는 곳: PlanNode.kind

| 값 | 라벨 |
|---|---|
| document | document |
| research | research |
| code | code |
| hitl | 확인 |

### MemoryKind — Main.dc.html, Memories.dc.html, MemoryDetail.dc.html
- 쓰는 곳: Memory.kind

| 값 | 라벨 |
|---|---|
| knowledge | 지식 |
| attitude | 태도 |
| plan | 계획 |

## 기능 데이터 (저장)

없음. 화면 안 상태(고른 노드, 명령서 펼침, 폼, 지우기 확인)는 페이지 단계에서 `useState` 로 둔다. 서버에 저장하는 것은 위 도메인뿐이다.
