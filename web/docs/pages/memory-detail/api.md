# memory-detail API

라우트: /memories/[id]
화면: MemoryDetail.dc.html
입력: docs/pages/memory-detail/data.md, components.md
작성: 2026-11-20
상태: 검수 완료 — 모두 이미 구현된 BE API 를 그대로 쓴다. 웹의 수정 범위(kind, theme, body, persona_ids)는 사용자가 웹 UI 문서에서 정했다 ("b")

## 목록

| # | 종류 | 이름 | 트리거 | 상태 |
|---|---|---|---|---|
| 1 | 도메인 CRUD | 지식 조회 | 진입, 저장 뒤 | 새로 필요 (웹) |
| 2 | 도메인 CRUD | 지식 고치기 | 수정 폼 [저장] | 새로 필요 (웹) |
| 3 | 도메인 CRUD | 지식 지우기 | 확인 창 [지우기] | 새로 필요 (웹) |
| 4 | 도메인 CRUD | 페르소나 목록 | 진입 | 있음 (fetchPersonas) |
| 5 | 도메인 CRUD | 계획 목록 (근거 계획이 있는지) | 진입 | 있음 (fetchPlans) |
| 6 | 페이지 동작 | 수정 폼 열고 닫기, 지우기 확인 열고 닫기, 근거의 계획 누르기 | 버튼, 링크 | API 아님 |

## 1. 도메인 CRUD

### GET /api/memories/{memory_id} — 지식 조회
- 동작: 지식 하나 (본문, 근거 포함). 없으면 404
- 인증: 불필요. 응답 MemoryDetailResponse

### PATCH /api/memories/{memory_id} — 지식 고치기
- 동작: 보낸 필드만 받은 그대로 저장. 고친 시각이 바뀐다. 웹은 작업 이름, 종류, 페르소나, 본문을 보낸다. 근거는 보내지 않는다 (CLI 의 덧붙이기만 근거를 바꾼다)
- 오류: 없으면 404, 빈 작업 이름·본문 400, 없는 페르소나 400 (서버 메시지를 그대로 보인다)
- 요청 MemoryUpdateRequest, 응답 MemoryIdResponse

### DELETE /api/memories/{memory_id} — 지식 지우기
- 동작: 지운다. 응답 204. 없으면 404. 지운 뒤 /memories 로 간다

## 3. 유즈케이스

없음.

## 결정 필요

없음.
