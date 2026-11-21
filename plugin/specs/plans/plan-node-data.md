# 계획: 계획·노드·간선과 로컬 계획 폴더의 데이터와 접근 인터페이스를 선언한다

## 요청

"전체에서 공통으로 쓸 workflow 말고 다른 영역에 있는 데이터들 먼저 선언하고 싶은데, 노드, 플랜, 그리고 로컬 파일에 대한 스펙과 거기 접근하는 인터페이스" (사용자, 2026-11-19)

근거 문서 (corbina/notes, re_code.html 탭 이름):
- 데이터·API: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-task-plan-manager-data-api.md "계획, 노드, 간선"
- 실행 데이터 (확정): /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-19-data-confirmed.md 1~5 절과 부록
- 계획 상태 바꾸기: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-flow-diagrams.md B 절 "계획 상태 바꾸기"

## 1. 평가

### 나누기

- 포트
  1. 계획 저장소: 계획, 노드, 간선, 계획 상태, 노드 상태를 읽고 쓴다. 원본은 나중의 서버 API 이고, 지금은 `.mockData/` 의 파일로 흉내 낸다.
  2. 계획 폴더: 작업 저장소의 `.plan/<plan_id>/` 아래 명령서 사본, 작업 지시, 결과, 실행 기록을 읽고 쓴다.
- 공통 기능: 없음. 경로 계산은 각 포트의 위치 파일에 둔다 (`common/paths.py` 는 고치지 않는 파일이다).
- 워크플로로 넘길 것: 다음 노드 계산(D 3-0), 노드 시작 때 선행 노드 결과를 모아 서브에이전트에게 넘기는 일, 계획 상태를 바꾸는 명령. 이번에는 이 일들이 쓸 데이터와 포트만 만든다.
- 이번 범위 밖: 페르소나 목록(GET /personas), 지식 검색·저장(/memories). A 2 단계와 3-1 단계가 쓰므로 다음 요청으로 둔다.

### tool-assess-port

**판정**: 미충족 (포트가 하나도 없다. 있는 것은 예시 `port/local/counter/` 뿐)

**접근별 판정**

| 접근 | 판정 | 포트 | 메서드 |
|---|---|---|---|
| 계획 조회 (노드, 간선 포함) | 미충족 | plan_api (신규) | PlanApiReader.get_plan(plan_id) -> Plan |
| 계획 만들기 | 미충족 | plan_api | PlanApiWriter.create_plan(new_plan) -> Plan |
| 노드 저장 | 미충족 | plan_api | PlanApiWriter.add_node(plan_id, new_node) -> PlanNode |
| 간선 저장 | 미충족 | plan_api | PlanApiWriter.add_edge(plan_id, from_node_id, to_node_id) -> PlanEdge |
| 노드 고치기 (상태 포함) | 미충족 | plan_api | PlanApiWriter.update_node(plan_id, node_id, change) -> PlanNode |
| 노드 지우기 | 미충족 | plan_api | PlanApiWriter.delete_node(plan_id, node_id) -> None |
| 간선 지우기 | 미충족 | plan_api | PlanApiWriter.delete_edge(plan_id, edge_id) -> None |
| 계획 상태 바꾸기 | 미충족 | plan_api | PlanApiWriter.set_plan_status(plan_id, status) -> Plan |
| 이 저장소의 계획 id 목록 | 미충족 | local/plan_folder (신규) | PlanFolderReader.list_plan_ids() -> tuple[int, ...] |
| 명령서 사본 쓰기·읽기 | 미충족 | local/plan_folder | PlanFolderWriter.create_plan(plan_id, command_md), PlanFolderReader.read_command(plan_id) |
| 작업 지시 쓰기·읽기 | 미충족 | local/plan_folder | PlanFolderWriter.write_prompt(...), PlanFolderReader.read_prompt(...) |
| 서브에이전트가 쓸 결과 위치 | 미충족 | local/plan_folder | PlanFolderReader.result_target(plan_id, node_id) -> ResultTarget |
| 노드 결과 읽기 | 미충족 | local/plan_folder | PlanFolderReader.read_output(plan_id, node_id) -> NodeOutput \| None |
| 실행 기록 쓰기·읽기 | 미충족 | local/plan_folder | PlanFolderWriter.save_run(...), PlanFolderReader.read_run(...) |
| 이전 회차 보관 | 미충족 | local/plan_folder | PlanFolderWriter.archive_round(plan_id, node_id) -> int |

**포트 계획**

