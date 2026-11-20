"""간선 다시 정하기에 넘기는 노드 하나. 계획 저장소의 노드와 make_plan 의 저장 전 노드를 같은 모양으로 넘긴다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RelinkNode:
    node_id: int  # 프롬프트에 넘기는 id. 저장 전 노드나 새 노드는 부른 쪽이 정한 임시 id
    title: str
    kind: str  # document | research | code | hitl
    output_spec: str  # 정의서 md. 입력을 만들 때 NodeSpec 으로 절을 나눈다
