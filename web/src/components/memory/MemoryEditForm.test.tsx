import { it, expect, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryEditForm } from "./MemoryEditForm";

const memory = {
  memory_id: 1,
  kind: "knowledge" as const,
  theme: "테이블 설계",
  body: "최소 스펙부터",
  persona_ids: [1],
  source: [],
};
const personas = [
  { persona_id: 1, name: "dankim-persona", description: "", memory_count: 7, plan_count: 1 },
  { persona_id: 2, name: "be-developer", description: "", memory_count: 1, plan_count: 0 },
];

it("고친 값으로 onSave 를 부른다", async () => {
  const onSave = vi.fn();
  render(<MemoryEditForm memory={memory} personas={personas} saving={false} onSave={onSave} onCancel={vi.fn()} />);
  await userEvent.clear(screen.getByLabelText("작업 이름"));
  await userEvent.type(screen.getByLabelText("작업 이름"), "테이블 설계 규칙");
  await userEvent.click(screen.getByLabelText("be-developer"));
  await userEvent.selectOptions(screen.getByLabelText("종류"), "plan");
  await userEvent.click(screen.getByRole("button", { name: "저장" }));
  expect(onSave).toHaveBeenCalledWith({
    theme: "테이블 설계 규칙",
    kind: "plan",
    personaIds: [1, 2],
    body: "최소 스펙부터",
  });
});
