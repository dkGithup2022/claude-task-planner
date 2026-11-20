# plans API

라우트: /plans
화면: Plans.dc.html
입력: docs/pages/plans/data.md, docs/pages/plans/components.md
작성: 2026-11-20
상태: 구현됨. 검수 완료 — 이미 있는 웹 API 함수(home 에서 만듦)와 BE API 를 그대로 쓴다. 새로 정할 것이 없다

## 목록

| # | 종류 | 이름 | 트리거 | 상태 |
|---|---|---|---|---|
| 1 | 도메인 CRUD | 계획 목록 읽기 (전부) | 진입 | 있음 (lib/plan-api.ts fetchPlans) |
| 2 | 페이지 동작 | 제목 누르기 | 링크 | API 아님 |

## 1. 도메인 CRUD

### GET /api/plans — 계획 목록
- 목적: 모든 계획을 만든 시각 최근 순으로 보인다 (실행 이력 겸 계획 목록)
- 동작: 조건 없이 부른다. 계획마다 상태별 노드 수가 온다
- 인증: 불필요
- 상태: 있음 (fetchPlans)

요청 `PlanListParams`: 없음 (status, limit 을 넘기지 않는다)

응답 `PlanListResponse`

| 필드 | 타입 | 뜻 · 화면 어디에 |
|---|---|---|
| plans | PlanSummary[] | 계획 표의 줄 |

## 2. 페이지 안 동작

| 이름 | 트리거 | 무엇이 바뀌는지 | 나중에 API 가 될 수 있는가 |
|---|---|---|---|
| 제목 누르기 | 링크 | /plans/{plan_id} 로 이동 | 아니오 |

## 3. 유즈케이스

없음.

## 결정 필요

없음. 계획이 많아지면 쪽 나누기가 필요할 수 있다. 지금 BE 는 limit 만 있다 (나중에 정할 일로 둔다).
