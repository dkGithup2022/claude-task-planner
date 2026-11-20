# memory-detail 데이터

화면: MemoryDetail.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 BE 스펙을 근거로 스스로 정함)

영역: 위 메뉴 / "← 지식 목록" / 머리 (지식 #n, 작업 이름, 종류·페르소나·덧붙임 수, [수정] [삭제]) / 지우기 확인 / 수정 폼 / 본문 (덧붙임 n 구분선으로 나눔) / 근거 (인용과 계획 링크)

## 공용 데이터 (스펙 그대로 사용)

| 항목 | 위치 | 쓰는 필드 | 쓰는 영역 |
|---|---|---|---|
| MemoryDetail | src/types/data/domain/memory.ts | memory_id, kind, theme, body, persona_ids, source | 머리, 본문, 근거, 수정 폼 |
| MemorySource | src/types/data/domain/memory-source.ts | quote, plan_id | 근거 |
| MemoryKind | src/types/data/domain/memory.ts | MEMORY_KIND_LABEL | 머리, 수정 폼 |
| Persona | src/types/data/domain/persona.ts | persona_id, name | 머리, 수정 폼의 고르기 |

## 스펙 부족

없음.

## API 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| MemoryDetailResponse | src/types/api/memory.ts | MemoryDetail 그대로 | GET /api/memories/{id} |
| MemoryUpdateRequest | src/types/api/memory.ts | kind?, theme?, body?, persona_ids?, source? (바꿀 필드만) | PATCH /api/memories/{id}. 웹은 kind, theme, body, persona_ids 를 보낸다 |
| MemoryIdResponse | src/types/api/memory.ts | memory_id: number | PATCH 응답 |
| PlanListResponse | src/types/api/plan.ts (있음) | plans | 근거의 계획이 서버에 있는지 ("계획 3 (서버에 없음)") |

## 페이지 전용 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| MemoryEditValues | src/components/memory/MemoryEditForm.types.ts | theme, kind, personaIds: number[], body | 수정 폼의 입력값 (폼 컴포넌트가 갖는다) |

계산값: 본문을 덧붙임 머리 `****** KNOWLEDGE APPENDED <n> ********` 로 나눈 조각 — `src/lib/memory-body.ts`

## 애매한 것 (사용자 판단 필요)

없음.
