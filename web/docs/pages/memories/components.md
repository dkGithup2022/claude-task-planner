# memories 컴포넌트

라우트: /memories
화면: Memories.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 스스로 정함)

## 영역

- A 위 메뉴 (지식 선택됨)
- B 제목 "지식"
- C 검색 줄: 검색어 입력, 종류 고르기(전체·지식·태도·계획), 페르소나 고르기(전체·이름들)
- D 개수 줄과 지식 표. 줄의 작업 이름을 누르면 지식 조회로

## 공용 컴포넌트 사용

| 영역 | 컴포넌트 | 쓰는 props | 비고 |
|---|---|---|---|
| A | layout/AppHeader | current="memories" | 그대로 |
| B | ui/PageHeading | title "지식" | 그대로 |
| C | ui/TextField (type search), ui/SelectField × 2 | label, value, onChange | 그대로 |
| D | ui/Table, TableHeaderCell, TableRow, TableCell, TextLink | | 그대로 |
| D | ui/EmptyState | "조건에 맞는 지식이 없습니다." | 그대로 |

## 추가 컴포넌트

| 이름 | 위치 | props | 안에 쓰는 공용 컴포넌트 | 근거 |
|---|---|---|---|---|
| MemoryTableRow | src/components/memory/MemoryTableRow.tsx | memory: MemoryListItem, personaNames: Map<number, string> | ui/TableRow, TableCell, TextLink | Memories.dc.html D. 지식마다 반복되는 줄 |

## 공용 승격 후보 (사용자 판단 필요)

없음.

## 기존 컴포넌트 수정 필요 (사용자 판단 필요)

없음.
