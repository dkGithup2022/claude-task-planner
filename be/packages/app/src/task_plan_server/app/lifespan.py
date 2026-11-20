from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import Engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    container = app.state.dishka_container
    container.get(Engine).dispose()  # 풀의 커넥션 정리 (컨테이너 close 는 dispose 를 부르지 않는다)
    container.close()
