# 서버 이미지. 시작할 때 테이블을 최신으로 맞추고(alembic upgrade head) uvicorn 을 띄운다.
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    APP_ENV=prod

WORKDIR /app

# 의존성 층을 먼저 만들어 소스만 바뀌면 다시 설치하지 않게 한다
COPY pyproject.toml uv.lock ./
RUN --mount=type=bind,source=packages,target=/tmp/src \
    for dir in /tmp/src/*/; do \
      name=$(basename "$dir"); mkdir -p "packages/$name"; cp "$dir/pyproject.toml" "packages/$name/"; \
    done && \
    uv sync --frozen --no-dev --no-install-workspace

COPY packages ./packages
COPY scripts ./scripts
COPY seed ./seed
RUN uv sync --frozen --no-dev

EXPOSE 8000
CMD ["sh", "-c", "alembic -c packages/schema/alembic.ini upgrade head && exec uvicorn task_plan_server.app.main:create_app --factory --host 0.0.0.0 --port 8000"]
