# home 데이터

화면: Main.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 BE 스펙을 근거로 스스로 정함)

영역: 위 메뉴 / 실행 중인 계획 / 확정을 기다리는 계획 / 최근 계획 (전체 보기) / 최근 지식 (전체 보기) / 지식 종류별 개수

## 공용 데이터 (스펙 그대로 사용)

| 항목 | 위치 | 쓰는 필드 | 쓰는 영역 |
|---|---|---|---|
| PlanSummary | src/types/data/domain/plan.ts | plan_id, title, status, created_at, node_counts | 실행 중인 계획, 확정을 기다리는 계획, 최근 계획 |
| NodeCounts | src/types/data/domain/node-counts.ts | done, failed, total | 노드 열 "완료 6 / 10", "6/9 (실패 1)" |
| PlanStatus | src/types/data/domain/plan.ts | PLAN_STATUS_LABEL | 계획 상태 기호 |
| MemoryListItem | src/types/data/domain/memory.ts | memory_id, theme, kind, edited, updated_at | 최근 지식 |
| MemoryKind | src/types/data/domain/memory.ts | MEMORY_KIND_LABEL | 최근 지식의 종류, 종류별 개수 |

## 스펙 부족

없음.

## API 데이터

BE 응답 모양을 그대로 옮긴다 (`../be/specs/api.md`). BE 의 목록은 페이지네이션이 아니라 템플릿의 PaginatedResponse 를 쓰지 않는다.

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| PlanListParams | src/types/api/plan.ts | status?: PlanStatus, limit?: number | GET /api/plans. 메인은 `status=running`, `status=reviewing`, `limit=5` 세 번 |
| PlanListResponse | src/types/api/plan.ts | plans: PlanSummary[] | 계획 목록 응답 (만든 시각 최근 순) |
| MemoryListParams | src/types/api/memory.ts | q?: string, kind?: MemoryKind, persona_id?: number, limit?: number | GET /api/memories. 메인은 `limit=5` 와 종류마다 `kind=…&limit=1` (total 만 쓴다) |
| MemoryListResponse | src/types/api/memory.ts | items: MemoryListItem[], total: number | 지식 목록 응답 (고친 시각 최근 순). total 은 limit 을 뺀 개수 |

## 페이지 전용 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| HomeData | src/app/home.types.ts | running: PlanSummary[], reviewing: PlanSummary[], recentPlans: PlanSummary[], recentMemories: MemoryListItem[], memoryTotal: number, kindCounts: Record<MemoryKind, number> | 여러 응답을 메인 화면용으로 합친 모양 |

## 애매한 것 (사용자 판단 필요)

없음. 지식 종류별 개수는 서버에 따로 세는 API 가 없어 종류마다 `limit=1` 로 불러 total 을 쓴다 (요청 3번). 지식이 많아져도 응답은 한 줄씩이다.
