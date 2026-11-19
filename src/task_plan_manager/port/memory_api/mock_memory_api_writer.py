"""지식 만들기·덧붙이기의 mock 구현. mock 폴더의 memories.json 에 쓴다."""

from __future__ import annotations

from task_plan_manager.model.memory.memory import Memory
from task_plan_manager.port.memory_api.dto.memory_addition import MemoryAddition
from task_plan_manager.port.memory_api.dto.new_memory import NewMemory
from task_plan_manager.port.memory_api.memory_api_error import MemoryApiError
from task_plan_manager.port.memory_api.memory_api_writer import MemoryApiWriter
from task_plan_manager.port.memory_api.mock_memory_files import load_memories, save_memories


class MockMemoryApiWriter(MemoryApiWriter):
    def create(self, new_memory: NewMemory) -> int:
        # 지금 있는 가장 큰 memory_id 다음 번호로 지식을 만들어 끝에 붙인다
        memories = load_memories()
        memory_id = max((memory.memory_id for memory in memories), default=0) + 1
        memory = Memory(
            memory_id=memory_id,
            kind=new_memory.kind,
            theme=new_memory.theme,
            body=new_memory.body,
            persona_ids=new_memory.persona_ids,
            sources=new_memory.sources,
        )
        save_memories((*memories, memory))
        return memory_id

    def append(self, memory_id: int, addition: MemoryAddition) -> int:
        # 그 지식의 본문 뒤에 "KNOWLEDGE APPENDED" 머리를 달아 덧붙이고 근거를 뒤에 붙인다
        memories = load_memories()
        if all(memory.memory_id != memory_id for memory in memories):
            raise MemoryApiError(f"덧붙일 지식 {memory_id} 가 mock 에 없습니다")
        save_memories(
            tuple(
                memory.append(addition.body, addition.sources) if memory.memory_id == memory_id else memory
                for memory in memories
            )
        )
        return memory_id
