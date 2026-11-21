"""작업 지시 생성기의 입력 글.
기존 persona-enhancer-pg2/plugin/client/plan/node_prompts.py:59-89 (build_input) 를 지금 노드 spec 에 맞춘 것.
뺀 절: 작업 종류, 나눈 이유, 완료 기준, 필요한 입력, 루프 (지금 노드 spec 에 없는 필드).
앞 노드는 간선의 선행 노드만, 산출물 스펙까지 넣는다.
결과 위치는 넣지 않는다 (실행할 때 함께 준다, 사용자 2026-11-19)."""

from __future__ import annotations

import re

from task_plan_manager.model.persona.persona import Persona
from task_plan_manager.model.plan.node_kind import NodeKind
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode

CONFIRM_NODE_OWNER = "(사용자 확인 노드)"


def node_prompt_input(
    command_md: str, plan: Plan, node: PlanNode, personas: dict[int, Persona], knowledge_md: str
) -> str:
    """명령서, 작업 지시를 쓸 노드, 이 노드의 산출물 스펙, 앞 노드, 담당 페르소나, 검색한 지식 순서의 글.
    knowledge_md 는 담당 페르소나로 찾은 지식의 글이다 (node_knowledge)."""
    owners = [personas[persona_id] for persona_id in node.persona_ids if persona_id in personas]
    parts = [
        "# 명령서",
        _lower_headings(command_md) or "(명령서 없음)",
        "# 작업 지시를 쓸 노드",
        "\n".join(
            [
                f"- 제목: {node.title}",
                f"- 노드 id: {node.node_id}",
                f"- 종류: {node.kind.value}",
                f"- 담당: {_owner_names(node, owners)}",
            ]
        ),
        "# 이 노드의 산출물 스펙",
        node.output_spec.strip() or "(없음)",
        "# 앞 노드",
        *_previous_parts(plan, node),
        "# 이 노드를 실행할 담당 페르소나",
        _owner_lines(node, owners),
        "# 담당 페르소나로 검색한 태도와 지식",
        knowledge_md,
    ]
    return "\n\n".join(parts) + "\n"


def _lower_headings(command_md: str) -> str:
    """명령서 안의 제목을 한 단계 낮춰 입력의 절 제목과 섞이지 않게 한다.
    shortcut: 코드 블록 안의 "# " 줄(셸 주석)도 낮춰진다 (기존과 같음).
    명령서에 코드 블록이 흔해지면 블록 밖만 바꾼다."""
    return re.sub(r"^(#+) ", r"#\1 ", command_md.strip(), flags=re.M)


def _previous_parts(plan: Plan, node: PlanNode) -> list[str]:
    """선행 노드마다 제목 줄과 산출물 스펙. 없으면 첫 노드라는 한 줄."""
    previous = [plan.node(pre_id) for pre_id in plan.prerequisites(node.node_id)]
    if not previous:
        return ["(없음. 계획의 첫 노드)"]
    parts: list[str] = []
    for pre in previous:
        parts += [f"## {pre.title} ({pre.node_id})", pre.output_spec.strip() or "(산출물 스펙 없음)"]
    return parts


def _owner_names(node: PlanNode, owners: list[Persona]) -> str:
    if node.kind is NodeKind.HITL or not owners:
        return CONFIRM_NODE_OWNER
    return ", ".join(owner.name for owner in owners)


def _owner_lines(node: PlanNode, owners: list[Persona]) -> str:
    if node.kind is NodeKind.HITL or not owners:
        return CONFIRM_NODE_OWNER
    return "\n".join(f"{owner.name}: {owner.description}" for owner in owners)
