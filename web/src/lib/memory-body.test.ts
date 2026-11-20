import { describe, expect, it } from "vitest";
import { splitMemoryBody } from "./memory-body";

describe("splitMemoryBody", () => {
  it("덧붙임 머리로 나눈다", () => {
    const body = "처음\n\n****** KNOWLEDGE APPENDED 1 ********\n하나\n\n****** KNOWLEDGE APPENDED 2 ********\n둘";
    expect(splitMemoryBody(body)).toEqual({
      base: "처음",
      appended: [
        { number: 1, text: "하나" },
        { number: 2, text: "둘" },
      ],
    });
  });

  it("머리가 없으면 본문 하나", () => {
    expect(splitMemoryBody("본문")).toEqual({ base: "본문", appended: [] });
  });
});
