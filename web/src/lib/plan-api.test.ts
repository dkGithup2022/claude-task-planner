import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchPlans } from "./plan-api";

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
