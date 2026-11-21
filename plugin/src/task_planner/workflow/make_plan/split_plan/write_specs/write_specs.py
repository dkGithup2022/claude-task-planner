"""3-2 정의서. 맨 아래 작업마다 정의서를 쓰고(동시 4개), 노드 spec 모양의 저장 전 노드로 바꾼다.
정의서의 needs 가운데 출처가 다른 작업인 것은 그 작업의 local_id 로 바꿔 선행 작업으로 둔다.
규칙은 기존 generate.py 의 make_node, resolve 와 같다."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from task_planner.claude_utils.prompt.call_prompt import call_prompt
from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.model.persona.persona import Persona
from task_planner.model.plan.node_kind import NodeKind
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.prompt_caller import PromptCaller
from task_planner.workflow.make_plan.split_plan.request_md import demoted
from task_planner.workflow.make_plan.split_plan.task_tree.task_tree import TaskTree
from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem
from task_planner.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind
from task_planner.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft
from task_planner.workflow.make_plan.split_plan.write_specs.prerequisite import Prerequisite
from task_planner.workflow.make_plan.split_plan.write_specs.prompt_spec_output import SpecOutput
from task_planner.workflow.make_plan.split_plan.write_specs.specs_result import SpecsResult

PARALLEL = 4
NOT_A_TASK_SOURCES = ("명령서", "저장소")  # 선행 작업이 아닌 출처

SPEC = PromptSpec(
    name="spec",
    prompt_file=Path(__file__).parent / "prompt_spec.md",
    output_type=SpecOutput,
    model="opus",
)


def write_specs(
    request_md: str,
    tree: TaskTree,
    participants: tuple[Persona, ...],
    call_log: PromptCallLog,
    caller: PromptCaller = call_prompt,
) -> SpecsResult:
    """맨 아래 작업마다 정의서를 받아 저장 전 노드로 바꾼다. 결과는 트리 순서 (n1, n2 …)."""
    leaves = tree.leaves()
    specs = _write_all_specs(request_md, tree, leaves, participants, call_log, caller)
    warnings: list[str] = []
    drafts = tuple(
        _to_draft(tree, leaf, spec, participants, warnings) for leaf, spec in zip(leaves, specs, strict=True)
    )
    return SpecsResult(drafts=drafts, warnings=tuple(warnings))


def _write_all_specs(
    request_md: str,
    tree: TaskTree,
    leaves: tuple[WorkItem, ...],
    participants: tuple[Persona, ...],
    call_log: PromptCallLog,
    caller: PromptCaller,
) -> list[SpecOutput]:
    def write_one(leaf: WorkItem) -> SpecOutput:
        output, record = caller(SPEC, build_spec_input(request_md, tree, leaf, participants))
        call_log.save("spec", record)
        return output  # type: ignore[no-any-return]

    with ThreadPoolExecutor(PARALLEL) as pool:
        return list(pool.map(write_one, leaves))


def _to_draft(
    tree: TaskTree, leaf: WorkItem, spec: SpecOutput, participants: tuple[Persona, ...], warnings: list[str]
) -> NodeDraft:
    """정의서를 노드 spec 필드로 옮긴다. 이름은 트리 이름을 쓰고, 종류·담당은 규칙에 맞게 고친다."""
    assert leaf.local_id is not None
    if spec.name.strip() != leaf.name:
        warnings.append(f'{leaf.local_id}: 정의서 이름 "{spec.name}"이 트리 이름 "{leaf.name}"과 달라 트리 이름을 씀')
    kind = _node_kind(leaf, spec)
    return NodeDraft(
        local_id=leaf.local_id,
        title=leaf.name,
        kind=kind,
        persona_ids=_persona_ids(leaf, spec, kind, participants, warnings),
        output_spec=_output_spec(leaf, spec),
        path=tree.path_of(leaf.item_key),
        prerequisites=_prerequisites(tree, leaf, spec, warnings),
    )


def _node_kind(leaf: WorkItem, spec: SpecOutput) -> NodeKind:
    """트리에서 HITL 이면 hitl. 아니면 정의서의 kind, 모르는 값이면 document."""
    if leaf.kind is WorkKind.HITL:
        return NodeKind.HITL
    if spec.kind in (NodeKind.DOCUMENT, NodeKind.RESEARCH, NodeKind.CODE):
        return NodeKind(spec.kind)
    return NodeKind.DOCUMENT


def _persona_ids(
    leaf: WorkItem, spec: SpecOutput, kind: NodeKind, participants: tuple[Persona, ...], warnings: list[str]
) -> tuple[int, ...]:
    """확인 노드는 담당이 없다. 참여 페르소나에 없는 id 는 빼고, 남는 것이 없으면 첫 참여 페르소나로 둔다."""
    if kind is NodeKind.HITL:
        return ()
    participant_ids = [participant.persona_id for participant in participants]
    chosen = tuple(persona_id for persona_id in spec.persona_ids if persona_id in participant_ids)
    if chosen or not participant_ids:
        return chosen
    warnings.append(
        f"{leaf.local_id}({leaf.name}): 담당 {spec.persona_ids} 이 참여 페르소나에 없어 {participant_ids[0]} 로 둠"
    )
    return (participant_ids[0],)


def _output_spec(leaf: WorkItem, spec: SpecOutput) -> str:
    """정의서의 does, output, notes 를 노드의 output_spec md 로 합친다 (기존 make_node 와 같은 모양)."""
    return "\n".join(
        [
            "### 하는 일",
            spec.does.strip() or leaf.scope,
            "",
            "### 산출물",
            "- 형태: " + (spec.output.form.strip() or "(정하지 않음)"),
            spec.output.contents.strip(),
            "",
            "### 그 외 설명",
            spec.notes.strip() or "(없음)",
        ]
    )


def _prerequisites(tree: TaskTree, leaf: WorkItem, spec: SpecOutput, warnings: list[str]) -> tuple[Prerequisite, ...]:
    """needs 의 출처가 다른 작업이면 그 아래 맨 아래 작업들의 local_id 로 바꾼다. 명령서·저장소는 선행 작업이 아니다."""
    found: list[Prerequisite] = []
    for need in spec.needs:
        source = need.source.strip().removeprefix("[HITL] ").strip()
        if not source or source in NOT_A_TASK_SOURCES:
            continue
        target = _find_source(tree, leaf, source)
        if target is None:
            warnings.append(
                f'{leaf.local_id}({leaf.name}): 필요 정보 "{need.what}"의 출처 "{source}"를 트리에서 하나로 찾지 못함'
            )
            continue
        found += [
            Prerequisite(local_id=prior.local_id, what=need.what.strip())
            for prior in tree.leaves_under(target.item_key)
            if prior.local_id is not None and prior.item_key != leaf.item_key
        ]
    return tuple(found)


def _find_source(tree: TaskTree, leaf: WorkItem, source: str) -> WorkItem | None:
    """출처 이름(또는 " / " 로 이은 경로)이 가리키는 작업.
    같은 이름이 여럿이면 대상과 가장 가까운 것, 정할 수 없으면 None."""
    candidates = [item for item in tree.items if item.parent_key is not None]
    if " / " in source:
        hits = [item for item in candidates if tree.path_of(item.item_key).endswith(source)]
    else:
        hits = [item for item in candidates if item.name == source]
    if len(hits) <= 1:
        return hits[0] if hits else None
    closeness = {item.item_key: _common_depth(item.item_key, leaf.item_key) for item in hits}
    closest = max(closeness.values())
    nearest = [item for item in hits if closeness[item.item_key] == closest]
    return nearest[0] if len(nearest) == 1 else None


def _common_depth(first_key: str, second_key: str) -> int:
    """두 작업의 공통 상위 작업 깊이. "0.1.2" 와 "0.1.3" 이면 2."""
    depth = 0
    for first_part, second_part in zip(first_key.split("."), second_key.split("."), strict=False):
        if first_part != second_part:
            break
        depth += 1
    return depth


def build_spec_input(request_md: str, tree: TaskTree, leaf: WorkItem, participants: tuple[Persona, ...]) -> str:
    """정의서 하나의 입력: 명령서, 작업 트리 전체, 대상 작업, 참여 페르소나 (id 포함)."""
    persona_lines = [
        f"- {person.persona_id} {person.name}: {person.description or '(설명 없음)'}" for person in participants
    ]
    return "\n\n".join(
        [
            "# 명령서\n사용자가 맡긴 원래 일입니다.\n\n" + demoted(request_md),
            "# 작업 트리\n" + tree.render(marked_key=leaf.item_key, mark_text="◀ 정의서 대상").rstrip(),
            f"# 대상 작업\n- 이름: {leaf.name}\n- 목적: {leaf.scope}\n- 종류: {leaf.kind.value}",
            "# 참여 페르소나\n" + ("\n".join(persona_lines) or "(없음)"),
        ]
    )
