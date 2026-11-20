"""노드 정의서. 노드의 output_spec(md)을 절(하는 일, 산출물 형태·담을 것, 그 외 설명)로 읽고 쓴다.
md 모양은 make_plan 이 쓰는 것과 같다: ### 하는 일 / ### 산출물 (- 형태: 줄과 담을 것) / ### 그 외 설명."""

from __future__ import annotations

from dataclasses import dataclass

DOES, OUTPUT, NOTES = "하는 일", "산출물", "그 외 설명"
_FORM_PREFIX = "- 형태: "
_NO_FORM, _NO_NOTES = "(정하지 않음)", "(없음)"


@dataclass(frozen=True, slots=True)
class NodeSpec:
    does: str  # 하는 일
    output_form: str = ""  # 산출물 형태 (문서 / 표 / 결정 / 코드 변경 / 조사 노트). 없으면 ""
    output_contents: str = ""  # 산출물에 담을 것. 없으면 ""
    notes: str = ""  # 그 외 설명. 없으면 ""
    extra_md: str = ""  # 세 절 밖의 절(### 머리째). md 로 되돌릴 때 뒤에 그대로 붙인다

    @classmethod
    def from_md(cls, md: str) -> NodeSpec:
        """'### 이름' 머리로 절을 나눈다. 머리 앞의 글은 하는 일로, 산출물 첫 줄 '- 형태: ' 는 형태로 본다."""
        sections = _split_sections(md)
        form, contents = _split_output(sections.pop(OUTPUT, ""))
        notes = sections.pop(NOTES, "")
        does = sections.pop(DOES, "")
        extra = "\n\n".join(f"### {name}\n{body}" for name, body in sections.items())
        return cls(does, form, contents, "" if notes == _NO_NOTES else notes, extra)

    def to_md(self) -> str:
        """make_plan 과 같은 모양의 md. 형태가 없으면 "(정하지 않음)", 설명이 없으면 "(없음)"."""
        output = _FORM_PREFIX + (self.output_form.strip() or _NO_FORM)
        if self.output_contents.strip():
            output += "\n" + self.output_contents.strip()
        parts = [
            f"### {DOES}\n{self.does.strip()}",
            f"### {OUTPUT}\n{output}",
            f"### {NOTES}\n{self.notes.strip() or _NO_NOTES}",
        ]
        if self.extra_md.strip():
            parts.append(self.extra_md.strip())
        return "\n\n".join(parts)


def _split_sections(md: str) -> dict[str, str]:
    """'### 이름' 머리로 나눈 절. 원래 순서를 지킨다.
    머리 앞의 글은 하는 일로 보고, 같은 이름이 또 나오면 이어 붙인다."""
    sections: dict[str, str] = {}
    name, lines = DOES, list[str]()

    def keep(section: str, body: str) -> None:
        body = body.strip()
        sections[section] = "\n\n".join(part for part in (sections.get(section, ""), body) if part)

    for line in md.splitlines():
        if line.startswith("### "):
            keep(name, "\n".join(lines))
            name, lines = line[4:].strip(), list[str]()
        else:
            lines.append(line)
    keep(name, "\n".join(lines))
    return {key: value for key, value in sections.items() if value or key in (DOES, OUTPUT, NOTES)}


def _split_output(section: str) -> tuple[str, str]:
    """산출물 절 → (형태, 담을 것). 첫 줄이 '- 형태: ' 가 아니면 형태는 비우고 절 전체를 담을 것으로 본다."""
    first, _, rest = section.strip().partition("\n")
    if first.startswith(_FORM_PREFIX):
        form = first[len(_FORM_PREFIX) :].strip()
        return ("" if form == _NO_FORM else form), rest.strip()
    return "", section.strip()
