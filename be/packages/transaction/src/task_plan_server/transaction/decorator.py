from collections.abc import Callable
from functools import wraps
from typing import Any

from .manager import TransactionManager


def transactional[R](method: Callable[..., R]) -> Callable[..., R]:
    """Spring @Transactional(propagation=REQUIRED) 대응.

    - 대상 객체는 self.tx (TransactionManager) 를 가져야 한다.
    - 이미 열린 트랜잭션이 있으면 합류하고, 없으면 새로 열어 메서드 종료 시 commit 한다.
    - 모든 예외에서 rollback 후 재전파한다 (Spring 과 달리 checked/unchecked 구분 없음).
    """

    @wraps(method)
    def wrapper(self: Any, *args: Any, **kwargs: Any) -> R:
        tx = getattr(self, "tx", None)
        if not isinstance(tx, TransactionManager):
            raise AttributeError(
                f"{type(self).__name__}.tx 가 TransactionManager 가 아니다. "
                "생성자에서 self.tx 를 설정해야 @transactional 을 쓸 수 있다."
            )
        if tx.in_transaction():
            return method(self, *args, **kwargs)
        with tx.begin():
            return method(self, *args, **kwargs)

    return wrapper
