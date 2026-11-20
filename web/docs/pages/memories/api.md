# memories API

라우트: /memories
화면: Memories.dc.html
입력: docs/pages/memories/data.md, components.md
작성: 2026-11-20
상태: 구현됨. 검수 완료 — 이미 있는 웹 API 함수와 BE API 를 그대로 쓴다

## 목록

| # | 종류 | 이름 | 트리거 | 상태 |
|---|---|---|---|---|
| 1 | 도메인 CRUD | 지식 목록 (검색어·종류·페르소나) | 진입, 조건 바꾸기 | 있음 (lib/memory-api.ts fetchMemories) |
| 2 | 도메인 CRUD | 페르소나 목록 (필터와 이름) | 진입 | 있음 (lib/persona-api.ts fetchPersonas) |
| 3 | 페이지 동작 | 조건 바꾸기 (주소 쿼리도 바꿈), 작업 이름 누르기 | 입력·고르기·링크 | API 아님 |

## 1. 도메인 CRUD

### GET /api/memories — 지식 목록
- 목적: 검색어(작업 이름·본문), 종류, 페르소나로 거른 지식을 고친 시각 최근 순으로
- 동작: 조건이 바뀔 때마다 다시 부른다. 검색어는 입력이 멈추고 300ms 뒤에 부른다
- 인증: 불필요. 상태: 있음

요청: q?, kind?, persona_id? (limit 없음 — 전부)
응답: items (MemoryListItem[]), total

### GET /api/personas — 페르소나 목록
- 목적: 페르소나 필터의 선택지와 표의 이름. 상태: 있음

## 2. 페이지 안 동작

| 이름 | 트리거 | 무엇이 바뀌는지 | 나중에 API 가 될 수 있는가 |
|---|---|---|---|
| 조건 바꾸기 | 입력, 고르기 | 필터 상태와 주소 쿼리 | 이미 API (1번) |
| 작업 이름 누르기 | 링크 | /memories/{id} | 아니오 |

## 3. 유즈케이스

없음.

## 결정 필요

없음.
