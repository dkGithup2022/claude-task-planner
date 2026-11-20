import { it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PersonaForm } from "./PersonaForm";

it("이름이 비면 만들기를 누를 수 없고, 채우면 앞뒤 공백을 지워 onSubmit 을 부른다", async () => {
  const onSubmit = vi.fn();
  render(<PersonaForm submitLabel="만들기" saving={false} onSubmit={onSubmit} onCancel={vi.fn()} />);
  expect(screen.getByRole("button", { name: "만들기" })).toBeDisabled();
  await userEvent.type(screen.getByLabelText("이름"), " fe-developer ");
  await userEvent.type(screen.getByLabelText("설명"), "프론트엔드 개발 역할");
  await userEvent.click(screen.getByRole("button", { name: "만들기" }));
  expect(onSubmit).toHaveBeenCalledWith({ name: "fe-developer", description: "프론트엔드 개발 역할" });
});
