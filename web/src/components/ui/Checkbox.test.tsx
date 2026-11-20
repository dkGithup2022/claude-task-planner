import { it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Checkbox } from "./Checkbox";

it("라벨을 누르면 onChange 가 불리고 체크된다", async () => {
  const onChange = vi.fn();
  render(<Checkbox label="be-developer" onChange={onChange} />);
  await userEvent.click(screen.getByText("be-developer"));
  expect(onChange).toHaveBeenCalledOnce();
  expect(screen.getByRole("checkbox", { name: "be-developer" })).toBeChecked();
});
