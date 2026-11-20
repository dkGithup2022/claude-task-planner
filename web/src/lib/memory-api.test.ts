import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchMemories } from "./memory-api";

beforeEach(() => vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "true"));

describe("지식 목록 API (mock)", () => {
  it("case 1: 지식 7개, 덧붙인 횟수와 근거 계획", async () => {
    const res = await fetchMemories();
    expect(res.total).toBe(7);
    const first = res.items.find((item) => item.memory_id === 1);
    expect(first?.appended_count).toBe(3);
    expect(first?.source_plan_ids).toEqual([3, 11]);
  });

  it("case 2: 종류와 limit — total 은 limit 을 뺀 개수", async () => {
    const res = await fetchMemories({ kind: "plan", limit: 1 });
    expect(res.items).toHaveLength(1);
    expect(res.total).toBe(4);
  });

  it("case 3·4: 검색어와 페르소나", async () => {
    expect((await fetchMemories({ q: "기획" })).items.length).toBeGreaterThan(0);
    expect((await fetchMemories({ persona_id: 2 })).items.map((item) => item.memory_id)).toEqual([2]);
  });
});