- [신규] port/plan_api/ — 계획 저장소. 나중에 서버 API 로 바꾸는 포트
  - PlanApiReader
    - get_plan(plan_id: int) -> Plan — 노드와 간선까지 담은 계획. 없으면 PlanNotFoundError
  - PlanApiWriter
    - create_plan(new_plan: NewPlan) -> Plan — 상태는 drafting, 노드·간선은 비어 있음. id 는 저장소가 준다
    - add_node(plan_id: int, new_node: NewNode) -> PlanNode — 상태는 todo. id 는 저장소가 준다
    - add_edge(plan_id: int, from_node_id: int, to_node_id: int) -> PlanEdge — 양 끝 노드가 없으면 PlanApiError
    - update_node(plan_id: int, node_id: int, change: NodeChange) -> PlanNode — `NodeChange` 에서 값이 있는 필드만 바꾼다
    - delete_node(plan_id: int, node_id: int) -> None — 그 노드에 닿은 간선도 지운다
    - delete_edge(plan_id: int, edge_id: int) -> None
    - set_plan_status(plan_id: int, status: PlanStatus) -> Plan — 허용하는 바꾸기인지는 여기서 보지 않는다 (model 의 동작으로 호출하는 쪽이 먼저 검사)
  - 구현: 지금은 mock 하나. `.mockData/` 아래 파일로 저장
    - 이름: `MockPlanApiReader`, `MockPlanApiWriter` (사용자 확인 필요. 번들 규칙은 구현 이름을 `Default` 로 시작하는데, 나중의 서버 구현에 그 이름을 남겨 두려는 것이다)
    - 파일: `.mockData/plans/<plan_id>.json` (계획 하나에 노드와 간선을 모두 담음), `.mockData/ids.json` (다음 계획·노드·간선 id)
    - 변환기: `MockPlanFileConverter` (`to_file` / `to_data`). JSON 모양은 데이터·API 문서의 GET /plans/{plan_id} 응답과 같게 둔다. 서버로 바꿀 때 같은 모양을 받기 위해서다
  - 예외: PlanNotFoundError, PlanApiError
  - dto: NewPlan, NewNode, NodeChange (요청 모양. 아래 model 층 요청에는 넣지 않음)
    - NewPlan(title: str, request: str, persona_ids: tuple[int, ...])
    - NewNode(title: str, kind: NodeKind, persona_ids: tuple[int, ...], output_spec: str)
    - NodeChange(title: str | None, kind: NodeKind | None, persona_ids: tuple[int, ...] | None, output_spec: str | None, status: PlanNodeStatus | None)
  - 새 의존성 없음

- [신규] port/local/plan_folder/ — 계획 폴더
  - 위치 (`plan_folder_location.py`): 작업 폴더의 `.plan/<plan_id>/`, 노드는 `nodes/<node_id>/`. 작업 폴더는 CLI 를 부른 폴더(`Path.cwd()`)다
  - PlanFolderReader
    - list_plan_ids() -> tuple[int, ...] — `.plan/` 아래 폴더 이름 가운데 정수인 것. 없으면 빈 튜플
    - read_command(plan_id: int) -> str — 없으면 PlanFolderMissingError
    - read_prompt(plan_id: int, node_id: int) -> str | None — 없으면 None
    - result_target(plan_id: int, node_id: int) -> ResultTarget — 서브에이전트가 쓸 `result.md`, `files/` 의 절대 경로. 파일을 만들지는 않는다
    - read_output(plan_id: int, node_id: int) -> NodeOutput | None — 마지막 회차의 결과 위치와 파일 목록. `result.md` 가 없으면 None
    - read_run(plan_id: int, node_id: int) -> NodeRun | None — `run.json`. 없으면 None
  - PlanFolderWriter
    - create_plan(plan_id: int, command_md: str) -> None — 폴더와 `command.md`. 이미 있으면 덮어쓰지 않고 PlanFolderExistsError
    - write_prompt(plan_id: int, node_id: int, text: str) -> None — 노드 폴더가 없으면 만든다
    - save_run(plan_id: int, node_id: int, run: NodeRun) -> None
    - archive_round(plan_id: int, node_id: int) -> int — 지금의 `prompt.md`, `result.md`, `files/` 를 `runs/<회차>/` 로 옮기고 새 회차를 돌려준다
  - 변환기: `NodeRunFileConverter` (`run.json` ↔ NodeRun). 나머지는 md 글 그대로
  - 예외: PlanFolderMissingError, PlanFolderExistsError
  - dto: ResultTarget(result_path: Path, files_dir: Path), NodeOutput(round: int, result_path: Path, files: tuple[Path, ...])

