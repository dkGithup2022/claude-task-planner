from abc import ABC, abstractmethod

from task_plan_server.model.memory.memory_embedding import MemoryEmbedding


class TextEmbedder(ABC):
    """글을 검색용 벡터로 바꾸는 port. 벡터 검색을 끄면 enabled 가 False 인 구현을 쓴다."""

    @property
    @abstractmethod
    def enabled(self) -> bool:
        """벡터 검색을 켰는지. False 이면 embed 를 부르지 않는다."""

    @property
    @abstractmethod
    def model(self) -> str:
        """지금 쓰는 모델 이름. 저장한 벡터가 이 모델로 만든 것인지 가릴 때 쓴다."""

    @abstractmethod
    def embed(self, text: str) -> MemoryEmbedding:
        """글의 벡터. enabled 가 False 이면 에러를 낸다."""
