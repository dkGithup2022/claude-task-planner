import { describe, it, expect } from "vitest";
import { cn, formatRelativeDate } from "./utils";

describe("cn", () => {
  it("충돌하는 tailwind 클래스는 뒤가 이긴다", () => {
    expect(cn("px-4", "px-2")).toBe("px-2");
  });
  it("falsy 값을 무시한다", () => {
    expect(cn("base", false && "hidden", undefined, null)).toBe("base");
  });
});

describe("formatRelativeDate", () => {
  const now = new Date("2026-01-10T12:00:00Z").getTime();
  it("1분 미만은 방금", () => {
    expect(formatRelativeDate(now - 30_000, now)).toBe("방금");
  });
  it("시간 단위", () => {
    expect(formatRelativeDate(now - 3 * 3_600_000, now)).toBe("3시간 전");
  });
  it("30일 이상은 날짜", () => {
    expect(formatRelativeDate("2025-11-01T00:00:00Z", now)).toMatch(/^2025\.11\.01$/);
  });
});
