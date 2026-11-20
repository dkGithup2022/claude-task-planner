"""후보의 근거(사용자 말)마다, 계획을 보여 준 뒤의 대화에서 그 말과 바로 앞의 Claude 말을 찾는다."""

from __future__ import annotations

from pathlib import Path

from task_plan_manager.workflow.confirm_plan.extract_knowledge.feedback_dialogue import feedback_dialogue


def quoted_context(transcript: Path, shown_at: str, quotes: list[str]) -> str:
    """'assistant: …' / 'user: …' 줄. 근거의 말을 대화에서 찾지 못하면 그 말만 user 줄로 넣는다."""
    utterances = feedback_dialogue(transcript, shown_at)
    blocks: list[str] = []
    for quote in quotes:
        index = next(
            (index for index, u in enumerate(utterances) if u.role == "user" and quote.strip() in u.text), None
        )
        if index is None:
            blocks.append(f"user: {quote}")
            continue
        previous = utterances[index - 1] if index > 0 and utterances[index - 1].role == "assistant" else None
        lines = ([f"assistant: {previous.text}"] if previous else []) + [f"user: {utterances[index].text}"]
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)
