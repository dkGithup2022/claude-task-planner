import { beforeEach, describe, expect, it, vi } from "vitest";
import { deleteMemory, fetchMemories, fetchMemory, updateMemory } from "./memory-api";

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

describe("지식 조회·고치기·지우기 API (mock)", () => {
  it("조회 case 1·2", async () => {
    const memory = await fetchMemory(1);
    expect(memory.source).toHaveLength(4);
    await expect(fetchMemory(999)).rejects.toMatchObject({ status: 404 });
  });

  it("고치기 case 1: 보낸 필드만 바뀌고 목록 맨 앞에 edited 로 온다", async () => {
    await updateMemory(3, { theme: "API 서버 개발 (고침)" });
    const memory = await fetchMemory(3);
    expect(memory.theme).toBe("API 서버 개발 (고침)");
    expect(memory.kind).toBe("plan");
    const first = (await fetchMemories()).items[0];
    expect([first.memory_id, first.edited]).toEqual([3, true]);
  });

  it("고치기 case 3: 빈 작업 이름은 400", async () => {
    await expect(updateMemory(3, { theme: "" })).rejects.toMatchObject({ status: 400 });
  });

  it("지우기 case 1·2: 지운 지식은 조회 404, 다시 지우면 404", async () => {
    await deleteMemory(5);
    await expect(fetchMemory(5)).rejects.toMatchObject({ status: 404 });
    await expect(deleteMemory(5)).rejects.toMatchObject({ status: 404 });
  });
});
