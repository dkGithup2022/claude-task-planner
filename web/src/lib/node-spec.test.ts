import { describe, expect, it } from "vitest";
import { parseNodeSpec } from "./node-spec";

describe("parseNodeSpec", () => {
  it("세 절과 산출물 형태를 나눈다", () => {
    const md = "### 하는 일\n도메인 문서를 만든다.\n\n### 산출물\n- 형태: 문서\ndomain.md\n\n### 그 외 설명\n- 이름의 기준이다";
    expect(parseNodeSpec(md)).toEqual({
      does: "도메인 문서를 만든다.",
      output_form: "문서",
      output_contents: "domain.md",
      notes: "- 이름의 기준이다",
    });
  });

  it("머리 앞의 글은 하는 일, '(없음)' 과 '(정하지 않음)' 은 빈 값", () => {
    const md = "앞글\n\n### 산출물\n- 형태: (정하지 않음)\n\n### 그 외 설명\n(없음)";
    expect(parseNodeSpec(md)).toEqual({ does: "앞글", output_form: "", output_contents: "", notes: "" });
  });

  it("세 절 밖의 절은 그 외 설명 뒤에 머리째 붙인다", () => {
    const md = "### 하는 일\n일\n### 참고\n링크";
    expect(parseNodeSpec(md).notes).toBe("### 참고\n링크");
  });
});
