import logging

from task_plan_server.infrastructure.memory.memory_repository import MemoryRepository
from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.transaction import TransactionManager, transactional

from ..search_terms.memory_search_terms_of import memory_search_terms_of

logger = logging.getLogger(__name__)


class MemorySearchTermsRefreshUsecase:
    """검색용 낱말이 빈 지식을 채운다. 서버가 시작할 때 app 의 lifespan 이 부른다.

    API 로 저장한 지식은 저장할 때 낱말이 생긴다. 비어 있는 것은 DB 에 직접 넣은 지식
    (scripts/import_mock_data.py) 과 낱말 열을 더하기 전에 있던 지식뿐이다.
    고친 시각은 바꾸지 않는다.
    """

    def __init__(
        self, tx: TransactionManager, repository: MemoryRepository, tokenizer: TextTokenizer
    ) -> None:
        self.tx = tx
        self._repository = repository
        self._tokenizer = tokenizer

    @transactional
    def execute(self) -> int:
        """채운 지식 수."""
        filled = 0
        for identity in self._repository.find_ids_without_search_terms():
            memory = self._repository.find_write_by_id(identity)
            if memory is None:
                continue
            terms = memory_search_terms_of(self._tokenizer, memory.theme, memory.body)
            self._repository.save_search_terms(identity, terms)
            filled += 1
        logger.info("Memory search terms filled: count=%s", filled)
        return filled
