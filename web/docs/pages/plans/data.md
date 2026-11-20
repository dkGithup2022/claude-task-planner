# plans 데이터

화면: Plans.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 BE 스펙을 근거로 스스로 정함)

영역: 위 메뉴(계획 선택됨) / 제목 줄 "계획" 과 "최근 것부터 (만든 시각 기준) · n개" / 계획 표 (계획, 제목, 상태, 노드, 만든 시각) / 상태 기호 설명 한 줄

## 공용 데이터 (스펙 그대로 사용)

| 항목 | 위치 | 쓰는 필드 | 쓰는 영역 |
|---|---|---|---|
| PlanSummary | src/types/data/domain/plan.ts | plan_id, title, status, created_at, node_counts | 계획 표 |
| NodeCounts | src/types/data/domain/node-counts.ts | done, skipped, failed, total | 노드 열 "10/10", "6/9 (실패 1)" |
| PlanStatus | src/types/data/domain/plan.ts | PLAN_STATUS_LABEL | 상태 열 |

## 스펙 부족

없음.

## API 데이터

이미 있다 (home 에서 만듦).

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| PlanListParams | src/types/api/plan.ts | status?, limit? | GET /api/plans. 이 화면은 조건 없이 부른다 (모든 계획) |
| PlanListResponse | src/types/api/plan.ts | plans: PlanSummary[] | 계획 표 |

## 페이지 전용 데이터

없음. 응답의 plans 를 그대로 표로 그린다.

## 애매한 것 (사용자 판단 필요)

없음.
