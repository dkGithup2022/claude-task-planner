import type { PlanSummary } from "@/types/data/domain/plan";

/** 줄 오른쪽 끝 칸. progress: 실행 중 "6/9 (실패 1)", node_total: 검토 중 "노드 7", created: 최근 "10/10 · 11-20 13:16" */
export type PlanListRowShow = "progress" | "node_total" | "created";

export interface PlanListRowProps {
  plan: PlanSummary;
  show: PlanListRowShow;
}
