from contextlib import AbstractContextManager
from typing import Any

from sqlalchemy.orm import Session

from task_plan_server.transaction import TransactionManager


class DefaultTransactionManager(TransactionManager):
    def __init__(self, session: Session) -> None:
        self._session = session

    def in_transaction(self) -> bool:
        return self._session.in_transaction()

    def begin(self) -> AbstractContextManager[Any]:
        return self._session.begin()

    def begin_nested(self) -> AbstractContextManager[Any]:
        return self._session.begin_nested()
