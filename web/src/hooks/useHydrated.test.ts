import { describe, it, expect } from "vitest";
import { renderHook } from "@testing-library/react";
import { useHydrated } from "./useHydrated";

describe("useHydrated", () => {
  it("effect 실행 후 true", () => {
    const { result } = renderHook(() => useHydrated());
    expect(result.current).toBe(true);
  });
});
