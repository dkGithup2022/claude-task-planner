import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchPlan, fetchPlans } from "./plan-api";

beforeEach(() => vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "true"));

describe("계획 목록 API (mock)", () => {
  it("case 1: 모든 계획과 상태별 노드 수", async () => {
    const res = await fetchPlans();
    expect(res.plans.map((plan) => plan.plan_id)).toEqual([11]);
    expect(res.plans[0].node_counts).toEqual({ todo: 0, running: 0, done: 10, failed: 0, skipped: 0, total: 10 });
  });

  it("case 2·3: 상태로 거른다", async () => {
    expect((await fetchPlans({ status: "done" })).plans).toHaveLength(1);
    expect((await fetchPlans({ status: "running" })).plans).toEqual([]);
  });

  it("case 4: limit", async () => {
    expect((await fetchPlans({ limit: 1 })).plans).toHaveLength(1);
  });
});

describe("계획 조회 API (mock)", () => {
  it("case 1: 노드와 간선이 순서대로 온다", async () => {
    const plan = await fetchPlan(11);
    expect(plan.nodes).toHaveLength(10);
    expect(plan.edges).toHaveLength(29);
    expect(plan.nodes.map((node) => node.node_id)).toEqual([...plan.nodes.map((node) => node.node_id)].sort((a, b) => a - b));
  });

  it("case 2: 없는 계획은 404", async () => {
    await expect(fetchPlan(999)).rejects.toMatchObject({ status: 404 });
  });
});
