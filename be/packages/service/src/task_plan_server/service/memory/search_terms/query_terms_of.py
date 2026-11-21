from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer


def query_terms_of(tokenizer: TextTokenizer, query: str) -> tuple[str, ...]:
    """검색어의 낱말. 저장할 때와 같은 tokenizer 로 나눠야 맞는다. 겹친 낱말은 처음 것만 둔다."""
    return tuple(dict.fromkeys(tokenizer.tokens(query)))
