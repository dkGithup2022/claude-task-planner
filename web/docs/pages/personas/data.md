# personas 데이터

화면: Personas.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 BE 스펙을 근거로 스스로 정함)

영역: 위 메뉴 / 제목 "페르소나" + [+ 새 페르소나] / 만들기 폼 / 페르소나 표 (#, 이름, 설명, 지식 수, 계획 수) / 펼친 줄 (수정·삭제, 이름·설명 또는 수정 폼, "이 페르소나의 지식 →", 지우기 거절 알림) / 설명 문구

## 공용 데이터 (스펙 그대로 사용)

| 항목 | 위치 | 쓰는 필드 | 쓰는 영역 |
|---|---|---|---|
| Persona | src/types/data/domain/persona.ts | persona_id, name, description, memory_count, plan_count | 표, 펼친 줄, 수정 폼 |

## 스펙 부족

없음.

## API 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| PersonaListResponse | src/types/api/persona.ts (있음) | personas | 표 |
| PersonaCreateRequest | src/types/api/persona.ts | name: string, description: string | POST /api/personas |
| PersonaUpdateRequest | src/types/api/persona.ts | name?, description? | PATCH /api/personas/{id} |
| PersonaIdResponse | src/types/api/persona.ts | persona_id: number | POST·PATCH 응답 |

## 페이지 전용 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| PersonaFormValues | src/components/persona/PersonaForm.types.ts | name, description | 만들기·수정 폼 입력값 |

화면 상태(펼친 페르소나, 만들기 폼 열림, 수정 중, 지우기 거절 문구)는 useState.

## 애매한 것 (사용자 판단 필요)

없음.
