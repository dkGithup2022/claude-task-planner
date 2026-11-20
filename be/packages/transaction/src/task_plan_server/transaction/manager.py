from abc import ABC, abstractmethod
from contextlib import AbstractContextManager, nullcontext
from typing import Any


class TransactionManager(ABC):
    """Spring PlatformTransactionManager 에 해당하는 port. 구현은 persistence."""

    @abstractmethod
    def in_transaction(self) -> bool: ...

    @abstractmethod
    def begin(self) -> AbstractContextManager[Any]:
        """새 트랜잭션. 정상 종료 시 commit, 예외 시 rollback 후 재전파."""

    @abstractmethod
    def begin_nested(self) -> AbstractContextManager[Any]:
        """세이브포인트. Spring REQUIRES_NEW 의 근사치 — 바깥이 롤백되면 같이 롤백된다."""


class NoopTransactionManager(TransactionManager):
    """단위 테스트용. 아무것도 열지 않는다."""

    def in_transaction(self) -> bool:
        return False

    def begin(self) -> AbstractContextManager[Any]:
        return nullcontext()

    def begin_nested(self) -> AbstractContextManager[Any]:
        return nullcontext()
