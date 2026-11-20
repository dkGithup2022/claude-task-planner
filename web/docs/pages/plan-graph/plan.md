# plan-graph 제작 계획

라우트: /plans/[id]
화면: PlanGraph.dc.html
입력: docs/pages/plan-graph/data.md, components.md, api.md
작성: 2026-11-20
상태: 제작 완료 (2026-11-20). 허가 (사용자 지시 "순차적으로 자유롭게 진행" 에 따라 스스로 검사·허가)

## 1. 충돌 검사

| # | 어디와 어디 | 내용 | 제안 |
|---|---|---|---|
| 1 | components.md ↔ data.md | 없음 | — |
| 1b | api.md ↔ data.md | 없음. PlanDetailResponse = PlanDetail | — |
| 2 | data.md ↔ 화면 | 정의서의 절과 앞뒤 노드는 계산값 | lib/node-spec.ts, lib/plan-graph.ts 에서 계산 |
| 3 | components.md ↔ src | MarkdownText, 그래프 컴포넌트 4개가 없다 | 이번에 만든다 (MarkdownText 는 components-plan.md 에 더함) |

## 2. 구조

파일: src/app/plans/[id]/page.tsx (generateMetadata: "계획 {id}"), PlanGraphClient.tsx, PlanGraphSkeleton.tsx, loading.tsx

```
PlanGraphClient
├── layout/AppHeader current="plans" wide
├── plan/PlanSummaryHeader (요약 세 줄, 명령서 펼치기 → ui/MarkdownText)
├── plan/PlanGraphView (React Flow 12.12.1, plan/PlanGraphNode × n, 간선 전부, 확대·축소) + 기호 설명
└── plan/NodeDetailPanel (머리, 앞뒤 노드, 정의서 → ui/MarkdownText)
```

상태: plan, personas, error("not_found" | "failed" | null), selectedNodeId, showRequest

동작:

| 동작 | 트리거 | 결과 | 부르는 것 |
|---|---|---|---|
| 읽기 | 진입 | 계획과 페르소나 이름 | fetchPlan, fetchPersonas |
| 다시 읽기 | 실행 중이면 10초마다 | 노드 상태가 바뀐다 | fetchPlan |
| 노드 고르기 | 노드 상자, 패널의 앞뒤 노드 | 패널이 그 노드 | 없음 |
| 명령서 펼치기 | 버튼 | 명령서 md 가 보인다 | 없음 |

## 3. 정하지 않은 UI 세부

| 영역 | 항목 | 정한 값 | 이유 |
|---|---|---|---|
| 그래프 | 배치 | 위에서 아래로 층 (앞 노드에서 오는 가장 긴 길이), 층 안은 node_id 순 가운데 정렬 | 과거 웹과 같은 방식, 가안 |
| 그래프 | 상자 크기 | 240 × 76px, 층 간격 64px, 옆 간격 40px | 가안 |
| 그래프 | 상자 높이 | 층 수 × 140 + 80px (480~1400px) | 9층이 720px 에 맞춰지면 글자가 읽히지 않았다 (화면 대조) |
| 그래프 | 간선 | smoothstep, 회색(accent-muted) 화살표 | 흑백 테마 |
| 패널 | 처음 고른 노드 | 실행 중·실패 노드가 있으면 그것, 없으면 첫 노드 | 가안은 노드 하나가 늘 골라져 있다 |
| 오류 | 없는 계획 | Notice "계획 {id} 이 없습니다." + 계획 목록 링크 | 가안에 없음 |

## 4. 제작에 필요한 판단

| 항목 | 판단 |
|---|---|
| 그래프 라이브러리 | @xyflow/react 12.12.1 (13.0 은 11-16 에 나와 2주가 안 되어 쓰지 않음) |
| md | react-markdown 10.1.0, remark-gfm 4.0.1 (템플릿 커밋에는 없어 더함) |
| 보기 전용 | 노드 끌기·잇기·고치기 없음 (웹 UI 문서 1번 화면) |

## 5. 와이어프레임

생략. 가안 아트보드가 구조를 보여 주고, 만든 뒤 화면 대조로 확인했다.

## 6. 제작 기록 (2026-11-20)

- 만든 파일: 페이지 4개, components/plan 의 PlanSummaryHeader·PlanGraphView·PlanGraphNode·NodeDetailPanel, ui/MarkdownText, lib/node-spec.ts·plan-graph.ts (+ 시험), 계획 조회·페르소나 목록 API 타입·mock·호출 함수 (+ 시험)
- 화면 대조에서 고친 것 (ego-browser, 1440px, 실제 서버)
  1. 그래프가 720px 높이에 9층을 맞추며 글자가 읽히지 않았다 → 높이를 층 수에 맞춤
  2. 확인 노드(이중 테두리) 안 글자가 넘쳤다 → 줄 간격을 줄임 (leading-snug)
  3. 메뉴(1120px)와 본문(1232px)의 왼쪽이 어긋났다 → AppHeader 에 wide 를 더함
- 확인: 명령서 펼치기, 패널의 앞뒤 노드로 노드 48 고르기, 없는 계획(/plans/999) 의 안내와 제목 "계획 999"
- 스크린샷: docs/pages/plan-graph/build.png
