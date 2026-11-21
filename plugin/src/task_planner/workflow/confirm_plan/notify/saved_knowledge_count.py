"""후보마다의 save_knowledge 결과를 세어, 새로 저장한 수와 덧붙인 수를 돌려준다.
넣지 않기를 골라 keep_each 를 건너뛴 후보는 결과가 없으므로 세지 않는다."""

from __future__ import annotations

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_missing_error import OutputMissingError


def saved_knowledge_count(context: FlowContext) -> tuple[int, int]:
    """(새로 저장한 수, 덧붙인 수)."""
    candidate_count = len(context.read("extract_knowledge")["candidates"])
    actions: list[str] = []
    for item_number in range(1, candidate_count + 1):
        try:
            saved = context.read("save_knowledge", str(item_number))
        except OutputMissingError:
            continue
        if saved["saved"]:
            actions.append(saved["action"])
    return actions.count("new"), actions.count("append")
