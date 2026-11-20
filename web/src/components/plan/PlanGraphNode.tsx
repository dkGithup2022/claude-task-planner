import { Handle, Position, type NodeProps } from "@xyflow/react";
import { cn } from "@/lib/utils";
import { NODE_HEIGHT, NODE_WIDTH } from "@/lib/plan-graph";
import type { PlanNodeStatus } from "@/types/data/domain/plan-node";
import { NodeStatusMark } from "./NodeStatusMark";
import type { PlanGraphFlowNode } from "./PlanGraphNode.types";

/** 상태별 상자 모양 (웹 UI 문서 1번 화면). 흑백이라 테두리와 글자 색으로 가른다 */
const statusClass: Record<PlanNodeStatus, string> = {
  done: "border border-border",
  running: "border-2 border-border",
  todo: "border border-accent-muted text-text-tertiary",
  failed: "border-2 border-dashed border-border",
  skipped: "border border-border-subtle bg-tertiary text-text-tertiary",
};

/** 그래프의 노드 상자: 번호, 제목, 종류, 상태. 확인 노드(hitl)는 이중 테두리, 고른 노드는 회색 바탕 */
export function PlanGraphNode({ data }: NodeProps<PlanGraphFlowNode>) {
  const { node, selected } = data;
  const isConfirm = node.kind === "hitl";
  return (
    <div
      className={cn(
        "box-border flex cursor-pointer flex-col justify-center gap-0.5 bg-surface px-3 py-2 text-[13px] leading-snug",
        statusClass[node.status],
        isConfirm && "border-4 border-double",
        selected && "bg-tertiary outline-2 outline-offset-2 outline-[var(--border-hover)]",
      )}
      style={{ width: NODE_WIDTH, height: NODE_HEIGHT }}
    >
      <Handle type="target" position={Position.Top} className="!border-0 !bg-transparent" />
      <span className="text-[12px] text-text-tertiary tabular-nums">
        {node.node_id}
        {isConfirm && " · 확인"}
      </span>
      <span className={cn("truncate font-medium", node.status === "skipped" && "line-through")}>{node.title}</span>
      <span className="flex justify-between text-[12px] text-text-secondary">
        <span>{node.kind}</span>
        <NodeStatusMark status={node.status} />
      </span>
      <Handle type="source" position={Position.Bottom} className="!border-0 !bg-transparent" />
    </div>
  );
}
