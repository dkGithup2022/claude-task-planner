# personas API

라우트: /personas
화면: Personas.dc.html
입력: docs/pages/personas/data.md, components.md
작성: 2026-11-20
상태: 구현됨. 검수 완료 — 모두 이미 구현된 BE API (be/specs/api.md)

## 목록

| # | 종류 | 이름 | 트리거 | 상태 |
|---|---|---|---|---|
| 1 | 도메인 CRUD | 페르소나 목록 | 진입, 쓰기 뒤 | 있음 (fetchPersonas) |
| 2 | 도메인 CRUD | 페르소나 만들기 | 만들기 폼 [만들기] | 있음 (createPersona) |
| 3 | 도메인 CRUD | 페르소나 고치기 | 수정 폼 [저장] | 있음 (updatePersona) |
| 4 | 도메인 CRUD | 페르소나 지우기 | [삭제] | 있음 (deletePersona) |
| 5 | 페이지 동작 | 줄 펼치기, 폼 열고 닫기, "이 페르소나의 지식 →" | 누르기 | API 아님 (/memories?persona_id={id}) |

## 1. 도메인 CRUD

### POST /api/personas
- 요청 name (1~255자), description (빈 값 허용). 응답 201 persona_id
- 오류: 같은 이름 409, 빈 이름 400 → 토스트로 서버 문구

### PATCH /api/personas/{persona_id}
- 요청 name?, description?. 응답 200 persona_id
- 오류: 없으면 404, 다른 페르소나와 이름이 같으면 409, 빈 이름 400 → 토스트

### DELETE /api/personas/{persona_id}
- 응답 204
- 오류: 쓰는 지식·계획이 있으면 409 "지식 n개, 계획 m개가 이 페르소나를 씁니다" → 펼친 줄 안에 Notice "지울 수 없습니다. {서버 문구}" (가안). 확인 창 없이 바로 부른다 — 쓰이는 페르소나는 서버가 막고, 안 쓰이는 페르소나는 지워도 잃는 것이 이름과 설명뿐이다

## 결정 필요

없음.
