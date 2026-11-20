import type { Node } from "@xyflow/react";
import type { PlanNode } from "@/types/data/domain/plan-node";

export type PlanGraphNodeData = { node: PlanNode; selected: boolean };

/** React Flow 의 노드 타입 이름 "plan" */
export type PlanGraphFlowNode = Node<PlanGraphNodeData, "plan">;
