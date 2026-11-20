# memories 제작 계획

라우트: /memories
화면: Memories.dc.html
입력: docs/pages/memories/data.md, components.md, api.md
작성: 2026-11-20
상태: 제작 완료 (2026-11-20). 허가 (사용자 지시에 따라 스스로)

## 1. 충돌 검사

없음. MemoryTableRow 만 새로 만든다.

## 2. 구조

파일: src/app/memories/page.tsx, MemoriesClient.tsx, MemoriesSkeleton.tsx, loading.tsx, memories.types.ts

```
MemoriesClient
├── layout/AppHeader current="memories"
├── ui/PageHeading "지식"
├── 검색 줄: ui/TextField(search) + ui/SelectField 종류 + ui/SelectField 페르소나
└── 개수 줄 + ui/Table > memory/MemoryTableRow × n | ui/EmptyState
```

상태: filter (MemoryFilter, 주소 쿼리에서 시작), result, personas, failed

| 동작 | 트리거 | 결과 | 부르는 것 |
|---|---|---|---|
| 읽기 | 진입, 조건 바꾸기 (300ms 뒤) | 표와 개수, 주소 쿼리 바꿈 | fetchMemories |
| 페르소나 읽기 | 진입 | 필터 선택지와 이름 | fetchPersonas |
| 작업 이름 누르기 | 링크 | /memories/{id} | 없음 |

## 3. 정하지 않은 UI 세부

| 항목 | 정한 값 | 이유 |
|---|---|---|
| 검색 시점 | 입력이 멈추고 300ms 뒤, 고르기도 같은 흐름 | 가안에 버튼이 없다 |
| 빈 결과 | EmptyState "조건에 맞는 지식이 없습니다." | 가안에 없음 |

## 4. 제작에 필요한 판단

- API: 모두 있음. 페르소나 화면의 "이 페르소나의 지식 →" 이 /memories?persona_id={id} 로 들어오므로 필터를 주소 쿼리와 맞춘다

## 5. 와이어프레임

생략 (가안 아트보드로 대신, 만든 뒤 화면 대조).

## 6. 제작 기록 (2026-11-20)

- 만든 파일: 위 5개 + components/memory/MemoryTableRow
- 화면 대조 (ego-browser, 1440px, 실제 서버): docs/pages/memories/build.png. 가안과 같은 열과 검색 줄
- 확인: "기획" 입력 → 주소 ?q=기획, 1개. /memories?persona_id=2 → 페르소나 고르기에 be-developer, 지식 #2 한 줄
