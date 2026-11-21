import logging

from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.transaction import TransactionManager, transactional

from ..search_terms.embedding_of import embedding_of

logger = logging.getLogger(__name__)


class MemoryEmbeddingRefreshUsecase:
    """검색용 벡터가 비었거나 다른 모델로 만든 지식의 벡터를 다시 만든다.

    서버가 시작할 때 app 의 lifespan 이 부른다. 벡터 검색을 끈 동안 저장한 지식(벡터가 빔),
    DB 에 직접 넣은 지식, 모델을 바꾸기 전에 만든 벡터가 대상이다. 고친 시각은 바꾸지 않는다.
    """

    def __init__(
        self, tx: TransactionManager, repository: MemoryRepository, embedder: TextEmbedder
    ) -> None:
        self.tx = tx
        self._repository = repository
        self._embedder = embedder

    @transactional
    def execute(self) -> int:
        """다시 만든 지식 수. 벡터 검색이 꺼져 있으면 0."""
        if not self._embedder.enabled:
            return 0
        filled = 0
        for identity in self._repository.find_ids_without_embedding_of(self._embedder.model):
            memory = self._repository.find_write_by_id(identity)
            if memory is None:
                continue
            embedding = embedding_of(self._embedder, memory.theme, memory.body)
            self._repository.save_embedding(identity, embedding)
            filled += 1
        logger.info("Memory embeddings filled: count=%s", filled)
        return filled
