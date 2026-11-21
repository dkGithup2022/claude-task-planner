from dishka import Provider, Scope, provide

from task_plan_server.infrastructure.memory.knowledge_searcher import KnowledgeSearcher
from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_embedder import TextEmbedder
from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.persistence.memory.default_knowledge_searcher import DefaultKnowledgeSearcher
from task_plan_server.persistence.memory.disabled_text_embedder import DisabledTextEmbedder
from task_plan_server.persistence.memory.fastembed_text_embedder import FastembedTextEmbedder
from task_plan_server.persistence.memory.kiwi_text_tokenizer import KiwiTextTokenizer
from task_plan_server.persistence.memory.memory_entity_query import MemoryEntityQuery
from task_plan_server.persistence.memory.memory_repository import DefaultMemoryRepository
from task_plan_server.service.memory.impl.default_memory_reader import DefaultMemoryReader
from task_plan_server.service.memory.impl.default_memory_writer import DefaultMemoryWriter
from task_plan_server.service.memory.memory_reader import MemoryReader
from task_plan_server.service.memory.memory_writer import MemoryWriter
from task_plan_server.service.memory.usecase.memory_create_usecase import MemoryCreateUsecase
from task_plan_server.service.memory.usecase.memory_delete_usecase import MemoryDeleteUsecase
from task_plan_server.service.memory.usecase.memory_embedding_refresh_usecase import (
    MemoryEmbeddingRefreshUsecase,
)
from task_plan_server.service.memory.usecase.memory_search_terms_refresh_usecase import (
    MemorySearchTermsRefreshUsecase,
)
from task_plan_server.service.memory.usecase.memory_update_usecase import MemoryUpdateUsecase

from ..settings import Settings


class MemoryProvider(Provider):
    scope = Scope.REQUEST

    entity_query = provide(MemoryEntityQuery)
    repository = provide(DefaultMemoryRepository, provides=MemoryRepository)
    searcher = provide(DefaultKnowledgeSearcher, provides=KnowledgeSearcher)
    # kiwi 는 모델을 읽느라 1 초 남짓 걸려 앱에 하나만 둔다
    tokenizer = provide(KiwiTextTokenizer, provides=TextTokenizer, scope=Scope.APP)
    reader = provide(DefaultMemoryReader, provides=MemoryReader)
    writer = provide(DefaultMemoryWriter, provides=MemoryWriter)
    create_usecase = provide(MemoryCreateUsecase)
    update_usecase = provide(MemoryUpdateUsecase)
    delete_usecase = provide(MemoryDeleteUsecase)
    search_terms_refresh_usecase = provide(MemorySearchTermsRefreshUsecase)
    embedding_refresh_usecase = provide(MemoryEmbeddingRefreshUsecase)

    @provide(scope=Scope.APP)
    def embedder(self, settings: Settings) -> TextEmbedder:
        """벡터 검색이 꺼져 있으면 모델을 띄우지 않는다.

        켜면 모델을 읽느라 시간이 걸려 앱에 하나만 둔다.
        """
        if not settings.memory_search_vector:
            return DisabledTextEmbedder()
        return FastembedTextEmbedder(
            settings.memory_search_vector_model, settings.memory_search_vector_dimension
        )
