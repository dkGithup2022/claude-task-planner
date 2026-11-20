"""지식 추출 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass

from task_plan_manager.workflow.confirm_plan.extract_knowledge.knowledge_candidate import KnowledgeCandidate


@dataclass(frozen=True, slots=True)
class ExtractKnowledgeOutput:
    candidates: list[KnowledgeCandidate]  # 지식 후보. 뽑을 것이 없으면 빈 목록
