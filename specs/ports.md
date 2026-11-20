# port

## plan_api (`port/plan_api/`)
계획 저장소. 계획, 노드, 간선, 계획 상태, 노드 상태. 원본은 나중의 서버 API 이고, 지금은 mock 구현이 task-plan-manager 저장소의 `.mockData/` 에 파일로 저장한다.
환경 변수: `TASK_PLAN_MANAGER_API` (mock | server, 없으면 mock), `TASK_PLAN_MANAGER_API_URL` (서버 주소), `TASK_PLAN_MANAGER_MOCK_DIR` (mock 폴더를 바꿀 때. 시험이 쓴다)

| 인터페이스 | 메서드 | 돌려주는 값 | 없을 때·실패 |
|---|---|---|---|
| PlanApiReader | get_plan(plan_id) | Plan (노드·간선 포함) | PlanNotFoundError |
| PlanApiWriter | create_plan(new_plan) | Plan (drafting, 노드·간선 없음) | |
| PlanApiWriter | add_node(plan_id, new_node) | PlanNode (todo) | PlanNotFoundError |
| PlanApiWriter | add_edge(plan_id, from_node_id, to_node_id) | PlanEdge. 같은 간선이 있으면 그것 | 노드가 없으면 PlanApiError |
| PlanApiWriter | update_node(plan_id, node_id, change) | PlanNode | 노드가 없으면 PlanApiError |
| PlanApiWriter | delete_node(plan_id, node_id) | None. 닿은 간선도 지움 | 이미 없으면 아무것도 안 함 |
| PlanApiWriter | delete_edge(plan_id, edge_id) | None | 이미 없으면 아무것도 안 함 |
| PlanApiWriter | set_plan_status(plan_id, status) | Plan | 허용 검사는 부르는 쪽이 `PlanStatus.can_move_to` 로 |

구현: `MockPlanApiReader`, `MockPlanApiWriter` (파일 `.mockData/plans/<plan_id>.json`, `.mockData/ids.json`), `DefaultPlanApiReader`, `DefaultPlanApiWriter` (서버 HTTP). 고르기: `plan_api_choice.plan_api_reader()`, `plan_api_writer()`. JSON 변환: `PlanJsonConverter` (응답과 mock 파일이 같은 모양), 요청 본문: `PlanApiRequestConverter`

dto: `NewPlan(title, request, persona_ids)`, `NewNode(title, kind, persona_ids, output_spec)`, `NodeChange(title?, kind?, persona_ids?, output_spec?, status?)`

## plan_folder (`port/local/plan_folder/`)
계획 폴더. CLI 를 부른 작업 폴더의 `.plan/<plan_id>/` 아래.

```
.plan/<plan_id>/
  command.md
  nodes/<node_id>/
    prompt.md  result.md  files/  run.json  runs/<회차>/
```

| 인터페이스 | 메서드 | 돌려주는 값 | 없을 때·실패 |
|---|---|---|---|
| PlanFolderReader | list_plan_ids() | tuple[int, ...] 작은 순 | 빈 튜플 |
| PlanFolderReader | read_command(plan_id) | str | PlanFolderMissingError |
| PlanFolderReader | read_prompt(plan_id, node_id) | str | None |
| PlanFolderReader | result_target(plan_id, node_id) | ResultTarget (절대 경로) | 만들지 않음 |
| PlanFolderReader | read_output(plan_id, node_id) | NodeOutput (회차, result.md, files) | result.md 가 없으면 None |
| PlanFolderReader | read_run(plan_id, node_id) | NodeRun | None |
| PlanFolderWriter | create_plan(plan_id, command_md) | None | 다른 명령서가 있으면 PlanFolderExistsError |
| PlanFolderWriter | write_prompt(plan_id, node_id, text) | None. 노드 폴더를 이때 만듦 | |
| PlanFolderWriter | write_result(plan_id, node_id, text) | None. 확인 노드처럼 우리 코드가 결과를 쓸 때 | |
| PlanFolderWriter | save_run(plan_id, node_id, run) | None | |
| PlanFolderWriter | archive_round(plan_id, node_id) | 새 회차 번호. prompt.md 는 복사, result.md·files/ 는 runs/<회차>/ 로 옮김. run.json 의 회차도 올려 저장 (상태 todo) | |
| PlanFolderReader | read_stop(plan_id) | StopMark (run_id, reason, node_ids, message). `.plan/<id>/stop.json` | None |
| PlanFolderWriter | save_stop(plan_id, mark) | None. 덮어씀. 이번 engine 실행에서 멈추기로 한 자리 (바깥 차례 안에서 앞 차례 결과를 못 읽어서) | |

구현: `DefaultPlanFolderReader`, `DefaultPlanFolderWriter`

dto: `ResultTarget(result_path, files_dir)`, `NodeOutput(round, result_path, files)`. 제목과 상태는 담지 않는다. 선행 노드의 제목·상태는 계획 저장소에서 읽어 노드를 시작하는 쪽이 합친다.

## 구현 고르기 (모든 API 포트)

워크플로 단계는 `Mock…` 이나 `Default…` 를 직접 고르지 않고 포트 폴더의 `*_api_choice.py` 함수를 쓴다. `TASK_PLAN_MANAGER_API=server` 면 서버 구현(`common/http/` 로 `TASK_PLAN_MANAGER_API_URL` 을 부름), 아니면 mock. mock 폴더와 mock id 는 `common/mock_data.py`.

## persona_api (`port/persona_api/`)
| 인터페이스 | 메서드 | 돌려주는 값 | 없을 때·실패 |
|---|---|---|---|
| PersonaApiReader | list_personas() | tuple[Persona, ...] | 빈 튜플 / PersonaApiError |

구현: `MockPersonaApiReader` (`.mockData/personas.json`. 없으면 1 dankim-persona, 2 be-developer 로 만듦), `DefaultPersonaApiReader` (GET /personas). 고르기: `persona_api_reader()`

## memory_api (`port/memory_api/`)
| 인터페이스 | 메서드 | 돌려주는 값 | 없을 때·실패 |
|---|---|---|---|
| MemoryApiReader | search(query) | tuple[MemorySearchHit, ...] | 빈 튜플 / MemoryApiError |
| MemoryApiWriter | create(new_memory) | memory_id | MemoryApiError |
| MemoryApiWriter | append(memory_id, addition) | memory_id | 지식이 없으면 MemoryApiError |

구현: `MockMemoryApiReader` (검색어와 상관없이 저장된 지식을 limit 개까지, 점수 1.0), `MockMemoryApiWriter` (`.mockData/memories.json`. 없으면 문서 예시의 "테이블 설계" 지식 두 개로 만듦), `DefaultMemoryApiReader`, `DefaultMemoryApiWriter` (POST /memories/search, /memories, /memories/{id}/append). 고르기: `memory_api_reader()`, `memory_api_writer()`

dto: `MemorySearchQuery(kind, query, persona_ids, theme?, limit)`, `MemorySearchHit(memory_id, kind, theme, body, score)`, `NewMemory(kind, theme, body, persona_ids, sources)`, `MemoryAddition(body, sources)`

검색한 지식을 글로 보일 때는 `****** KNOWLEDGE SEARCHED <n> ********` 머리로 구분한다 (사용자, 2026-11-19. 보이는 쪽에서 만든다)

