import type { PlanDetail } from "@/types/data/domain/plan";

export interface PlanSummaryHeaderProps {
  plan: PlanDetail;
  personaNames: string[];
  /** 실행 중이라 10초마다 다시 읽는 중인지 */
  autoRefresh: boolean;
  showRequest: boolean;
  onToggleRequest: () => void;
}
