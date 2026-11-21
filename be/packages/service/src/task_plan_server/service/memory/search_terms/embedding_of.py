from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.model.memory.memory_embedding import MemoryEmbedding


def embedding_of(embedder: TextEmbedder, theme: str, body: str) -> MemoryEmbedding:
    """저장(인덱싱)할 지식의 검색용 벡터. 작업 이름과 본문을 줄바꿈으로 이어 하나로 만든다."""
    return embedder.embed(f"{theme}\n{body}")
