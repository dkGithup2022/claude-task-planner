import { apiGet, toQueryParams } from "@/lib/api/client";
import type { PlanDetailResponse, PlanListParams, PlanListResponse } from "@/types/api/plan";

/** 페이지: home (실행 중·검토 중·최근 계획), plans (계획 목록) */
export const fetchPlans = (params: PlanListParams = {}) =>
  apiGet<PlanListResponse>("/api/plans", toQueryParams(params), { skipAuth: true });

/** 페이지: plan-graph (계획 요약, 그래프, 노드 패널. 실행 중이면 10초마다 다시) */
export const fetchPlan = (planId: number) =>
  apiGet<PlanDetailResponse>(`/api/plans/${planId}`, undefined, { skipAuth: true });
