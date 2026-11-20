import { vi } from "vitest";

/** 테스트 파일에서 `import "@/test/mocks/next-navigation"` 하면 next/navigation 이 mock 된다. */
export const useRouter = vi.fn(() => ({
  push: vi.fn(),
  replace: vi.fn(),
  back: vi.fn(),
  forward: vi.fn(),
  refresh: vi.fn(),
  prefetch: vi.fn(),
}));
export const useSearchParams = vi.fn(() => new URLSearchParams());
export const usePathname = vi.fn(() => "/");

vi.mock("next/navigation", () => ({ useRouter, useSearchParams, usePathname }));
