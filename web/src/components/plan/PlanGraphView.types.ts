import type { PlanDetail } from "@/types/data/domain/plan";

export interface PlanGraphViewProps {
  plan: PlanDetail;
  selectedNodeId: number | null;
  onSelect: (nodeId: number) => void;
}
