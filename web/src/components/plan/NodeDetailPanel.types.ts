import type { PlanDetail } from "@/types/data/domain/plan";
import type { PlanNode } from "@/types/data/domain/plan-node";

export interface NodeDetailPanelProps {
  plan: PlanDetail;
  node: PlanNode;
  /** persona_id → 이름 */
  personaNames: Map<number, string>;
  onSelect: (nodeId: number) => void;
}
