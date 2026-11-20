# plans 제작 계획

라우트: /plans
화면: Plans.dc.html
입력: docs/pages/plans/data.md, docs/pages/plans/components.md, docs/pages/plans/api.md
작성: 2026-11-20
상태: 제작 완료 (2026-11-20). 허가 (사용자 지시 "순차적으로 자유롭게 진행" 에 따라 스스로 검사·허가)

## 1. 충돌 검사

| # | 어디와 어디 | 내용 | 제안 |
|---|---|---|---|
| 1 | components.md ↔ data.md | 없음 | — |
| 1b | api.md 응답 ↔ data.md · components.md | 없음 | — |
| 2 | data.md ↔ 화면 | 없음 | — |
| 3 | components.md ↔ src/components | PlanTableRow 가 아직 없다 | 이번에 만든다 |

## 2. 구조

파일:
- src/app/plans/page.tsx — 서버. metadata: title "계획", description "모든 계획을 만든 시각 최근 순으로"
- src/app/plans/PlansClient.tsx — 본문
- src/app/plans/loading.tsx — 스켈레톤

```
PlansClient
├── A layout/AppHeader current="plans"
├── B ui/PageHeading title "계획" meta "최근 것부터 (만든 시각 기준) · n개"
├── C ui/Table > thead(ui/TableHeaderCell × 5) > tbody(plan/PlanTableRow × n) | ui/EmptyState
└── D 상태 기호 설명 한 줄
```

상태: plans: PlanSummary[] | null (진입 때 채움), failed: boolean

동작:

| 동작 | 트리거 | 결과 | 부르는 것 |
|---|---|---|---|
| 읽기 | 진입 | plans 를 채운다 | lib/plan-api.ts fetchPlans() |
| 제목 누르기 | 링크 | /plans/{plan_id} | 없음 |

## 3. 정하지 않은 UI 세부

| 영역 | 항목 | 가정값 | 근거 · 이유 |
|---|---|---|---|
| C | 열 폭 | 계획 56px, 상태 112px, 노드 120px, 만든 시각 120px, 제목은 나머지 | 가안 |
| 전체 | 로딩 | 제목 줄 + 표 줄 4개 회색 상자 | 가안에 없음 |
| 전체 | 오류 | Notice "불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요." + 토스트 | home 과 같게 |

## 4. 제작에 필요한 판단

| 항목 | 판단 | 이유 |
|---|---|---|
| API | 있음 (fetchPlans) | api.md |
| 이동 | /plans/{id} 는 다음 화면(계획 그래프)에서 만든다 | 페이지 순서 |
| 시각 | formatShortDateTime (MM-DD HH:mm) | 가안 |

## 5. 와이어프레임

생략. 이미 있는 공용 컴포넌트로만 조립하는 표 화면이라, 가안 아트보드(Plans.dc.html)가 곧 구조 확인용 그림이다. 만든 뒤 화면 대조로 확인한다.

## 6. 제작 기록 (2026-11-20)

- 만든 파일: src/app/plans/page.tsx, PlansClient.tsx, PlansSkeleton.tsx, loading.tsx, src/components/plan/PlanTableRow
- 계획과 달라진 것: 없음. 로딩 상자는 home 처럼 PlansSkeleton 으로 떼어 함께 쓴다
- 건너뛴 단계: fe-generate-api (새 API 없음, fetchPlans 재사용), 와이어프레임 (5절)
- 화면 대조 (ego-browser, 1440px, 실제 서버): docs/pages/plans/build.png. 가안 Plans 와 표 열·기호·설명 줄이 같다
