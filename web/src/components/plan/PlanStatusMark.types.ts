/** 서버의 계획 상태 값 (be/specs/models.md PlanStatus). "실패" 는 없다 */
export type PlanStatusValue = "drafting" | "reviewing" | "approved" | "rejected" | "running" | "done";

export interface PlanStatusMarkProps {
  status: PlanStatusValue;
}
