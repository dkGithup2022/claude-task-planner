from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.model.memory.memory_search_terms import MemorySearchTerms


def memory_search_terms_of(tokenizer: TextTokenizer, theme: str, body: str) -> MemorySearchTerms:
    """저장(인덱싱)할 지식의 검색용 낱말. 작업 이름과 본문을 따로 나눈다 (무게를 따로 붙이려고)."""
    return MemorySearchTerms(theme=tokenizer.tokens(theme), body=tokenizer.tokens(body))
