import { describe, expect, it } from "vitest";
import type { PlanDetail } from "@/types/data/domain/plan";
import type { PlanNode } from "@/types/data/domain/plan-node";
import { layoutLayers, nextNodes, previousNodes } from "./plan-graph";

const node = (node_id: number): PlanNode => ({
  node_id,
  title: `노드 ${node_id}`,
  kind: "document",
  persona_ids: [1],
  output_spec: "",
  status: "todo",
});

const plan = (edges: [number, number][], ids = [1, 2, 3, 4]): PlanDetail => ({
  plan_id: 1,
  title: "t",
  request: "r",
  persona_ids: [1],
  status: "running",
  created_at: "2026-11-20T00:00:00Z",
  nodes: ids.map(node),
  edges: edges.map(([from, to], index) => ({ edge_id: index + 1, from_node_id: from, to_node_id: to })),
});

describe("layoutLayers", () => {
  it("층은 앞에서 오는 가장 긴 길이다", () => {
    const layers = Object.fromEntries(layoutLayers(plan([[1, 2], [2, 4], [1, 4], [1, 3]])).map((p) => [p.nodeId, p.layer]));
    expect(layers).toEqual({ 1: 0, 2: 1, 3: 1, 4: 2 });
  });

  it("순환이 있어도 끝난다", () => {
    expect(layoutLayers(plan([[1, 2], [2, 1]], [1, 2]))).toHaveLength(2);
  });
});

describe("previousNodes · nextNodes", () => {
  it("간선에서 앞뒤 노드를 node_id 순으로 찾는다", () => {
    const p = plan([[3, 2], [1, 2], [2, 4]]);
    expect(previousNodes(p, 2).map((n) => n.node_id)).toEqual([1, 3]);
    expect(nextNodes(p, 2).map((n) => n.node_id)).toEqual([4]);
  });
});