**model 층 요청**

- 대상: plan (신규)
- 클래스: Plan (plan/plan.py), PlanNode (plan/plan_node.py), PlanEdge (plan/plan_edge.py), PlanStatus, PlanNodeStatus, NodeKind (enum)
- 동작: Plan.prerequisites(node_id) -> tuple[int, ...], PlanStatus.can_move_to(to) -> bool
- 쓰는 곳: PlanApiReader.get_plan, PlanApiWriter 전부
- 이유: 계획과 노드는 이 도구가 주로 다루는 도메인 데이터다

- 대상: node_run (신규)
- 클래스: NodeRun (node_run/node_run.py), ReadInput (node_run/read_input.py)
- 쓰는 곳: PlanFolderReader.read_run, PlanFolderWriter.save_run
- 이유: 회차와 확인 대기는 로컬 실행 기록에만 둔다 (데이터·API 문서, 2026-11-18)

**사용자 확인 필요**

1. mock 구현의 이름 (`Mock...` 으로 둘지, 번들 규칙대로 `Default...` 로 둘지)
2. `.mockData/` 의 기준 폴더. 계획 폴더(`.plan/`)처럼 CLI 를 부른 작업 폴더로 둘지, 도구 저장소(claude-task-planner) 쪽 고정 위치로 둘지
3. 확정 문서와 다른 점: 확정 문서 3 절은 `read_result` 가 선행 노드의 제목과 상태까지 돌려준다고 적었다. 제목과 상태의 원본은 계획 저장소이므로, 계획 폴더 포트는 로컬에 있는 것(회차, 결과 위치, 파일 목록)만 돌려주고 제목·상태와 합치는 일은 쓰는 쪽(노드 시작 단계)이 하도록 나눈다. 이름도 `read_result` 대신 `read_output` 으로 한다

### tool-assess-model

**판정**: 미충족 (model 이 없다. 있는 것은 예시 `model/counter/` 뿐)

**클래스별 계획**

- [신규] model/plan/plan.py — Plan
  - 필드: plan_id: int, title: str, request: str, persona_ids: tuple[int, ...], status: PlanStatus, created_at: str, nodes: tuple[PlanNode, ...], edges: tuple[PlanEdge, ...]
  - 동작: node(node_id) -> PlanNode (없으면 KeyError), prerequisites(node_id) -> tuple[int, ...] (간선으로 바로 이어진 앞 노드 id)
- [신규] model/plan/plan_node.py — PlanNode
  - 필드: node_id: int, title: str, kind: NodeKind, persona_ids: tuple[int, ...], output_spec: str, status: PlanNodeStatus
- [신규] model/plan/plan_edge.py — PlanEdge
  - 필드: edge_id: int, from_node_id: int, to_node_id: int
- [신규] model/plan/plan_status.py — PlanStatus(StrEnum): DRAFTING = "drafting", REVIEWING = "reviewing", APPROVED = "approved", REJECTED = "rejected", RUNNING = "running", DONE = "done"
  - 동작: can_move_to(to: PlanStatus) -> bool. 허용: 없음 → drafting, drafting → reviewing, reviewing → approved 또는 rejected, approved → running, running → done (흐름 도식 B 절의 가안)
- [신규] model/plan/plan_node_status.py — PlanNodeStatus(StrEnum): TODO = "todo", RUNNING = "running", DONE = "done", FAILED = "failed", SKIPPED = "skipped"
  - 이름에 `Plan` 을 붙인다. 번들 engine 에 `NodeStatus` 가 이미 있어서, 계획 노드와 engine 노드를 섞지 않기 위해서다 (확정 문서 부록)
- [신규] model/plan/node_kind.py — NodeKind(StrEnum): DOCUMENT = "document", RESEARCH = "research", CODE = "code", HITL = "hitl"
- [신규] model/node_run/node_run.py — NodeRun
  - 필드: round: int, status: PlanNodeStatus, started_at: str | None, finished_at: str | None, read_inputs: tuple[ReadInput, ...], confirm: str | None, skipped_reason: str | None
  - 동작: start(now: str) -> NodeRun, finish(status: PlanNodeStatus, now: str) -> NodeRun
- [신규] model/node_run/read_input.py — ReadInput
  - 필드: node_id: int, round: int

**사용자 확인 필요**

