import type { PlanDetail, PlanStatus, PlanSummary } from "@/types/data/domain/plan";

/**
 * 계획 API. BE 확정 (be/specs/api.md 와 같다). docs/pages/home/api.md
 */

/** GET /api/plans 요청 — Main.dc.html 실행 중·검토 중·최근 5개 */
export interface PlanListParams {
  status?: PlanStatus; // 이 상태의 계획만
  limit?: number;      // 최대 개수 (1~200). 없으면 전부
}

/** GET /api/plans 응답. 만든 시각 최근 순 */
export interface PlanListResponse {
  plans: PlanSummary[];
}

/** GET /api/plans/{plan_id} 응답. 노드는 node_id 순, 간선은 edge_id 순. 없으면 404 — docs/pages/plan-graph/api.md */
export type PlanDetailResponse = PlanDetail;
