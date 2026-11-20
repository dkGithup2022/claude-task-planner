# home API

라우트: /
화면: Main.dc.html
입력: docs/pages/home/data.md, docs/pages/home/components.md
작성: 2026-11-20
상태: 구현됨 (fe-generate-api, 2026-11-20). 검수 완료. 모두 이미 구현된 BE API(`../be/specs/api.md`)를 그대로 쓴다. 새 엔드포인트도, BE 와 다른 점도 없어 사용자 지시("API 데이터 관련만 질문")에 따라 묻지 않고 확정했다

"새로 필요" 는 웹 쪽 코드(types/api, mock, lib/*-api.ts)가 아직 없다는 뜻이다. 서버는 이미 있다.

## 목록

| # | 종류 | 이름 | 트리거 | 상태 |
|---|---|---|---|---|
| 1 | 도메인 CRUD | 계획 목록 읽기 (상태별·최근) | 진입 | 있음 (lib/plan-api.ts fetchPlans) |
| 2 | 도메인 CRUD | 지식 목록 읽기 (최근·종류별 개수) | 진입 | 있음 (lib/memory-api.ts fetchMemories) |
| 3 | 페이지 동작 | 계획 줄·지식 줄·전체 보기 누르기 | 링크 | API 아님 |

## 1. 도메인 CRUD

### GET /api/plans — 계획 목록
- 목적: 실행 중인 계획, 확정을 기다리는 계획, 최근 계획 5개를 보인다
- 동작: 지우지 않은 계획을 만든 시각 최근 순으로 돌려준다. 계획마다 지우지 않은 노드의 상태별 수를 담는다. 메인은 세 번 부른다: `status=running`, `status=reviewing`, `limit=5`
- 인증: 불필요 (이 서비스에는 로그인이 없다)
- 상태: 있음 (fetchPlans, mock getPlanList)

요청 `PlanListParams`

| 위치 | 이름 | 타입 | 필수 | 뜻 · 근거 |
|---|---|---|---|---|
| query | status | PlanStatus | 아니오 | 이 상태의 계획만. Main.dc.html "실행 중인 계획", "확정을 기다리는 계획" |
| query | limit | number (1~200) | 아니오 | 최대 개수. Main.dc.html "최근 계획" 5개 |

응답 `PlanListResponse`

| 필드 | 타입 | 뜻 · 화면 어디에 |
|---|---|---|
| plans | PlanSummary[] | 계획 줄 (plan_id, title, status, persona_ids, created_at, node_counts) |

### GET /api/memories — 지식 목록
- 목적: 최근 지식 5개와 지식 종류별 개수를 보인다
- 동작: 지우지 않은 지식을 고친 시각 최근 순으로 돌려준다. total 은 limit 을 뺀 조건에 맞는 개수. 메인은 `limit=5` 한 번과 종류마다 `kind=…&limit=1` 세 번 (total 만 쓴다)
- 인증: 불필요
- 상태: 있음 (fetchMemories, mock getMemoryList)

요청 `MemoryListParams`

| 위치 | 이름 | 타입 | 필수 | 뜻 · 근거 |
|---|---|---|---|---|
| query | q | string | 아니오 | 작업 이름·본문 검색어 (메인은 안 씀) |
| query | kind | MemoryKind | 아니오 | Main.dc.html "지식 3 · 태도 0 · 계획 4" |
| query | persona_id | number | 아니오 | (메인은 안 씀) |
| query | limit | number (1~200) | 아니오 | Main.dc.html 최근 지식 5개 |

응답 `MemoryListResponse`

| 필드 | 타입 | 뜻 · 화면 어디에 |
|---|---|---|
| items | MemoryListItem[] | 최근 지식 줄 (memory_id, theme, kind, edited, updated_at) |
| total | number | "지식 전체 7개", 종류별 개수 |

## 2. 페이지 안 동작

| 이름 | 트리거 | 무엇이 바뀌는지 | 나중에 API 가 될 수 있는가 |
|---|---|---|---|
| 계획 줄 누르기 | 줄 링크 | /plans/{plan_id} 로 이동 | 아니오 |
| 지식 줄 누르기 | 줄 링크 | /memories/{memory_id} 로 이동 | 아니오 |
| 전체 보기 | 링크 | /plans, /memories 로 이동 | 아니오 |

## 3. 유즈케이스

없음.

## 결정 필요

없음. 종류별 개수를 세는 API 가 서버에 따로 없어 목록 API 를 종류마다 부른다 (요청 3번, 응답은 한 줄씩).
