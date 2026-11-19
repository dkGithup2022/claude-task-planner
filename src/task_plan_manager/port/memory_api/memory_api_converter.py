"""지식 API 의 요청 본문과 응답 JSON. mock 파일의 지식 하나도 같은 모양(지식 spec)이라 같이 쓴다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.model.memory.memory import Memory
from task_plan_manager.model.memory.memory_kind import MemoryKind
from task_plan_manager.model.memory.memory_source import MemorySource
from task_plan_manager.port.memory_api.dto.memory_addition import MemoryAddition
from task_plan_manager.port.memory_api.dto.memory_search_hit import MemorySearchHit
from task_plan_manager.port.memory_api.dto.memory_search_query import MemorySearchQuery
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory


class MemoryApiConverter:
    def to_search_body(self, query: MemorySearchQuery) -> dict[str, Any]:
        return {
            "kind": query.kind.value,
            "query": query.query,
            "persona_ids": list(query.persona_ids),
            "theme": query.theme,
            "limit": query.limit,
        }

    def to_search_hits(self, body: dict[str, Any]) -> tuple[MemorySearchHit, ...]:
        return tuple(
            MemorySearchHit(
                memory_id=int(item["memory_id"]),
                kind=MemoryKind(item["kind"]),
                theme=item["theme"],
                body=item["body"],
                score=float(item.get("score") or 0),
            )
            for item in body.get("items") or ()
        )

    def to_create_body(self, new_memory: NewMemory) -> dict[str, Any]:
        return {
            "kind": new_memory.kind.value,
            "theme": new_memory.theme,
            "body": new_memory.body,
            "persona_ids": list(new_memory.persona_ids),
            "source": _sources_to_body(new_memory.sources),
        }

    def to_append_body(self, addition: MemoryAddition) -> dict[str, Any]:
        return {"body": addition.body, "source": _sources_to_body(addition.sources)}

    def to_memory_id(self, body: dict[str, Any]) -> int:
        return int(body["memory_id"])

    def to_memory(self, item: dict[str, Any]) -> Memory:
        """지식 spec 모양 하나 → Memory (mock 파일을 읽을 때)."""
        return Memory(
            memory_id=int(item["memory_id"]),
            kind=MemoryKind(item["kind"]),
            theme=item["theme"],
            body=item["body"],
            persona_ids=tuple(int(persona_id) for persona_id in item.get("persona_ids") or ()),
            sources=tuple(MemorySource(source["quote"], int(source["plan_id"])) for source in item.get("source") or ()),
        )

    def to_memory_item(self, memory: Memory) -> dict[str, Any]:
        """Memory → 지식 spec 모양 하나 (mock 파일에 쓸 때)."""
        return {
            "memory_id": memory.memory_id,
            "kind": memory.kind.value,
            "theme": memory.theme,
            "body": memory.body,
            "persona_ids": list(memory.persona_ids),
            "source": _sources_to_body(memory.sources),
        }


def _sources_to_body(sources: tuple[MemorySource, ...]) -> list[dict[str, Any]]:
    return [{"quote": source.quote, "plan_id": source.plan_id} for source in sources]
