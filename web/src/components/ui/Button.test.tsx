import { it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "./Button";

it("누르면 onClick 이 불린다", async () => {
  const onClick = vi.fn();
  render(<Button variant="primary" onClick={onClick}>수정</Button>);
  await userEvent.click(screen.getByRole("button", { name: "수정" }));
  expect(onClick).toHaveBeenCalledOnce();
});

it("disabled 면 눌리지 않는다", async () => {
  const onClick = vi.fn();
  render(<Button disabled onClick={onClick}>삭제</Button>);
  await userEvent.click(screen.getByRole("button", { name: "삭제" }));
  expect(onClick).not.toHaveBeenCalled();
});
