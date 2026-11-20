import { beforeEach, describe, expect, it, vi } from "vitest";
import { createPersona, deletePersona, fetchPersonas, updatePersona } from "./persona-api";

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

describe("페르소나 만들기·고치기·지우기 API (mock)", () => {
  it("만들기 case 1·2·3", async () => {
    const { persona_id } = await createPersona({ name: "fe-developer", description: "" });
    expect(persona_id).toBe(3);
    const created = (await fetchPersonas()).personas.at(-1);
    expect([created?.name, created?.memory_count, created?.plan_count]).toEqual(["fe-developer", 0, 0]);
    await expect(createPersona({ name: "fe-developer", description: "" })).rejects.toMatchObject({ status: 409 });
    await expect(createPersona({ name: "", description: "" })).rejects.toMatchObject({ status: 400 });
  });

  it("고치기 case 1·2·3", async () => {
    await updatePersona(2, { description: "새 설명" });
    expect((await fetchPersonas()).personas[1].description).toBe("새 설명");
    await expect(updatePersona(999, { name: "x" })).rejects.toMatchObject({ status: 404 });
    await expect(updatePersona(2, { name: "dankim-persona" })).rejects.toMatchObject({ status: 409 });
  });

  it("지우기 case 1·2·3", async () => {
    await expect(deletePersona(1)).rejects.toMatchObject({
      status: 409,
      message: "지식 7개, 계획 1개가 이 페르소나를 씁니다",
    });
    await deletePersona(3);
    expect((await fetchPersonas()).personas.map((p) => p.persona_id)).toEqual([1, 2]);
    await expect(deletePersona(3)).rejects.toMatchObject({ status: 404 });
  });
});
