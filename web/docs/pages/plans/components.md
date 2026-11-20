# plans 컴포넌트

라우트: /plans
화면: Plans.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 스스로 정함)

## 영역

- A 위 메뉴: 계획 선택됨
- B 제목 줄: "계획", "최근 것부터 (만든 시각 기준) · 1개"
- C 계획 표: 머리(계획, 제목, 상태, 노드, 만든 시각)와 계획 줄. 제목을 누르면 그래프로
- D 상태 기호 설명: 한 줄

## 공용 컴포넌트 사용

| 영역 | 컴포넌트 | 쓰는 props | 비고 |
|---|---|---|---|
| A | layout/AppHeader | current="plans" | 그대로 사용 |
| B | ui/PageHeading | title "계획", meta "최근 것부터 (만든 시각 기준) · n개" | 그대로 사용 |
| C | ui/Table, ui/TableHeaderCell, ui/TableRow, ui/TableCell(tone) | minWidth 760 | 그대로 사용 |
| C | ui/TextLink | href /plans/{id}, 제목 | 그대로 사용 |
| C | plan/PlanStatusMark, plan/NodeProgress | status, counts | 그대로 사용 (home 에서 만듦) |
| C | ui/EmptyState | "아직 계획이 없습니다." | 계획이 없을 때 |

## 추가 컴포넌트

| 이름 | 위치 | props | 안에 쓰는 공용 컴포넌트 | 근거 |
|---|---|---|---|---|
| PlanTableRow | src/components/plan/PlanTableRow.tsx | plan: PlanSummary | ui/TableRow, ui/TableCell, ui/TextLink, plan/PlanStatusMark, plan/NodeProgress | Plans.dc.html C. 계획마다 반복되는 표의 줄 |

본문에 두는 것: D 상태 기호 설명 한 줄 (한 번만 나온다).

## 공용 승격 후보 (사용자 판단 필요)

없음.

## 기존 컴포넌트 수정 필요 (사용자 판단 필요)

없음.
