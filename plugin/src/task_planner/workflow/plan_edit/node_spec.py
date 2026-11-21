"""계획 고치기에서 노드 정의서(output_spec md)를 만들고 바꾼다. 모양은 make_plan 과 같다 (model 의 NodeSpec)."""

from __future__ import annotations

from dataclasses import replace

from task_planner.model.plan.node_spec import NodeSpec
from task_planner.workflow.plan_edit.op.new_part import NewPart
from task_planner.workflow.plan_edit.op.node_output import NodeOutput


def new_spec(part: NewPart) -> str:
    """새 노드의 정의서. 산출물이 없으면 형태 "(정하지 않음)", 그 외 설명이 없으면 "(없음)"."""
    output = part.output or NodeOutput("")
    return NodeSpec(part.does.strip(), output.form, output.contents, _bullets(part.notes)).to_md()


def change_spec(spec_md: str, does: str | None, output: NodeOutput | None, add_note: str | None) -> str:
    """값이 있는 절만 바꾼다. add_note 는 그 외 설명 끝에 한 줄로 더한다."""
    spec = NodeSpec.from_md(spec_md)
    if does is not None:
        spec = replace(spec, does=does.strip())
    if output is not None:
        spec = replace(spec, output_form=output.form, output_contents=output.contents)
    if add_note is not None and add_note.strip():
        spec = replace(spec, notes="\n".join(line for line in (spec.notes, _bullets(add_note)) if line))
    return spec.to_md()


def _bullets(text: str | None) -> str:
    """줄마다 "- " 를 붙인 목록. 이미 붙어 있으면 그대로."""
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return "\n".join(line if line.startswith("- ") else "- " + line for line in lines)
