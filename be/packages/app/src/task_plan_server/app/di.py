from collections.abc import Iterator

from dishka import Container, Provider, Scope, from_context, make_container, provide
from fastapi import Request
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from task_plan_server.api.auth import CurrentUser, resolve_current_user
from task_plan_server.my_logging import set_context
from task_plan_server.persistence.session import create_db_engine, create_session_factory
from task_plan_server.persistence.transaction import DefaultTransactionManager
from task_plan_server.transaction import TransactionManager

from .providers.memory_provider import MemoryProvider
from .providers.persona_provider import PersonaProvider
from .providers.plan_edge_provider import PlanEdgeProvider
from .providers.plan_node_provider import PlanNodeProvider
from .providers.plan_provider import PlanProvider
from .settings import Settings


class AppProvider(Provider):
    """앱 수명(싱글턴). Spring 싱글턴 빈에 해당하는 것만 둔다."""

    scope = Scope.APP

    @provide
    def settings(self) -> Settings:
        return Settings()

    @provide
    def engine(self, settings: Settings) -> Engine:
        return create_db_engine(
            settings.database_url,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            echo=settings.db_echo,
        )

    @provide
    def session_factory(self, engine: Engine) -> sessionmaker[Session]:
        return create_session_factory(engine)


class RequestProvider(Provider):
    """요청 수명. Session 과 TransactionManager 는 요청당 하나."""

    scope = Scope.REQUEST

    request = from_context(provides=Request)

    @provide
    def session(self, factory: sessionmaker[Session]) -> Iterator[Session]:
        with factory() as session:  # close() 가 미커밋 내용을 롤백
            yield session

    @provide
    def transaction_manager(self, session: Session) -> TransactionManager:
        return DefaultTransactionManager(session)

    @provide
    def current_user(self, request: Request, settings: Settings) -> CurrentUser:
        user = resolve_current_user(request, settings.env)
        set_context("user_id", user.user_id)  # 이후 이 요청의 모든 로그 줄에 붙는다
        return user


# add-usecase 스킬이 app/providers/{domain}_provider.py 를 만들고 여기에 등록한다 (C-10).
DOMAIN_PROVIDERS: list[Provider] = [
    PlanProvider(),
    PlanNodeProvider(),
    PlanEdgeProvider(),
    MemoryProvider(),
    PersonaProvider(),
]


def build_container(*extra: Provider) -> Container:
    return make_container(AppProvider(), RequestProvider(), *DOMAIN_PROVIDERS, *extra)
