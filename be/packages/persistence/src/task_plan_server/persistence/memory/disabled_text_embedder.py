from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.model.memory.memory_embedding import MemoryEmbedding


class DisabledTextEmbedder(TextEmbedder):
    """벡터 검색을 끈 상태 (설정 APP_MEMORY_SEARCH_VECTOR 가 false). 모델을 띄우지 않는다.

    부르는 쪽이 enabled 를 먼저 보므로 embed 는 불리지 않는다. 불리면 에러를 낸다.
    """

    @property
    def enabled(self) -> bool:
        return False

    @property
    def model(self) -> str:
        return ""

    def embed(self, text: str) -> MemoryEmbedding:
        raise RuntimeError("vector search is disabled: embed must not be called")
