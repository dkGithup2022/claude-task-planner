"""가장 단순한 검색 점수 (글자 맞추기).

나중에 벡터 검색 등으로 바꿀 때 이 파일과 검색 구현만 갈아 끼운다.
"""

THEME_WEIGHT = 2  # 낱말이 작업 이름에 있을 때
BODY_WEIGHT = 1  # 낱말이 본문에 있을 때


def query_words(query: str) -> list[str]:
    """검색어를 공백으로 나눈 낱말. 대소문자는 무시한다."""
    return [word.lower() for word in query.split()]


def text_match_score(words: list[str], theme: str, body: str) -> float:
    """낱말마다 작업 이름에 있으면 2, 본문에 있으면 1 을 더해 (낱말 수 × 3) 으로 나눈 0~1."""
    if not words:
        return 0.0
    theme_text, body_text = theme.lower(), body.lower()
    total = sum(
        (THEME_WEIGHT if word in theme_text else 0) + (BODY_WEIGHT if word in body_text else 0)
        for word in words
    )
    return total / (len(words) * (THEME_WEIGHT + BODY_WEIGHT))
