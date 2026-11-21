from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemorySearchTerms:
    """지식 하나의 검색용 낱말. 작업 이름에서 나온 것과 본문에서 나온 것을 나눠 둔다.

    저장할 때 작업 이름 낱말에 더 큰 무게를 붙이려고 나눈다. 낱말은 형태소로 나눈 것
    (명사, 영문, 동사·형용사 어간) 이고, 나누는 규칙은 service 의 search_terms 에 있다.
    """

    theme: tuple[str, ...]
    body: tuple[str, ...]
