# plan-graph API

라우트: /plans/[id]
화면: PlanGraph.dc.html
입력: docs/pages/plan-graph/data.md, docs/pages/plan-graph/components.md
작성: 2026-11-20
상태: 검수 완료 — 모두 이미 있는 BE API 를 그대로 쓴다. 새 엔드포인트와 BE 와 다른 점이 없다

## 목록

| # | 종류 | 이름 | 트리거 | 상태 |
|---|---|---|---|---|
| 1 | 도메인 CRUD | 계획 조회 (노드·간선 포함) | 진입, 실행 중이면 10초마다 | 새로 필요 (웹) |
| 2 | 도메인 CRUD | 페르소나 목록 (이름) | 진입 | 새로 필요 (웹) |
| 3 | 페이지 동작 | 노드 고르기, 앞뒤 노드로 이동, 명령서 펼치기, 확대·축소 | 클릭 | API 아님 |

## 1. 도메인 CRUD

### GET /api/plans/{plan_id} — 계획 조회
- 목적: 계획 요약, 그래프, 노드 패널을 그린다
- 동작: 계획과 지우지 않은 노드(node_id 순)·간선(edge_id 순)을 돌려준다. 없으면 404
- 인증: 불필요
- 상태: 새로 필요 (웹)

요청: path plan_id (number)

응답 `PlanDetailResponse` = PlanDetail (plan_id, title, request, persona_ids, status, created_at, nodes[], edges[])

### GET /api/personas — 페르소나 목록
- 목적: 참여·담당 페르소나 id 를 이름으로 바꾼다
- 동작: 지우지 않은 페르소나 전부 (persona_id 순, 지식 수·계획 수 포함)
- 인증: 불필요
- 상태: 새로 필요 (웹)

응답 `PersonaListResponse`: personas: Persona[]

## 2. 페이지 안 동작

| 이름 | 트리거 | 무엇이 바뀌는지 | 나중에 API 가 될 수 있는가 |
|---|---|---|---|
| 노드 고르기 | 노드 상자, 패널의 앞뒤 노드 | selectedNodeId | 아니오 |
| 명령서 펼치기 | 버튼 | showRequest | 아니오 |
| 다시 읽기 | 실행 중인 계획이면 10초마다 | 계획 조회를 다시 부른다 | 이미 API (1번) |

## 3. 유즈케이스

없음. 웹은 계획을 고치지 않는다 (웹 UI 문서 1번 화면은 보기만).

## 결정 필요

없음.
