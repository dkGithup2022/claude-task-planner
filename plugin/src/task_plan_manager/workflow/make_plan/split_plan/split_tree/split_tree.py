"""3-1 나눌지 판단. 작업 트리를 한 층씩 넓힌다. 한 층 안의 작업은 동시에 판단한다.
멈추는 때: 더 나눌 작업이 없을 때, 노드 상한이나 깊이 상한에 닿았을 때. 규칙은 기존 generate.py 의 split_all 과 같다."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from task_plan_manager.claude_utils.prompt.call_prompt import call_prompt
from task_plan_manager.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_plan_manager.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_plan_manager.workflow.make_plan.split_plan.prompt_caller import PromptCaller
from task_plan_manager.workflow.make_plan.split_plan.request_md import demoted, section
from task_plan_manager.workflow.make_plan.split_plan.split_tree.prompt_split_output import SplitOutput
from task_plan_manager.workflow.make_plan.split_plan.split_tree.relevant_plan_knowledge import relevant_plan_knowledge
from task_plan_manager.workflow.make_plan.split_plan.split_tree.split_result import SplitResult
from task_plan_manager.workflow.make_plan.split_plan.task_tree.task_tree import ROOT_KEY, TaskTree
from task_plan_manager.workflow.make_plan.split_plan.task_tree.work_item import WorkItem
from task_plan_manager.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind

MAX_NODES = 40  # 맨 아래 작업(= 노드) 상한 (기존과 같음)
MAX_DEPTH = 5  # 이 깊이에 닿은 작업은 더 판단하지 않는다
PARALLEL = 4  # 한 층 안에서 동시에 부르는 claude -p 수

SPLIT = PromptSpec(
    name="split",
    prompt_file=Path(__file__).parent / "prompt_split.md",
    output_type=SplitOutput,
    model="opus",
)


def split_tree(
    title: str,
    request_md: str,
    persona_ids: tuple[int, ...],
    call_log: PromptCallLog,
    caller: PromptCaller = call_prompt,
) -> SplitResult:
    """명령서 전체에서 시작해 나눌 작업이 없어질 때까지 한 층씩 판단하고, 맨 아래 작업에 local_id 를 붙인다.
    persona_ids 는 계획의 참여 페르소나다. 작업마다 이 페르소나의 지식을 찾아 판단에 넣는다."""
    tree = TaskTree.start(title, "명령서 전체. 산출물: " + _one_line(section(request_md, "산출물")))
    warnings: list[str] = []
    frontier = tree.items
    while frontier:
        if len(tree.leaves()) >= MAX_NODES:
            warnings.append(f"노드 상한 {MAX_NODES}개에 닿아 작업 {len(frontier)}개를 더 나누지 않음")
            break
        judgments = _judge_layer(tree, frontier, request_md, persona_ids, call_log, caller)
        warnings += [warning for _, warning in judgments if warning]
        tree, frontier = _apply_layer(tree, frontier, [judgment for judgment, _ in judgments], warnings)
    return SplitResult(tree=tree.with_local_ids(), warnings=tuple(warnings))


def _judge_layer(
    tree: TaskTree,
    frontier: tuple[WorkItem, ...],
    request_md: str,
    persona_ids: tuple[int, ...],
    call_log: PromptCallLog,
    caller: PromptCaller,
) -> list[tuple[SplitOutput, str | None]]:
    """한 층의 작업마다 지식을 찾아 거른 뒤 나눌지 판단한다. (판단, 지식 찾기의 경고) 를 frontier 순서 그대로."""
    plan_title = tree.item(ROOT_KEY).name

    def judge(work_item: WorkItem) -> tuple[SplitOutput, str | None]:
        knowledge_md, warning = relevant_plan_knowledge(plan_title, work_item, persona_ids, call_log, caller)
        output, record = caller(SPLIT, build_split_input(tree, work_item, request_md, knowledge_md))
        call_log.save("split", record)
        return output, warning

    with ThreadPoolExecutor(PARALLEL) as pool:
        return list(pool.map(judge, frontier))


def _apply_layer(
    tree: TaskTree, frontier: tuple[WorkItem, ...], judgments: list[SplitOutput], warnings: list[str]
) -> tuple[TaskTree, tuple[WorkItem, ...]]:
    """판단 결과를 판단한 순서대로 트리에 넣고, 다음 층에서 판단할 작업을 돌려준다."""
    next_frontier: list[WorkItem] = []
    for work_item, judgment in zip(frontier, judgments, strict=True):
        tree = tree.with_why(work_item.item_key, judgment.why)
        children = _children_to_add(tree, work_item, judgment, warnings)
        if not children:
            continue
        tree = tree.with_children(work_item.item_key, children)
        next_frontier += [child for child in children if _should_judge(child, warnings)]
    return tree, tuple(next_frontier)


def _children_to_add(
    tree: TaskTree, work_item: WorkItem, judgment: SplitOutput, warnings: list[str]
) -> tuple[WorkItem, ...]:
    """나누기로 했고, 자식이 2개 이상이고, 노드 상한을 넘지 않을 때만 자식 작업을 만든다."""
    named = [child for child in judgment.children if child.name.strip()]
    if not judgment.split or len(named) < 2:
        return ()
    leaf_count_after = len(tree.leaves()) + len(named) - 1
    if leaf_count_after > MAX_NODES:
        warnings.append(
            f"{work_item.name}: 나누면 노드가 {leaf_count_after}개가 되어 상한 {MAX_NODES}개를 넘으므로 나누지 않음"
        )
        return ()
    return tuple(
        WorkItem(
            item_key=f"{work_item.item_key}.{order}",
            name=child.name.strip(),
            scope=child.scope.strip(),
            kind=WorkKind.HITL if child.kind == WorkKind.HITL else WorkKind.TASK,
            depth=work_item.depth + 1,
            parent_key=work_item.item_key,
        )
        for order, child in enumerate(named, start=1)
    )


def _should_judge(child: WorkItem, warnings: list[str]) -> bool:
    """HITL 은 더 나누지 않는다. 깊이 상한에 닿은 작업도 더 판단하지 않는다."""
    if child.kind is WorkKind.HITL:
        return False
    if child.depth >= MAX_DEPTH:
        warnings.append(f"{child.name}: 깊이 상한 {MAX_DEPTH}에 닿아 더 판단하지 않음")
        return False
    return True


def build_split_input(tree: TaskTree, work_item: WorkItem, request_md: str, knowledge_md: str) -> str:
    """나누기 판단 하나의 입력: 명령서, 판단할 작업, 지금까지의 작업 트리, 쓸 수 있는 자료, 검색 결과.
    knowledge_md 는 이 작업으로 찾아 거른 지식의 글이다 (없으면 "없음", 검색이 실패하면 "(검색 실패)")."""
    materials = "\n".join(text for text in (section(request_md, "맥락"), section(request_md, "저장소")) if text)
    return "\n\n".join(
        [
            "# 명령서\n사용자가 맡긴 원래 일입니다.\n\n" + demoted(request_md),
            f"# 작업\n- 이름: {work_item.name}\n- 하는 일: {work_item.scope}",
            "# 지금까지의 작업 트리\n" + tree.render(marked_key=work_item.item_key).rstrip(),
            "# 쓸 수 있는 자료\n" + (materials or "(없음)"),
            "# 검색 결과\n" + knowledge_md,
        ]
    )


def _one_line(text: str) -> str:
    """여러 줄 목록을 한 줄로. 작업 트리의 한 줄에 들어가야 하므로 "- 장보기 목록\n- 레시피" → "장보기 목록, 레시피"."""
    return ", ".join(line.strip().removeprefix("- ").strip() for line in text.splitlines() if line.strip())
