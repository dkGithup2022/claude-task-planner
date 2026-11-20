# Plan: GET /api/plans

## 요청 스펙

웹의 계획 목록. 6번 화면(계획 목록·실행 이력)과 5번 메인이 쓴다. 출처: `corbina/notes/2026-11-20-ui.md` 5·6절, 끝의 API 표.
- 모든 계획을 만든 시각 최근 것부터. 아직 실행하지 않은 계획(검토 중, 승인, 불허)도 넣는다
- 계획마다 상태별 노드 수 ("6/9 (실패 1)")
- 메인: 실행 중인 계획, 확정을 기다리는 계획(검토 중), 최근 계획 5개

## 정한 모양 (서버 세션)

요청 (query string, 생략 가능): `status` (이 상태의 계획만), `limit` (1~200, 없으면 전부)
- 메인은 `?status=running`, `?status=reviewing`, `?limit=5` 로 세 번 부른다

응답 200

```jsonc
{
  "plans": [
    {
      "plan_id": 11, "title": "...", "status": "running", "persona_ids": [1],
      "created_at": "2026-11-20T04:16:15Z",
      "node_counts": { "todo": 2, "running": 0, "done": 6, "failed": 1, "skipped": 0, "total": 9 }
    }
  ]
}
```

- 노드 수는 지우지 않은 노드만 센다. 노드가 없는 계획은 모두 0
- 명령서(request), 노드, 간선은 목록에 넣지 않는다 (누르면 GET /api/plans/{id})

## Phase 1: 평가

### assess-api

미충족. [Reader] PlanReader.get_summaries(status: PlanStatus | None, limit: int | None) -> list[PlanSummary]. 응답 PlanListResponse.

### assess-usecase

부분 충족. PlanReader 에 get_summaries.
- infrastructure 신규: PlanRepository.find_summaries(status, limit) -> list[PlanSummary]

### assess-infra

부분 충족.
- find_summaries: 계획은 PlanEntityQuery 로 (참여 페르소나 selectin), 노드 상태별 수는 노드 테이블에 걸치므로 PlanJoinQuery SQL 로 한 번에 센다 (`count(*) FILTER (WHERE status = ...)`, plan_id 로 묶음). 둘을 plan_id 로 합친다 (N+1 없음)

### assess-model

충족. PlanSummary, PlanNodeCounts, Plan.to_summary.

## Phase 2: 구현 계획

1. add-infrastructure: find_summaries
2. add-query: PlanEntityQuery.find_all_and_active(status, limit), PlanJoinQuery.count_nodes_by_status(plan_ids) + PlanNodeCountsRow, DefaultPlanRepository
3. add-usecase: PlanReader.get_summaries, PlanProvider 에 PlanJoinQuery
4. add-api: GET "", PlanListResponse·PlanSummaryResponse·NodeCountsResponse
5. 시험: 만든 시각 최근 순, 상태별 노드 수(지운 노드 제외), 노드 없는 계획 0, status·limit, 지운 계획 빠짐(지우기 API 가 없어 DB 로 지운다)

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- PlanRepository.find_summaries, PlanEntityQuery.find_all_and_active, `persistence/plan/plan_join_query.py` PlanJoinQuery·PlanNodeCountsRow (FILTER 로 상태별 수, plan_id IN 확장 바인드), DefaultPlanRepository 에 joins
- PlanReader.get_summaries, PlanProvider 에 join_query
- GET "" (query `status`, `limit`), `dto/plan_list_response.py`
- 검증: ruff, lint-imports, mypy(221 파일) 통과. 시험 2개 더해 모두 58개 통과 (최근 순·상태별 수·지운 노드와 지운 계획 제외·노드 없는 계획 0·응답 필드, status·limit·계획 상태가 아닌 값 400)

### 리뷰 (별도 에이전트, 2026-11-20) — 지식·페르소나·계획 목록 11개 API
- 버그 없음. CLI converter 가 읽는 필드, 시각 모양, soft-delete 제외, JoinQuery SQL(EXISTS 로 중복 없이 셈) 모두 맞음
- 위험 (고치지 않음, 사용자 판단 대기)
  1. 지식 PATCH 가 보내지 않은 persona_ids·source 도 자식 행을 지우고 다시 넣는다. 웹 수정과 CLI 덧붙이기가 동시에 오면 덧붙인 근거가 사라질 수 있다
  2. 지식 만들기·고치기가 persona_ids 가 있는 페르소나인지 보지 않는다. 지운 페르소나 id 로 지식을 만들 수 있고, 페르소나 지우기의 "쓰는 곳" 검사를 건너뛸 수 있다
- 작은 것
  3. 경로·본문의 정수에 위 한계가 없어 2^63 이 넘는 id 는 500 (bigint out of range)
  4. 빈 PATCH(`{}`)도 updated_at 을 바꿔 메인에 "고침" 으로 보인다
  5. persona_ids 의 중복([2, 2])을 그대로 저장한다
