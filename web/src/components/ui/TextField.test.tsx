import { it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TextField } from "./TextField";

it("라벨로 입력칸을 찾고 입력할 수 있다", async () => {
  render(<TextField label="검색어 (작업 이름·본문)" placeholder="예: 테이블 설계" />);
  const input = screen.getByLabelText("검색어 (작업 이름·본문)");
  await userEvent.type(input, "기획");
  expect(input).toHaveValue("기획");
});
