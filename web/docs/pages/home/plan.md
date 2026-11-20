# home 제작 계획

라우트: /
화면: Main.dc.html
입력: docs/pages/home/data.md, docs/pages/home/components.md, docs/pages/home/api.md
작성: 2026-11-20
상태: 제작 완료 (2026-11-20). 허가 (사용자 지시 "순차적으로 자유롭게 진행" 에 따라 스스로 검사·허가, 2026-11-20)

## 1. 충돌 검사

| # | 어디와 어디 | 내용 | 제안 |
|---|---|---|---|
| 1 | components.md PlanListRow props ↔ data.md | 없음. PlanSummary 의 필드로 충분 | — |
| 1b | api.md 응답 ↔ data.md · components.md | 없음. PlanListResponse.plans, MemoryListResponse.items 가 컴포넌트가 받는 타입 | — |
| 2 | data.md ↔ 화면 | 시각 표시 "11-20 13:16" 을 만드는 함수가 없다 | `lib/utils.ts` 에 formatShortDateTime (사용자 시간대, MM-DD HH:mm) 을 더한다 |
| 3 | components.md ↔ src/components | PlanListRow, NodeProgress, RecentMemoryRow 가 아직 없다 (새로 만들 것) | fe-page-build 에서 만든다 |

## 2. 구조

파일:
- src/app/page.tsx — 서버. metadata: title "task plan manager" (absolute), description "작업 계획과 지식을 한눈에"
- src/app/HomeClient.tsx — 본문. 템플릿의 health 확인용을 덮어쓴다
- src/app/loading.tsx — 스켈레톤. 본문과 같은 max-w (템플릿 것을 덮어쓴다)
- src/app/home.types.ts — HomeData

영역과 컴포넌트:
```
HomeClient
├── A 위 메뉴: layout/AppHeader (current 없음)
├── B 실행 중인 계획: ui/SectionHeader + plan/PlanListRow × n (show "progress") | ui/EmptyState
├── C 확정을 기다리는 계획: ui/SectionHeader + plan/PlanListRow × n (show "node_total") | ui/EmptyState
├── D 최근 계획: ui/SectionHeader(action 전체 보기) + plan/PlanListRow × 5 (show "created")
├── E 최근 지식: ui/SectionHeader(action 전체 보기) + memory/RecentMemoryRow × 5
└── F 지식 개수: 본문 한 줄
```

상태:

| 이름 | 타입 | 초기값 | 어디서 바뀜 |
|---|---|---|---|
| data | HomeData \| null | null | 진입 때 6개 요청을 함께 부른 뒤 |
| failed | boolean | false | 요청 실패 |

동작:

| 동작 | 트리거 | 결과 | 부르는 것 |
|---|---|---|---|
| 읽기 | 진입 | data 를 채운다 | lib/plan-api.ts fetchPlans × 3 (status=running, status=reviewing, limit=5), lib/memory-api.ts fetchMemories × 4 (limit=5, kind 셋 limit=1) |
| 계획 줄 누르기 | 링크 | /plans/{plan_id} | 없음 |
| 지식 줄 누르기 | 링크 | /memories/{memory_id} | 없음 |
| 전체 보기 | 링크 | /plans, /memories | 없음 |

## 3. 정하지 않은 UI 세부

| 영역 | 항목 | 가정값 | 근거 · 이유 |
|---|---|---|---|
| 전체 | 본문 폭·여백 | max-w 1120px, 위 40px 아래 64px, 구역 사이 40px | 가안 |
| B·D | 줄 높이·여백 | 위아래 14px, 칸 사이 16px | 가안 |
| E | 줄 여백 | 위아래 12px | 가안 |
| 전체 | 로딩 | 구역마다 회색 줄 상자 2개 | 가안에 없음 |
| 전체 | 오류 | Notice "불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요." + 오류 토스트 | 가안에 없음 |
| D | 계획이 하나도 없을 때 | EmptyState "아직 계획이 없습니다." | 가안에 없음 |
| E | 지식이 하나도 없을 때 | EmptyState "아직 지식이 없습니다." | 가안에 없음 |

## 4. 제작에 필요한 판단

| 항목 | 판단 | 이유 |
|---|---|---|
| API | api.md 두 항목 모두 "있음" | api.md |
| 인증 | 없음 (로그인 없는 서비스) | |
| 이동 | /plans, /plans/{id}, /memories, /memories/{id} 는 아직 없다. 다음 페이지들에서 만든다. 그 전까지 누르면 404 | 페이지 순서 |
| 스켈레톤 | 구역 5개, 구역마다 줄 2개 | |
| 시각 | 서버 UTC 를 브라우저 시간대로 "MM-DD HH:mm" | data-spec.md 규칙 |
| 계획 줄 오른쪽 칸 | 실행 중: "완료 6 / 10" (실패가 있으면 "6/9 (실패 1)"), 검토 중: "노드 7", 최근: 노드 수와 만든 시각 | 가안 |

## 5. 와이어프레임

- 라우트: /dev/wireframe/home (실제 페이지를 만들면 지운다)
- 스크린샷: docs/pages/home/wireframe.png
- 그린 것: 위 메뉴, 구역 제목, 빈 상태, 상태 기호
- 자리만 잡은 것: PlanListRow, RecentMemoryRow (아직 없는 컴포넌트), 지식 개수 줄

## 6. 제작 기록 (2026-11-20)

만든 파일
- src/app/page.tsx, HomeClient.tsx, HomeSkeleton.tsx, loading.tsx, home.types.ts (템플릿의 health 확인용 화면을 덮어씀)
- src/components/plan/PlanListRow, NodeProgress (+ 시험), src/components/memory/RecentMemoryRow
- src/lib/utils.ts formatShortDateTime (+ 시험)

계획과 달라진 것
- 로딩 상자를 HomeSkeleton 으로 떼어 loading.tsx 와 HomeClient 가 같이 쓴다 (같은 구조를 두 번 쓰지 않으려고)
- layout/AppHeader 의 폭을 1232px 에서 1120px 로 고쳤다. 화면 대조에서 메뉴가 본문보다 왼쪽에서 시작했다 (가안의 메인은 1120px)

화면 대조 (ego-browser, 데스크톱 1440px)
- mock: docs/pages/home/build.png. 가안 Main 과 구역 순서·기호·간격이 같다
- 실제 서버(USE_MOCK=false, 옮긴 데이터): 계획 11, 지식 7개, "지식 3 · 태도 0 · 계획 4" 가 그대로 나온다. 지식 시각은 서버에 옮긴 시각(11-20 19:00)
- 와이어프레임 라우트(/dev/wireframe/home)는 지웠다
