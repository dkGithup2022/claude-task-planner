import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from dishka import Container
from fastapi import FastAPI
from sqlalchemy import Engine

from task_plan_server.infrastructure.memory.text_tokenizer import TextTokenizer
from task_plan_server.service.memory.usecase.memory_search_terms_refresh_usecase import (
    MemorySearchTermsRefreshUsecase,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    container = app.state.dishka_container
    warm_up_tokenizer(container)
    fill_empty_search_terms(container)
    yield
    container.get(Engine).dispose()  # 풀의 커넥션 정리 (컨테이너 close 는 dispose 를 부르지 않는다)
    container.close()


def warm_up_tokenizer(container: Container) -> None:
    """형태소 분석기를 미리 한 번 돌린다.

    kiwi 는 처음 나눌 때 모델을 읽느라 수 초가 걸리고, 그동안 다른 요청은 잠금에서 기다린다.
    시작할 때 이 시간을 써서 첫 검색·저장이 느리지 않게 한다. 실패해도 서버는 뜬다.
    """
    try:
        container.get(TextTokenizer).tokens("준비")
    except Exception:
        logger.exception("Text tokenizer warm-up failed")


def fill_empty_search_terms(container: Container) -> None:
    """검색용 낱말이 빈 지식을 채운다 (사용자, 2026-11-21: 서버가 시작할 때 스스로 채운다).

    DB 에 직접 넣은 지식도 다음 시작 때 검색에 나오게 하려고.
    실패해도 서버는 뜬다 (그 지식이 검색에 나오지 않을 뿐이다).
    """
    try:
        with container() as request_container:
            request_container.get(MemorySearchTermsRefreshUsecase).execute()
    except Exception:
        logger.exception("Memory search terms fill failed")
