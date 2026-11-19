"""mock 지식 파일(mock 폴더의 memories.json)을 읽고 쓰는 함수. 없으면 처음 값으로 만들어 둔다."""

from __future__ import annotations

from task_plan_manager.common import files
from task_plan_manager.common.mock_data import mock_dir
from task_plan_manager.model.memory.memory import Memory
from task_plan_manager.port.memory_api.memory_api_converter import MemoryApiConverter

# 처음 값: 데이터·API 문서의 지식 spec 과 검색 응답 예시 그대로
FIRST_MEMORIES = {
    "memories": [
        {
            "memory_id": 1,
            "kind": "knowledge",
            "theme": "테이블 설계",
            "body": "최소 스펙부터, 꼭 필요한 스펙만 나열한다. "
            "기존 구조에 테이블을 추가한다면 기존 DB 를 먼저 조회해 컨벤션을 파악한다.",
            "persona_ids": [1],
            "source": [],
        },
        {
            "memory_id": 2,
            "kind": "knowledge",
            "theme": "테이블 설계",
            "body": "배열은 별도 테이블로 둔다. FK 는 기존 서비스가 걸고 있을 때만 건다.",
            "persona_ids": [1, 2],
            "source": [{"quote": "fk 걸지 마, 우리 서비스는 안 걸어", "plan_id": 1}],
        },
    ]
}


def load_memories() -> tuple[Memory, ...]:
    memories_path = mock_dir() / "memories.json"
    if not memories_path.exists():
        files.write_json(memories_path, FIRST_MEMORIES)
    converter = MemoryApiConverter()
    return tuple(converter.to_memory(item) for item in files.read_json(memories_path)["memories"])


def save_memories(memories: tuple[Memory, ...]) -> None:
    converter = MemoryApiConverter()
    files.write_json(
        mock_dir() / "memories.json", {"memories": [converter.to_memory_item(memory) for memory in memories]}
    )
