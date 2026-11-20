import { it, expect } from "vitest";
import { render } from "@testing-library/react";
import { NodeProgress } from "./NodeProgress";

it("완료와 건너뜀을 끝난 수로 세고, 실패가 있으면 붙인다", () => {
  const { container } = render(
    <NodeProgress counts={{ todo: 2, running: 0, done: 5, failed: 1, skipped: 1, total: 9 }} />,
  );
  expect(container.textContent).toBe("6/9 (실패 1)");
});
