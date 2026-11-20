# home 컴포넌트

라우트: /
화면: Main.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 스스로 정함)

## 영역

- A 위 메뉴: 서비스 이름, 계획 · 지식 · 페르소나
- B 실행 중인 계획: 계획 줄 목록 (번호, 제목, 상태, "완료 6 / 10" 또는 "6/9 (실패 1)"), 없으면 빈 상태
- C 확정을 기다리는 계획: 계획 줄 목록 (번호, 제목, 상태, "노드 7"), 없으면 빈 상태
- D 최근 계획: 구역 제목과 "전체 보기 →", 계획 줄 5개 (번호, 제목, 상태, 노드 수, 만든 시각)
- E 최근 지식: 구역 제목과 "전체 보기 →", 지식 줄 5개 (번호, 작업 이름, 종류, 새로 저장/고침, 고친 시각)
- F 지식 개수: "지식 전체 7개 (지식 3 · 태도 0 · 계획 4)"

## 공용 컴포넌트 사용

| 영역 | 컴포넌트 | 쓰는 props | 비고 |
|---|---|---|---|
| A | layout/AppHeader | current 없음 | 그대로 사용 |
| B, C, D, E | ui/SectionHeader | title, action=ui/TextLink("전체 보기 →", tone secondary) | 그대로 사용 |
| B, C | ui/EmptyState | children "실행 중인 계획이 없습니다." / "검토 중인 계획이 없습니다." | 그대로 사용 |
| B, C, D | plan/PlanStatusMark | status | 그대로 사용 |

## 추가 컴포넌트

| 이름 | 위치 | props | 안에 쓰는 공용 컴포넌트 | 근거 |
|---|---|---|---|---|
| PlanListRow | src/components/plan/PlanListRow.tsx | plan: PlanSummary, show: "progress" \| "node_total" \| "created" (오른쪽 끝 칸) | plan/PlanStatusMark, plan/NodeProgress | Main.dc.html B·C·D. 같은 모양이 세 구역에 반복. 누르면 /plans/{id} |
| NodeProgress | src/components/plan/NodeProgress.tsx | counts: NodeCounts | — | Main.dc.html B·D "완료 6 / 10", "6/9 (실패 1)". 계획 목록 화면(Plans.dc.html)의 노드 열과 같은 표기 |
| RecentMemoryRow | src/components/memory/RecentMemoryRow.tsx | memory: MemoryListItem | — | Main.dc.html E. 5번 반복. 누르면 /memories/{id} |

본문에 두는 것: 영역 F 한 줄 (한 번만 나온다).

## 공용 승격 후보 (사용자 판단 필요)

없음. NodeProgress 는 계획 목록 화면에서도 쓰지만 계획 도메인 표기라 `components/plan/` 에 둔다 (도메인 폴더는 여러 페이지가 함께 쓴다).

## 기존 컴포넌트 수정 필요 (사용자 판단 필요)

없음.
