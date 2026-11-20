"use client";

import "@xyflow/react/dist/style.css";
import { Background, Controls, MarkerType, ReactFlow, type Edge } from "@xyflow/react";
import { useMemo } from "react";
import { graphHeight, layoutLayers } from "@/lib/plan-graph";
import { PlanGraphNode } from "./PlanGraphNode";
import type { PlanGraphFlowNode } from "./PlanGraphNode.types";
import type { PlanGraphViewProps } from "./PlanGraphView.types";

const nodeTypes = { plan: PlanGraphNode };
const EDGE_COLOR = "var(--accent-muted)";

/** 계획 그래프 (React Flow). 노드는 층으로 놓고, 간선은 전부 화살표로 그린다. 보기 전용 */
export function PlanGraphView({ plan, selectedNodeId, onSelect }: PlanGraphViewProps) {
  const layout = useMemo(() => layoutLayers(plan), [plan]);
  const nodes = useMemo<PlanGraphFlowNode[]>(() => {
    const positions = new Map(layout.map((p) => [p.nodeId, p]));
    return plan.nodes.map((node) => {
      const position = positions.get(node.node_id) ?? { x: 0, y: 0 };
      return {
        id: String(node.node_id),
        type: "plan",
        position: { x: position.x, y: position.y },
        data: { node, selected: node.node_id === selectedNodeId },
        draggable: false,
        connectable: false,
      };
    });
  }, [plan, layout, selectedNodeId]);

  const edges = useMemo<Edge[]>(
    () =>
      plan.edges.map((edge) => ({
        id: String(edge.edge_id),
        source: String(edge.from_node_id),
        target: String(edge.to_node_id),
        type: "smoothstep",
        style: { stroke: EDGE_COLOR, strokeWidth: 1 },
        markerEnd: { type: MarkerType.ArrowClosed, color: EDGE_COLOR, width: 14, height: 14 },
      })),
    [plan],
  );

  return (
    <div className="border border-border-subtle bg-canvas" style={{ height: graphHeight(layout) }} aria-label="계획 그래프">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => onSelect(Number(node.id))}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        proOptions={{ hideAttribution: true }}
        minZoom={0.3}
        maxZoom={1.5}
      >
        <Background color="var(--border-subtle)" gap={24} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
