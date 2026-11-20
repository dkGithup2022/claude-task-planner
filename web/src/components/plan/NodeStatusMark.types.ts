/** 서버의 노드 상태 값 (be/specs/models.md PlanNodeStatus) */
export type NodeStatusValue = "todo" | "running" | "done" | "failed" | "skipped";

export interface NodeStatusMarkProps {
  status: NodeStatusValue;
}
