from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MemoryEmbedding:
    """글 하나의 검색용 벡터와 그 벡터를 만든 모델 이름.

    모델이 다르면 벡터 길이(차원)도 다를 수 있어, 같은 모델로 만든 벡터끼리만 비교한다.
    """

    model: str
    vector: tuple[float, ...]
