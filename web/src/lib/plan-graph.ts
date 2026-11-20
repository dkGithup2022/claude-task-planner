import type { PlanDetail } from "@/types/data/domain/plan";
import type { PlanNode } from "@/types/data/domain/plan-node";

/** 그래프 배치의 칸 크기 (px). PlanGraphNode 상자 크기와 맞춘다 */
export const NODE_WIDTH = 240;
export const NODE_HEIGHT = 76;
export const LAYER_GAP = 64;
const COLUMN_GAP = 40;

export interface NodePosition {
  nodeId: number;
  x: number;
  y: number;
  layer: number;
}

/**
 * 위치가 없는 노드를 층으로 놓는다 (과거 웹과 같은 방식). 층 = 앞 노드에서 오는 가장 긴 길이.
 * 위에서 아래로 쌓고, 한 층의 노드는 가운데 정렬해 node_id 순으로 옆에 놓는다.
 * 순환이 있어도 멈추지 않게, 계산 중인 노드를 다시 만나면 0 층으로 본다.
 */
export function layoutLayers(plan: PlanDetail): NodePosition[] {
  const ids = new Set(plan.nodes.map((node) => node.node_id));
  const before = new Map<number, number[]>(plan.nodes.map((node) => [node.node_id, []]));
  for (const edge of plan.edges) {
    if (ids.has(edge.from_node_id) && ids.has(edge.to_node_id) && edge.from_node_id !== edge.to_node_id) {
      before.get(edge.to_node_id)?.push(edge.from_node_id);
    }
  }
  const layer = new Map<number, number>();
  const visiting = new Set<number>();
  const layerOf = (id: number): number => {
    const known = layer.get(id);
    if (known !== undefined) return known;
    if (visiting.has(id)) return 0;
    visiting.add(id);
    const previous = before.get(id) ?? [];
    const value = previous.length === 0 ? 0 : 1 + Math.max(...previous.map(layerOf));
    visiting.delete(id);
    layer.set(id, value);
    return value;
  };

  const byLayer = new Map<number, number[]>();
  for (const node of [...plan.nodes].sort((a, b) => a.node_id - b.node_id)) {
    const value = layerOf(node.node_id);
    byLayer.set(value, [...(byLayer.get(value) ?? []), node.node_id]);
  }
  return [...byLayer.entries()].flatMap(([value, nodeIds]) => {
    const rowWidth = nodeIds.length * NODE_WIDTH + (nodeIds.length - 1) * COLUMN_GAP;
    return nodeIds.map((nodeId, index) => ({
      nodeId,
      layer: value,
      x: index * (NODE_WIDTH + COLUMN_GAP) - rowWidth / 2,
      y: value * (NODE_HEIGHT + LAYER_GAP),
    }));
  });
}

/** 앞 노드 (이 노드로 들어오는 간선의 시작). node_id 순 */
export function previousNodes(plan: PlanDetail, nodeId: number): PlanNode[] {
  const ids = new Set(plan.edges.filter((edge) => edge.to_node_id === nodeId).map((edge) => edge.from_node_id));
  return plan.nodes.filter((node) => ids.has(node.node_id));
}

/** 뒤 노드 (이 노드에서 나가는 간선의 끝). node_id 순 */
export function nextNodes(plan: PlanDetail, nodeId: number): PlanNode[] {
  const ids = new Set(plan.edges.filter((edge) => edge.from_node_id === nodeId).map((edge) => edge.to_node_id));
  return plan.nodes.filter((node) => ids.has(node.node_id));
}

/** 그래프 상자의 높이 (px). 층 수에 맞춰 글자가 읽히는 크기로 두되, 너무 길지 않게 자른다 */
export function graphHeight(positions: NodePosition[]): number {
  const layers = positions.reduce((max, p) => Math.max(max, p.layer + 1), 0);
  return Math.min(Math.max(layers * (NODE_HEIGHT + LAYER_GAP) + 80, 480), 1400);
}
