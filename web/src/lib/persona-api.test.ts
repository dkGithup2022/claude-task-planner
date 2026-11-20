import { beforeEach, describe, expect, it, vi } from "vitest";
import { fetchPersonas } from "./persona-api";

beforeEach(() => vi.stubEnv("NEXT_PUBLIC_USE_MOCK", "true"));

describe("페르소나 목록 API (mock)", () => {
  it("case 1: 지식 수와 계획 수를 서버처럼 센다", async () => {
    const { personas } = await fetchPersonas();
    expect(personas.map((p) => [p.persona_id, p.name, p.memory_count, p.plan_count])).toEqual([
      [1, "dankim-persona", 7, 1],
      [2, "be-developer", 1, 0],
    ]);
  });
});
