"""노드마다 작업 지시(prompt.md)를 만든다. write_prompts 와 retry_prompts 가 같이 쓴다.

생성기는 읽기 도구를 켠 claude -p(run_agent, opus)다. 프롬프트가 생성기의 조사(라이브러리, 웹 검색)를 전제하기 때문이다
(사용자, 2026-11-19 "run_agent 를 지금 만들어서 여기 사용 하도록"). 노드끼리는 3개씩 동시에 만든다:
작업 지시는 앞 노드의 결과가 아니라 산출물 스펙만 읽기 때문이다 (도식화 D 2 단계).
만든 뒤 첫 줄이 정해진 제목인지 검사하고, 끝에 산출물 스펙 원문 절과 글쓰기 규칙을 붙여 저장한다 (사용자, 2026-11-18).
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from task_plan_manager.claude_utils.agent.agent_call_error import AgentCallError
from task_plan_manager.claude_utils.agent.dto.agent_result import AgentResult
from task_plan_manager.claude_utils.agent.run_agent import install_child_cleanup, run_agent
from task_plan_manager.model.persona.persona import Persona
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_node import PlanNode
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_plan_manager.port.persona_api.persona_api_choice import persona_api_reader
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.plan_run.prompts.write_prompts.node_knowledge import node_knowledge
from task_plan_manager.workflow.plan_run.prompts.write_prompts.node_prompt_error import NodePromptError
from task_plan_manager.workflow.plan_run.prompts.write_prompts.node_prompt_input import node_prompt_input
from task_plan_manager.workflow.plan_run.show_progress import show_writing_prompts

HERE = Path(__file__).parent
FIRST_LINE = "## 전체 작업과 이 노드의 목표"
SPEC_SECTION = "## 이 노드의 산출물 스펙 (원문)"
READ_TOOLS = ("Read", "Glob", "Grep", "WebSearch", "WebFetch")
MODEL = "opus"
TIMEOUT_SECONDS = 900  # 기존 run_agent 와 같음
PARALLEL = 3


def write_node_prompts(plan_id: int, node_ids: list[int]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """노드마다 작업 지시를 만들어 prompt.md 에 쓴다. 3개씩 동시에. (만든 것, 실패한 것). 실패한 노드는 쓰지 않는다."""
    # 읽기: 계획, 명령서, 페르소나, 생성기 프롬프트
    plan = plan_api_reader().get_plan(plan_id)
    show_writing_prompts(plan)
    command_md = DefaultPlanFolderReader().read_command(plan_id)
    personas = {persona.persona_id: persona for persona in persona_api_reader().list_personas()}
    system_prompt = generator_prompt()
    install_child_cleanup()  # 명령이 끊기면 돌던 생성기도 끝낸다
    made: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
        futures = {
            node_id: pool.submit(_make_one, system_prompt, command_md, plan, plan.node(node_id), personas)
            for node_id in node_ids
        }
        for node_id, future in futures.items():
            try:
                text, answer, warning = future.result()
            except NodePromptError as error:
                failed.append({"node_id": node_id, "title": plan.node(node_id).title, "reason": str(error)})
                continue
            # 쓰기: 이 스레드에서만 쓴다
            DefaultPlanFolderWriter().write_prompt(plan_id, node_id, text)
            made.append(_made_entry(node_id, answer, warning))
    return made, failed


def generator_prompt() -> str:
    """생성기 프롬프트에 글쓰기 규칙을 끼운 글."""
    body = (HERE / "prompt_write_node_prompt.md").read_text(encoding="utf-8")
    return body.replace("{WRITING}", writing_rules())


def writing_rules() -> str:
    return (HERE / "writing.md").read_text(encoding="utf-8").strip()


def _made_entry(node_id: int, answer: AgentResult, warning: str | None) -> dict[str, Any]:
    """만든 것 한 줄. 지식 검색이 실패했으면 warning 을 더한다."""
    entry: dict[str, Any] = {"node_id": node_id, "cost_usd": answer.cost_usd, "seconds": answer.seconds}
    if warning:
        entry["warning"] = warning
    return entry


def _make_one(
    system_prompt: str, command_md: str, plan: Plan, node: PlanNode, personas: dict[int, Persona]
) -> tuple[str, AgentResult, str | None]:
    """담당 페르소나의 지식을 찾아 생성기를 부르고 첫 줄을 검사한 뒤, 산출물 스펙 원문 절과 글쓰기 규칙을 붙인 글.
    셋째 값은 지식 찾기의 경고 (없으면 None)."""
    knowledge_md, warning = node_knowledge(node)
    user_input = node_prompt_input(command_md, plan, node, personas, knowledge_md)
    try:
        answer = run_agent(system_prompt, user_input, READ_TOOLS, Path.cwd(), MODEL, TIMEOUT_SECONDS)
    except AgentCallError as error:
        raise NodePromptError(str(error)) from error
    if not answer.text.startswith(FIRST_LINE):
        raise NodePromptError("첫 줄이 정해진 제목이 아님")
    text = "\n\n".join([answer.text, SPEC_SECTION, node.output_spec.strip(), writing_rules()])
    return text + "\n", answer, warning
