# memory-detail 컴포넌트

라우트: /memories/[id]
화면: MemoryDetail.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 스스로 정함)

## 공용 컴포넌트 사용

| 영역 | 컴포넌트 | 쓰는 props | 비고 |
|---|---|---|---|
| 메뉴 | layout/AppHeader | current="memories" | 그대로 |
| 뒤로 | ui/TextLink | "← 지식 목록", tone secondary | 그대로 |
| 머리 | ui/Button | 수정(primary), 삭제(outline) | 그대로 |
| 지우기 확인 | ui/Notice + ui/Button(subtle 취소, primary 지우기) | | 그대로 |
| 본문 | ui/MarkdownText, ui/LabeledDivider "덧붙임 n" | | 그대로 |
| 수정 폼 | ui/TextField, ui/SelectField, ui/Checkbox, ui/TextAreaField, ui/Button | | 그대로 |
| 오류 | ui/Notice | 없는 지식, 실패 | 그대로 |

## 추가 컴포넌트

| 이름 | 위치 | props | 안에 쓰는 공용 컴포넌트 | 근거 |
|---|---|---|---|---|
| MemoryBody | src/components/memory/MemoryBody.tsx | body: string | ui/MarkdownText, ui/LabeledDivider | 본문을 덧붙임 구분선으로 나눠 보인다 |
| MemorySourceList | src/components/memory/MemorySourceList.tsx | source: MemorySource[], existingPlanIds: Set<number> | ui/TextLink | 근거 목록. 서버에 없는 계획은 링크 대신 "(서버에 없음)" |
| MemoryEditForm | src/components/memory/MemoryEditForm.tsx | memory: MemoryDetail, personas: Persona[], saving: boolean, onSave(values), onCancel() | ui/TextField, SelectField, Checkbox, TextAreaField, Button | 수정 폼 덩어리 (입력값 상태를 안에 둔다) |

## 공용 승격 후보 / 기존 컴포넌트 수정 필요

없음.
