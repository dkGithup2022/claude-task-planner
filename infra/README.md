# 배포 (docker compose)

postgres, 서버(be), 웹(web) 세 컨테이너를 한 번에 띄운다.

| 컨테이너 | 이미지 | 밖으로 여는 포트 | 하는 일 |
|---|---|---|---|
| db | postgres:16-alpine | 없음 | 데이터는 볼륨 `pgdata` 에 남는다 |
| be | `be/Dockerfile` | `BE_PORT` (기본 8000) | 시작할 때 `alembic upgrade head` 로 테이블을 맞추고 uvicorn 을 띄운다 |
| web | `web/Dockerfile` | `WEB_PORT` (기본 3000) | Next standalone. `BACKEND_API_URL=http://be:8000` 으로 서버를 부른다 |

시작 순서: db 가 준비되면(pg_isready) be, be 가 응답하면(`GET /api/personas`) web.

## 띄우기

저장소 맨 위에서:

```bash
cp infra/.env.example infra/.env   # POSTGRES_PASSWORD 를 바꾼다
docker compose -f infra/docker-compose.yml up -d --build
```

- 웹: http://localhost:3000 (WEB_PORT)
- 서버: http://localhost:8000/api (BE_PORT). CLI 는 `TASK_PLANNER_API_URL` 을 이 주소로 둔다
- 개발 서버가 같은 포트를 쓰고 있으면 `infra/.env` 에서 `BE_PORT`, `WEB_PORT` 를 바꾼다

처음 빌드는 기본 이미지를 받고 `npm ci`, `next build` 를 하느라 10분쯤 걸린다. 그 뒤에는 바뀐 층만 다시 만든다.

## 데이터 옮기기 (처음 한 번)

새 DB 는 비어 있다. tpm-trial 데이터(`be/seed/tpm-trial`)를 넣으려면:

```bash
docker compose -f infra/docker-compose.yml exec be python scripts/import_mock_data.py
```

## 그 밖

```bash
docker compose -f infra/docker-compose.yml logs -f be    # 서버 로그
docker compose -f infra/docker-compose.yml down          # 끄기 (데이터는 남는다)
docker compose -f infra/docker-compose.yml down -v       # 끄고 데이터까지 지운다
```

- 개발할 때 쓰는 DB 하나짜리 compose 는 `be/docker-compose.yml` 이다. 이것과 따로 돈다
- 웹의 mock 여부(`NEXT_PUBLIC_USE_MOCK`)는 브라우저 번들에 들어가므로 이미지 빌드 때 `false` 로 정해져 있다
