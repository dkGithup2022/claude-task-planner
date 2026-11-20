import { it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { NodeStatusMark } from "./NodeStatusMark";

it("상태마다 기호와 이름을 보인다", () => {
  render(
    <>
      <NodeStatusMark status="done" />
      <NodeStatusMark status="failed" />
    </>,
  );
  expect(screen.getByText("완료")).toBeInTheDocument();
  expect(screen.getByText("실패")).toBeInTheDocument();
});
