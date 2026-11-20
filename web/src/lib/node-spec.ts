import type { NodeSpecSections } from "@/types/data/domain/node-spec-sections";

/**
 * 노드 정의서(output_spec md)를 절로 나눈다. CLI 의 NodeSpec.from_md 와 같은 규칙:
 * "### 이름" 머리로 나누고, 머리 앞의 글은 하는 일로 본다. 같은 이름이 또 나오면 이어 붙인다.
 * 산출물 절의 첫 줄이 "- 형태: " 면 형태로, 나머지는 담을 것으로 본다. "(정하지 않음)", "(없음)" 은 빈 값.
 * 세 절 밖의 절은 그 외 설명 뒤에 머리째 붙인다.
 */
const DOES = "하는 일";
const OUTPUT = "산출물";
const NOTES = "그 외 설명";
const FORM_PREFIX = "- 형태: ";

export function parseNodeSpec(md: string): NodeSpecSections {
  const sections = new Map<string, string>();
  const keep = (name: string, lines: string[]) => {
    const body = lines.join("\n").trim();
    const before = sections.get(name);
    sections.set(name, [before, body].filter(Boolean).join("\n\n"));
  };
  let name = DOES;
  let lines: string[] = [];
  for (const line of md.split("\n")) {
    if (line.startsWith("### ")) {
      keep(name, lines);
      name = line.slice(4).trim();
      lines = [];
    } else {
      lines.push(line);
    }
  }
  keep(name, lines);

  const [first = "", ...rest] = (sections.get(OUTPUT) ?? "").split("\n");
  const hasForm = first.startsWith(FORM_PREFIX);
  const form = hasForm ? first.slice(FORM_PREFIX.length).trim() : "";
  const notes = sections.get(NOTES) ?? "";
  const extra = [...sections.entries()]
    .filter(([key, body]) => ![DOES, OUTPUT, NOTES].includes(key) && body)
    .map(([key, body]) => `### ${key}\n${body}`);

  return {
    does: sections.get(DOES) ?? "",
    output_form: form === "(정하지 않음)" ? "" : form,
    output_contents: (hasForm ? rest.join("\n") : sections.get(OUTPUT) ?? "").trim(),
    notes: [notes === "(없음)" ? "" : notes, ...extra].filter(Boolean).join("\n\n"),
  };
}
