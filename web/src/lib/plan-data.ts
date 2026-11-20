import { ApiError } from "@/lib/api/types";
import type { PlanListParams, PlanListResponse } from "@/types/api/plan";
import type { NodeCounts } from "@/types/data/domain/node-counts";
import type { PlanDetail, PlanSummary } from "@/types/data/domain/plan";
import seed from "./plan-data.seed.json";

/**
 * 계획 mock. 서버 DB 에 옮긴 tpm-trial 데이터(be/seed/tpm-trial)를 서버 응답 모양 그대로 둔다.
 * 계획 11: 노드 10개, 간선 29개, 모든 노드 완료.
 */
const plans: PlanDetail[] = seed.plans as PlanDetail[];

function countNodes(plan: PlanDetail): NodeCounts {
  const counts: NodeCounts = { todo: 0, running: 0, done: 0, failed: 0, skipped: 0, total: 0 };
  for (const node of plan.nodes) {
    counts[node.status] += 1;
    counts.total += 1;
  }
  return counts;
}

function toSummary(plan: PlanDetail): PlanSummary {
  return {
    plan_id: plan.plan_id,
    title: plan.title,
    status: plan.status,
    persona_ids: plan.persona_ids,
    created_at: plan.created_at,
    node_counts: countNodes(plan),
  };
}

/**
 * GET /api/plans
 * case 1: 인자 {}
 *   정상 응답: { plans: 모든 계획, 만든 시각 최근 순, 계획마다 상태별 노드 수 }
 * case 2: 인자 { status: "done" }
 *   정상 응답: { plans: 완료 계획만 }  — mock 의 계획 11 은 done
 * case 3: 인자 { status: "running" }
 *   정상 응답: { plans: [] }
 * case 4: 인자 { limit: 1 }
 *   정상 응답: { plans: 최근 1개 }
 */
export function getPlanList(params: PlanListParams): PlanListResponse {
  const matched = plans
    .filter((plan) => params.status === undefined || plan.status === params.status)
    .sort((a, b) => b.created_at.localeCompare(a.created_at) || b.plan_id - a.plan_id)
    .map(toSummary);
  return { plans: params.limit === undefined ? matched : matched.slice(0, params.limit) };
}

/**
 * GET /api/plans/:id
 * case 1: 인자 { id: 11 }
 *   정상 응답: 계획 11, 노드 10개 (node_id 순), 간선 29개 (edge_id 순)
 * case 2: 인자 { id: 없는 계획 }
 *   예외: 404 "해당 리소스를 찾을 수 없습니다"
 */
export function getPlanDetail(id: number): PlanDetail {
  const plan = plans.find((item) => item.plan_id === id);
  if (!plan) throw new ApiError("해당 리소스를 찾을 수 없습니다", 404);
  return plan;
}

/** 페르소나 mock 의 계획 수 세기에 쓴다 */
export function getAllPlanDetails(): PlanDetail[] {
  return plans;
}
