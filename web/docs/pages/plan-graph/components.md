# plan-graph 컴포넌트

라우트: /plans/[id]
화면: PlanGraph.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 스스로 정함)

## 영역

- A 위 메뉴 (계획 선택됨)
- B 계획 요약: "계획 11 {제목}", "● 완료 · 2026-11-20 13:16 · dankim-persona", "완료 10 · 실행 중 0 · 할 일 0", 다시 읽기 안내, [명령서 보기 ▾] 와 펼친 명령서
- C 그래프: React Flow. 층으로 놓은 노드 상자, 간선 화살표, 확대·축소, 상태 기호 설명
- D 노드 패널: 노드 번호·제목·상태·종류·담당, 받는 산출물(앞 노드)·넘기는 곳(뒤 노드) 각 상태와 이동, 하는 일·산출물·그 외 설명

## 공용 컴포넌트 사용

| 영역 | 컴포넌트 | 쓰는 props | 비고 |
|---|---|---|---|
| A | layout/AppHeader | current="plans" | 그대로 |
| B | ui/Button | variant outline, size sm | 명령서 보기/접기 |
| B, D | ui/MarkdownText | 명령서, 정의서의 절 | 이번에 공용으로 더함 (components-plan.md) |
| B, C, D | plan/PlanStatusMark, plan/NodeStatusMark | status | 그대로 |
| 오류 | ui/Notice | 없는 계획, 불러오기 실패 | 그대로 |

## 추가 컴포넌트

| 이름 | 위치 | props | 안에 쓰는 공용 컴포넌트 | 근거 |
|---|---|---|---|---|
| PlanSummaryHeader | src/components/plan/PlanSummaryHeader.tsx | plan: PlanDetail, personaNames: string[], autoRefresh: boolean | ui/Button, ui/MarkdownText, plan/PlanStatusMark | PlanGraph.dc.html B. 계획 한 개의 요약 덩어리 |
| PlanGraphNode | src/components/plan/PlanGraphNode.tsx | React Flow 노드 data: { node: PlanNode, selected: boolean } | plan/NodeStatusMark | PlanGraph.dc.html C. 노드 상자가 반복. 상태별 테두리, 확인 노드 이중 테두리 |
| PlanGraphView | src/components/plan/PlanGraphView.tsx | plan: PlanDetail, selectedNodeId, onSelect(nodeId) | PlanGraphNode | PlanGraph.dc.html C. React Flow 와 층 배치를 감싼다 |
| NodeDetailPanel | src/components/plan/NodeDetailPanel.tsx | plan: PlanDetail, node: PlanNode, personaNames: Map, onSelect(nodeId) | ui/MarkdownText, plan/NodeStatusMark | PlanGraph.dc.html D |

## 공용 승격 후보 (사용자 판단 필요)

없음. MarkdownText 는 지식 조회 화면도 쓰므로 처음부터 ui 에 둔다.

## 기존 컴포넌트 수정 필요 (사용자 판단 필요)

없음.
