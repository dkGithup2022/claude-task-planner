from abc import ABC, abstractmethod


class TextTokenizer(ABC):
    """글을 검색용 낱말로 나누는 port. 구현(형태소 분석기)을 바꿔 끼울 수 있게 따로 둔다."""

    @abstractmethod
    def tokens(self, text: str) -> tuple[str, ...]:
        """검색에 쓸 낱말 (명사, 영문, 동사·형용사 어간).

        나온 순서대로, 겹쳐도 그대로. 없으면 ().
        """
