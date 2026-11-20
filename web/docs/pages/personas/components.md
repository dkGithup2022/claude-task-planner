# personas 컴포넌트

라우트: /personas
화면: Personas.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 스스로 정함)

## 공용 컴포넌트 사용

| 영역 | 컴포넌트 | 쓰는 props | 비고 |
|---|---|---|---|
| 메뉴 | layout/AppHeader | current="personas" | 그대로 |
| 제목 | ui/PageHeading | title, actions=[+ 새 페르소나] | 그대로 |
| 표 | ui/Table, TableHeaderCell, TableRow(selected), TableCell | | 그대로 |
| 펼친 줄 | ui/Button, ui/TextLink, ui/Notice | | 그대로 |
| 폼 | ui/TextField, ui/TextAreaField, ui/Button | | 그대로 |

## 추가 컴포넌트

| 이름 | 위치 | props | 안에 쓰는 공용 컴포넌트 | 근거 |
|---|---|---|---|---|
| PersonaForm | src/components/persona/PersonaForm.tsx | initial?: PersonaFormValues, submitLabel, saving, onSubmit(values), onCancel() | ui/TextField, ui/TextAreaField, ui/Button | 만들기와 수정이 같은 폼 |
| PersonaDetail | src/components/persona/PersonaDetail.tsx | persona, editing, saving, blockedMessage, onEdit, onCancelEdit, onSave(values), onDelete | ui/Button, ui/TextLink, ui/Notice, PersonaForm | 펼친 줄 안의 상세 |

## 공용 승격 후보 / 기존 컴포넌트 수정 필요

없음.
