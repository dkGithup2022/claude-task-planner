"""노드 정의서(output_spec md)를 절 단위로 만들고 바꾼다. 형식은 make_plan 과 같다: 하는 일 / 산출물 / 그 외 설명."""

from __future__ import annotations

DOES, OUTPUT, NOTES = "하는 일", "산출물", "그 외 설명"
_ORDER = (DOES, OUTPUT, NOTES)


def new_spec(scope: str, output: str | None, note: str | None) -> str:
    """새 노드의 정의서. 산출물이 없으면 "(정하지 않음)", 그 외 설명이 없으면 "(없음)"."""
    return _join(
        {DOES: scope.strip(), OUTPUT: "- 형태: " + (output or "(정하지 않음)").strip(), NOTES: _note_line(note)}
    )


def change_spec(spec: str, scope: str | None, output: str | None, add_note: str | None) -> str:
    """값이 있는 절만 바꾼다. add_note 는 그 외 설명 끝에 한 줄로 더한다."""
    sections = split_sections(spec)
    if scope is not None:
        sections[DOES] = scope.strip()
    if output is not None:
        sections[OUTPUT] = "- 형태: " + output.strip()
    if add_note is not None:
        notes = sections.get(NOTES, "").strip()
        sections[NOTES] = _note_line(add_note) if notes in ("", "(없음)") else notes + "\n" + _note_line(add_note)
    return _join(sections)


def split_sections(spec: str) -> dict[str, str]:
    """'### 이름' 머리로 나눈 절. 머리 앞의 글은 하는 일로 본다."""
    sections: dict[str, str] = {}
    name, lines = DOES, list[str]()
    for line in spec.splitlines():
        if line.startswith("### "):
            sections[name] = "\n".join(lines).strip()
            name, lines = line[4:].strip(), list[str]()
        else:
            lines.append(line)
    sections[name] = "\n".join(lines).strip()
    return {key: value for key, value in sections.items() if value or key in _ORDER}


def _note_line(note: str | None) -> str:
    if not note or not note.strip():
        return "(없음)"
    note = note.strip()
    return note if note.startswith("- ") else "- " + note


def _join(sections: dict[str, str]) -> str:
    """정해진 세 절을 먼저, 그 밖의 절은 뒤에 원래 순서대로."""
    names = [*_ORDER, *(name for name in sections if name not in _ORDER)]
    return "\n\n".join(f"### {name}\n{sections.get(name, '').strip()}" for name in names).strip()
