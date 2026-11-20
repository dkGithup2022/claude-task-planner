# memories 데이터

화면: Memories.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 BE 스펙을 근거로 스스로 정함)

영역: 위 메뉴(지식) / 제목 "지식" / 검색 줄 (검색어, 종류, 페르소나) / "n개 · 고친 시각 최근 것부터" / 지식 표 (#, 종류, 작업 이름, 페르소나, 덧붙임, 근거 계획)

## 공용 데이터 (스펙 그대로 사용)

| 항목 | 위치 | 쓰는 필드 | 쓰는 영역 |
|---|---|---|---|
| MemoryListItem | src/types/data/domain/memory.ts | memory_id, kind, theme, persona_ids, appended_count, source_plan_ids | 지식 표 |
| MemoryKind | src/types/data/domain/memory.ts | MEMORY_KIND_LABEL | 종류 열, 종류 필터 |
| Persona | src/types/data/domain/persona.ts | persona_id, name | 페르소나 열, 페르소나 필터 |

## 스펙 부족

없음.

## API 데이터

이미 있다. MemoryListParams (q, kind, persona_id), MemoryListResponse (items, total), PersonaListResponse.

## 페이지 전용 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| MemoryFilter | src/app/memories/memories.types.ts | q: string, kind: MemoryKind \| "", personaId: number \| null | 검색 줄의 값. 주소 쿼리(?q=&kind=&persona_id=)와 같게 둔다 (페르소나 화면의 "이 페르소나의 지식 →" 이 ?persona_id=1 로 들어온다) |

## 애매한 것 (사용자 판단 필요)

없음.
