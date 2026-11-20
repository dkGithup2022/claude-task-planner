# task-plan-server

task-plan-manager 의 서버. FastAPI / SQLAlchemy 2.0 / Postgres 기반 Hexagonal uv workspace 백엔드.

## 실행

    docker compose up -d db
    cp .env.example .env
    uv sync --all-groups
    uv run alembic -c packages/schema/alembic.ini upgrade head
    uv run uvicorn task_plan_server.app.main:create_app --factory --reload --port 8000

- OpenAPI: http://localhost:8000/docs
- CLI 에서 쓰기: `TASK_PLAN_MANAGER_API=server`, `TASK_PLAN_MANAGER_API_URL=http://localhost:8000/api` (서버 경로는 모두 /api 로 시작한다)

## 패키지

- app — 실행 진입점, DI 바인딩, 예외 핸들러
- api — APIRouter / Pydantic DTO
- service — Reader / Writer / Usecase
- infrastructure — Repository port
- persistence — Entity, EntityQuery(ORM), JoinQuery(SQL), Default{Domain}Repository(port 구현체)
- transaction — TransactionManager 계약 + @transactional
- my_logging — JSON 한 줄 로깅, 요청 컨텍스트 키
- model — 도메인 모델 + AuditFields
- schema — Alembic migration
- exception — 공통 예외
