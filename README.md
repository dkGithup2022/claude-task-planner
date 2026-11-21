# claude-task-planner

## 1. 서버 띄우기

docker 가 필요합니다. 플러그인을 설치하면(아래 2절) 이 저장소 전체가
`~/.claude/plugins/marketplaces/claude-task-planner/` 에 받아집니다. 그 폴더에서 띄웁니다.

```bash
cd ~/.claude/plugins/marketplaces/claude-task-planner
cp infra/.env.example infra/.env      # POSTGRES_PASSWORD 를 바꿉니다
docker compose -f infra/docker-compose.yml up -d --build
```

- 서버: http://localhost:8000/api
- 웹: http://localhost:3000
- 처음 빌드는 10분쯤 걸립니다. 포트를 바꾸려면 `infra/.env` 의 `BE_PORT`, `WEB_PORT` 를 고칩니다
- 끄기: `docker compose -f infra/docker-compose.yml down` (데이터는 남습니다)

## 2. CLI 순서와 역할

uv 가 필요합니다.

설치 (Claude Code 에서):

```
/plugin marketplace add dkGithup2022/claude-task-planner
/plugin install task-planner@claude-task-planner
```

서버 연결: 작업 폴더의 `.claude/settings.local.json` 에 넣습니다. 넣지 않으면 서버 대신 mock 데이터를 씁니다.

```json
{
  "env": {
    "TASK_PLANNER_API": "server",
    "TASK_PLANNER_API_URL": "http://localhost:8000/api"
  }
}
```

| 순서 | 명령 | 하는 일 |
|---|---|---|
| 1 | `/task-planner:run make_plan <할 일>` | 할 일을 작업 노드로 나눈 계획을 만듭니다. 계획은 검토 중 상태로 저장됩니다 |
| 2 | (대화) | 계획을 보인 뒤 대화로 노드와 지시할 내용을 고칩니다. Claude 가 plan-feedback, plan-edit 을 부릅니다 |
| 3 | `/task-planner:plan-go <계획 id>` | 고친 내용에서 지식을 다듬어 저장하고, 계획을 승인으로 확정합니다 |
|   | `/task-planner:plan-cancel <계획 id>` | 지식을 다듬어 저장하고, 계획을 불허로 확정합니다 |
| 4 | `/task-planner:plan-run <계획 id>` | 승인된 계획을 노드 순서대로 실행합니다 |

계획 id 를 빼면 이 작업 폴더의 계획 목록을 보입니다.
