import { apiGet, toQueryParams } from "@/lib/api/client";
import type { PlanListParams, PlanListResponse } from "@/types/api/plan";

/** 페이지: home (실행 중·검토 중·최근 계획), plans (계획 목록) */
export const fetchPlans = (params: PlanListParams = {}) =>
  apiGet<PlanListResponse>("/api/plans", toQueryParams(params), { skipAuth: true });