- 계획 상태 값 목록: 데이터·API 문서에는 "값 목록은 미정"이고, 흐름 도식 B 절에 가안이 있다. 가안대로 enum 을 만들지

## 2. 구현 계획

**평가 요약**
- port: 미충족 — port/plan_api/ (계획 저장소, 지금은 mock), port/local/plan_folder/ (계획 폴더) 신규
- model: 미충족 — model/plan/ (계획, 노드, 간선, 상태 enum), model/node_run/ (실행 기록) 신규
- 공통 기능: 없음

**정한 것** (근거 문서에서)
- id 는 정수. 계획 저장소가 준다
- 노드의 선행 관계는 저장하지 않고 간선에서 계산한다
- 계획 폴더: `.plan/<plan_id>/command.md`, `nodes/<node_id>/{prompt.md, result.md, files/, run.json, runs/<회차>/}`. `plan.md`, `node_spec.md` 는 두지 않는다
- mock 은 `.mockData/` 아래 파일
- 그래프 버전은 두지 않는다

**사용자 확인 (2026-11-19)**
1. mock 구현 이름은 `MockPlanApiReader`, `MockPlanApiWriter` 로 한다
2. `.mockData/` 는 claude-task-planner 저장소 쪽에 둔다. 위치는 이 패키지 파일에서 저장소 루트를 계산한다. 시험과 다른 위치가 필요할 때는 환경 변수 `TASK_PLANNER_MOCK_DIR` 로 바꾼다
3. 계획 폴더 포트는 로컬에 있는 것(회차, 결과 위치, 파일 목록)만 `read_output` 으로 돌려준다. 제목·상태와 합치는 일은 노드를 시작하는 쪽이 한다
4. 계획 상태는 흐름 도식 B 절의 가안대로 enum 을 만든다. 진행 중 이상하면 바꾼다

번들 규칙과 다른 점: 번들은 파일 포트의 위치를 데이터 폴더(`common.paths.home()`) 아래에 두게 한다. 이 계획은 사용자가 정한 대로 계획 폴더를 작업 폴더의 `.plan/` 에, mock 을 저장소의 `.mockData/` 에 둔다.

**구현 순서**
1. add-model: model/plan/ (6개 파일), model/node_run/ (2개 파일), 시험, specs/models.md
2. add-port: port/plan_api/ (인터페이스 2, mock 구현 2, 변환기, 위치, 예외 2, dto 3), 시험, specs/ports.md
3. add-port: port/local/plan_folder/ (인터페이스 2, 구현 2, 변환기, 위치, 예외 2, dto 2), 시험, specs/ports.md
4. 최종 검증: ruff, lint-imports, mypy, pytest

## 3. 진행 기록

### 2026-11-19
- add-model: model/plan/ (plan.py, plan_node.py, plan_edge.py, plan_status.py, plan_node_status.py, node_kind.py), model/node_run/ (node_run.py, read_input.py), 시험 tests/model/plan/test_plan.py, tests/model/node_run/test_node_run.py, specs/models.md
- add-port: port/plan_api/ (인터페이스 2, mock 구현 2, mock_plan_files.py, 변환기, 위치, 예외 2, dto 3), 시험 tests/port/plan_api/test_mock_plan_api.py
- add-port: port/local/plan_folder/ (인터페이스 2, 구현 2, 변환기, 위치, 예외 2, dto 2), 시험 tests/port/plan_folder/test_plan_folder.py, specs/ports.md
- tests/conftest.py: 모든 시험이 임시 폴더를 mock 폴더로 쓰게 `TASK_PLANNER_MOCK_DIR` 을 바꾸는 픽스처를 더함
- 최종 검증: ruff 통과, import 검사 계약 4개 지킴, mypy 225개 파일 문제 없음, pytest 55개 통과
- 리뷰 (별도 에이전트): `archive_round` 를 연달아 부르면 앞 회차 결과를 덮어쓰는 문제 1건. `archive_round` 가 run.json 의 회차를 직접 올려 저장하도록 고치고 시험을 더함
- 가독성 정리 (사용자 규칙, CLAUDE.md): 줄임말 변수를 풀어 쓰고, 인터페이스 구현 메서드마다 하는 일 주석을 달고, 긴 메서드를 뜻 단위 함수로 나눔 (mock_plan_api_writer, mock_plan_file_converter, mock_plan_files, default_plan_folder_reader/writer, node_run_file_converter, plan.py, 시험 4개). 동작은 바꾸지 않음. 검증: ruff, import 계약 4개, mypy, pytest 56개 통과
