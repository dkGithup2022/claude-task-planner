# 워크플로: plan_run (D 계획 실행)

승인된 계획의 계획 노드를 간선 순서대로 실행한다. `/task-planner:plan-run <id>`.
진행 방식: dk-claude-tool-bundle 의 tool-workflow-planner 절차 (계획서 → 확답 → 준비 → 단계 제작 → 조립 → 검증). 묶음 다섯으로 나눠 묶음마다 만들고 검수받는다. 단계마다의 상세(프롬프트·지시문 전문, 입력·출력 예시)는 묶음마다 사용자와 대화로 정하고 이 문서에 더한다.

## 요청

- "바로 구현하지 말고 우리 html 상에 시나리오 D 도식화 해놓은 것, 거기 있는 레퍼런스된 파일. 그리고 dk-claude-tool-bundle 이용해서 한번 구현을 해보고 싶어요. 바로 하진 말고 계획부터" (사용자, 2026-11-19)
- "반복 실행의 경우 engine 기능보다는 우리가 루프를 만들어서 거기서 돌게 하는게 좋을듯. 아마 내 기억으로는 prompt split 부분이 비슷하게 하고 있음" (사용자, 2026-11-19)
- "프롬프트 실행 자체를 옵션을 두어서 HITL 가 필요하면 메인세션으로, 그게 아니라면 서브에이전트로 실행하면 되는거 아니야?" (사용자, 2026-11-19)
- "기존 claude -p 가 node 작업을 수행하기는 이제 적합하지 않으니까. 그래서 더 자유도를 준 것" (사용자, 2026-11-19)
- 근거 (corbina/notes, re_code.html): 도식화 - D 탭, 흐름 입출력 D 절, 실행 데이터 (확정), 유즈케이스 D 섹션 함수 초안
- 레퍼런스 (persona-enhancer-pg2/plugin): skills/plan-run/SKILL.md, skills/plan-go/procedure.md:51, client/plan/prepare.py, node_prompts.py, run.py, schedule.py, node_prompt.md, writing.md

## 정한 것

D 탭과 실행 데이터에서 (사용자, 2026-11-18 ~ 19):
- 확정과 실행을 나눈다. id 없이 부르면 계획 목록을 보이고 끝낸다
- 승인이면 실행 중으로, 실행 중이면 이어 가고, 그 밖이면 알리고 끝. 모든 노드가 완료 또는 건너뜀이면 끝남
- 작업 지시: node_prompt.md, writing.md. 첫 줄 "## 전체 작업과 이 노드의 목표" 검사. 끝에 산출물 스펙 원문 절과 글쓰기 규칙을 코드가 붙임. 사람이 고친 작업 지시는 덮지 않음. 저장 위치 `<작업 폴더>/.plan/<계획 id>/nodes/<노드 id>/prompt.md`
- 다음 노드: 앞 노드가 모두 끝난(완료·건너뜀) 노드, 최대 3개, 실패한 노드 뒤로는 고르지 않음
- 노드 실행이 읽는 파일은 작업 지시 하나. 선행 노드 결과는 노드를 시작할 때 포트로 조회해 넘김 (바로 앞 노드만, 마지막 회차). `run.json` 의 `read_inputs` 에 남김
- 노드 상태는 노드 고치기 API 로 status 만 (todo, running, done, failed, skipped). 회차·확인한 말은 run.json
- 실패 처리: 다시 실행 / 고쳐서 다시 / 건너뛰기(그 노드에만 기대는 뒤 노드도) / 멈추기. 멈추면 계획은 실행 중으로 남음
- 계획 노드는 engine 노드로 올리지 않는다

이번 대화에서 (사용자, 2026-11-19):
- 반복은 engine 이 아니라 우리 코드의 루프로 돈다 (split_plan 과 같은 방식)
- 노드 실행 방법을 노드마다 나눈다. 사용자 판단이 필요하면(확인 노드, 실패 처리) 메인 세션, 그 밖은 우리 코드가 claude -p 를 도구를 켠 채로 띄운다 (run_agent). engine 의 SUBAGENT 단계는 쓰지 않는다
- run_agent 를 따로 둔다. 기존 call_prompt 는 입력 글만 보고 답하는 호출용이라 노드 작업에 맞지 않는다
- 노드 하나의 제한 시간 30분
- 아래 "루프 설계"와 "시뮬레이션" 대로 ("ㅇㅇ 이대로 계획서에 옮기고")
- 보류: 지난 실행에서 실패로 남은 노드(예: 멈추기를 고른 노드)를 다시 실패 처리로 묻는 자리

## 흐름도                                  상태: 확답 (사용자, 2026-11-19)

```
plan_run
├─ find_plan            [CODE]               명령 줄 /plan-run 7 → 계획 조회. 승인·실행 중이 아니면 멈춤
├─ start_run            [CODE]               승인 → 실행 중
├─ resume               [IN_ORDER] [run_if: plan_run.was_running]
│  ├─ check_broken      [CODE]               실행 중으로 남은 노드: result.md 가 있으면 완료, 없으면 목록
│  ├─ ask_rerun         [MAIN_SESSION_ASK] [run_if: plan_run.has_broken]   끊긴 노드를 한 질문에 모아: 모두 다시 실행 / 멈추기
│  └─ apply_rerun       [CODE] [run_if: plan_run.has_broken]
├─ prompts              [IN_ORDER] [run_if: plan_run.not_stopped]
│  ├─ count_prompts     [CODE]
│  ├─ show_estimate     [MAIN_SESSION_SHOW]  "노드 N개의 작업 지시를 만듭니다. 약 M분, $X"
│  ├─ write_prompts     [CODE]               call_prompt (도구 없음) 3개씩 동시
│  └─ retry_each        [FOR_EACH_ITEM: write_prompts.failed]
│     ├─ ask_retry      [MAIN_SESSION_ASK]
│     └─ retry_prompt   [CODE]
├─ rounds               [FOR_EACH_ITEM: round_items.rounds]       차례 1, 2, … (노드 수 × 2)
│  ├─ run_nodes         [CODE] [run_if: plan_run.has_work]        우리 루프. run_agent 로 노드 실행
│  ├─ confirm           [IN_ORDER] [run_if: plan_run.stopped_at("confirm")]
│  │  ├─ ask_confirm    [MAIN_SESSION_ASK]   허가 / 허가하지 않음
│  │  └─ finish_confirm [CODE]
│  └─ failed            [IN_ORDER] [run_if: plan_run.stopped_at("failed")]
│     ├─ ask_failed     [MAIN_SESSION_ASK]   다시 실행 / 고쳐서 다시 / 건너뛰기 / 멈추기
│     └─ apply_failed   [CODE]
├─ finish_plan          [CODE]               모두 완료·건너뜀이면 실행 중 → 끝남
└─ notify               [MAIN_SESSION_SHOW]  끝남 / 멈춤 / 차례를 다 씀(이어서 /plan-run 7)
```

- 조건(`was_running`, `not_stopped`, `has_work`, `stopped_at`)은 프로젝트의 조건 함수로 둔다 (C 의 `keeps_candidate` 와 같은 방식)
- 실행할 수 없는 계획은 find_plan 이 오류로 멈춘다 (B 의 find_plan 과 같은 방식)

## 루프 설계

### 두 겹

```
바깥 (engine): rounds 의 차례마다
    run_nodes   ← 안쪽 루프. 사용자에게 물을 것이 생길 때까지 돈다
    confirm 또는 failed   ← 메인 세션이 하나를 묻고 답을 기록
    → 다음 차례

안쪽 (우리 코드, run_nodes 하나 안):
    반복:
        실행할 수 있는 노드를 고른다 (최대 3개)
        없으면 멈춘다
        run_agent 로 동시에 실행하고, 끝나면 기록한다
```

상태의 원본은 계획 저장소의 노드 상태와 `.plan/<id>/nodes/<노드 id>/run.json`. 차례 번호에는 뜻이 없고, 매 차례 run_nodes 가 상태를 다시 읽고 정한다.

### 안쪽 루프 (초안): `rounds/run_nodes/run_nodes_task.py`

```python
def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
    # 실행할 수 있는 노드가 없어질 때까지 run_agent 로 실행하고, 메인 세션이 물을 것을 하나 돌려준다
    plan_id = context.read("find_plan")["plan_id"]
    ran: list[int] = []
    while True:
        plan = plan_api_reader().get_plan(plan_id)
        runs = _read_runs(plan)                                   # 노드마다 run.json
        work_nodes = runnable_nodes(plan, limit=3)                # 앞 노드가 모두 완료·건너뜀, todo, 확인 노드 아님
        if not work_nodes:
            break
        for outcome in _run_parallel(plan, runs, work_nodes):    # 끝나는 대로 받음
            _record(plan_id, outcome)                             # 기록은 이 스레드 하나에서만
            ran.append(outcome.node_id)
    return TaskOutput(_next_question(plan_api_reader().get_plan(plan_id), ran))


def _next_question(plan: Plan, ran: list[int]) -> dict[str, Any]:
    """돌 수 있는 노드가 없을 때 메인 세션이 물을 것. 실패한 노드를 확인 노드보다 먼저."""
    failed = [n for n in plan.nodes if n.status is PlanNodeStatus.FAILED]
    if failed:
        return {"stop_at": "failed", "node_id": failed[0].node_id, "ran": ran}
    confirm = waiting_confirm_nodes(plan)                         # 앞 노드가 모두 끝난 확인 노드
    if confirm:
        return {"stop_at": "confirm", "node_id": confirm[0].node_id, "ran": ran}
    if all(n.status in (PlanNodeStatus.DONE, PlanNodeStatus.SKIPPED) for n in plan.nodes):
        return {"stop_at": "finished", "node_id": None, "ran": ran}
    return {"stop_at": "blocked", "node_id": None, "ran": ran}   # 남은 노드가 있는데 갈 길이 없음
```

규칙:
1. 실패한 노드가 나와도 루프를 바로 멈추지 않는다. 그 뒤로는 고르지 않고 상관없는 노드는 끝까지 돌린다 (기존 plan-run SKILL.md:46-47)
2. 확인 노드는 돌 수 있는 노드를 다 돌린 뒤에 묻는다
3. 메인 세션에는 한 차례에 하나만 넘긴다. 실패가 확인보다 먼저
4. 동시 실행 중에도 노드 기록은 한 곳에서만 쓴다 (mock 저장소가 파일이라 동시에 쓰면 덮일 수 있음)

### 노드 하나 (초안): `rounds/run_nodes/run_one_node.py`

```python
def run_one_node(plan: Plan, node_id: int, run: NodeRun | None) -> NodeOutcome:
    """시작 기록 → run_agent → 판정. 기록 쓰기는 하지 않고 결과만 돌려준다 (부르는 쪽이 _record)."""
    inputs = [read_input(plan, pre_id) for pre_id in plan.prerequisites(node_id)]   # 선행 노드 결과, 마지막 회차
    target = DefaultPlanFolderReader().result_target(plan.plan_id, node_id)       # result.md, files/ 경로
    message = node_run_message(prompt_path(plan.plan_id, node_id), inputs, target) # 노드 실행 지시문 (전문 검수)
    answer = run_agent(message, Path.cwd(), model="opus", timeout_seconds=1800)
    return judge(node_id, answer, target)


def judge(node_id: int, answer: AgentResult, target: ResultTarget) -> NodeOutcome:
    """완료: 답 첫 줄 'status: done' 이고 result.md 가 있음. 그 밖은 실패와 이유."""
    first_line = answer.text.strip().splitlines()[0] if answer.text.strip() else ""
    if answer.timed_out:
        return NodeOutcome.failed(node_id, "시간 초과")
    if first_line != "status: done":
        return NodeOutcome.failed(node_id, answer.text[:300] or "답 없음")
    if not target.result.exists():
        return NodeOutcome.failed(node_id, "결과 파일 없음")
    return NodeOutcome.done(node_id, answer.text)
```

시작 기록(노드 상태 running, run.json 시작, 실패했던 노드면 이전 회차를 `runs/<회차>/` 로)은 실행 직전에 따로 쓴다. 프로세스가 중간에 죽으면 "실행 중"으로 남아 다음 `/plan-run` 의 check_broken 이 처리한다.

### 노드 실행용 claude -p (초안): `claude_utils/agent/run_agent.py`

```python
"""노드 실행용 claude -p. 도구를 켜고 사용자 작업 폴더에서 돈다.
call_prompt 와 달리 출력 모양을 정하지 않는다. 답 글 첫 줄의 status 로 판정한다."""

def run_agent(prompt_text: str, work_dir: Path, model: str, timeout_seconds: int) -> AgentResult:
    argv = [
        os.environ.get("TASK_PLANNER_CLAUDE_BIN", "claude"), "-p", "--model", model,
        "--output-format", "json",
        "--allowedTools", "Read Write Edit Glob Grep Bash",
        "--permission-mode", "bypassPermissions",
        "--settings", '{"disableAllHooks": true}',
        "--no-session-persistence",
    ]
    timed_out, stdout, stderr, exit_code = _run(argv, prompt_text, work_dir, timeout_seconds)
    parsed = _parse_json(stdout)
    return AgentResult(text=parsed.get("result", ""), cost_usd=parsed.get("total_cost_usd"),
                       exit_code=exit_code, timed_out=timed_out)
```

기존 `claude_utils/prompt/call_prompt.py` 와 다른 점: `--tools ""` → 도구 켬, 임시 폴더 → 작업 폴더, `--json-schema` → 자유 글, 권한 묻지 않음, 훅은 `disableAllHooks` 로 끔.

### 메인 세션 답 뒤의 기록

```
finish_confirm   허가 → 노드 done, run.json confirm 에 사용자가 한 말
                 허가하지 않음 → 멈춤 (뒤 차례 모두 건너뜀)
apply_failed     다시 실행 → 노드 todo (회차는 다음 시작 때 옮김)
                 고쳐서 다시 → 멈춤. 알림에 "작업 지시를 고친 뒤 /plan-run 7"
                 건너뛰기 → skipped, 그 노드에만 기대는 뒤 노드도 skipped
                 멈추기 → 멈춤
```

### 차례 수

`round_items.py`: `range(1, 노드 수 × 2 + 1)`. 차례마다 노드 하나 이상이 끝나거나 멈춘다. 차례를 다 쓰면 notify 가 "남은 노드가 있습니다. /plan-run 7 로 이어 주세요".

## 시뮬레이션 (노드 5개)

```
1 테이블 설계 (code) ──┬──▶ 2 API 구현 (code) ──┐
                       └──▶ 3 화면 구현 (code) ──┴──▶ 4 스테이징 확인 (확인 노드) ──▶ 5 배포 문서 (document)
```
노드 3 이 처음에 한 번 실패한다고 가정.

| 차례 | 안에서 일어나는 일 | 사용자 화면 | 끝난 뒤 노드 상태 |
|---|---|---|---|
| 시작 | find_plan(승인) → start_run(실행 중) → resume 건너뜀 → 작업 지시 5개 | "노드 5개의 작업 지시를 만듭니다. 약 2분, $1.5 안팎" | 모두 todo |
| 1 | run_nodes: [1] 실행 → done. [2, 3] 동시 → 2 done, 3 blocked → failed. 고를 노드 없음 → stop_at failed | [선택 창] 노드 3 "화면 구현"이 막혔습니다: 차트 라이브러리를 설치할 권한이 없음. 어떻게 할까요? → 다시 실행 | 1 done, 2 done, 3 todo, 4·5 todo |
| 2 | run_nodes: [3] (이전 결과 runs/1/ 로, 회차 2) → done. 4 는 확인 노드 → stop_at confirm | [선택 창] 노드 4 "스테이징 확인": 노드 2 의 API 시험 결과와 노드 3 의 화면 캡처 위치입니다. 다음으로 넘어가도 될까요? → 허가 | 1~4 done, 5 todo |
| 3 | run_nodes: [5] → done → stop_at finished | — | 모두 done |
| 4~10 | has_work 거짓, 건너뜀 | — | |
| 끝 | finish_plan(끝남) → notify | 계획 7 을 마쳤습니다. 노드별 상태 표 (노드 3 은 회차 2) | |

다른 답을 고른 경우:
- 차례 1 에서 건너뛰기: 3 skipped. 4 는 앞 노드 2(done), 3(skipped)이 모두 끝나 차례 2 에 확인 노드로 나온다 (3 에만 기대는 노드가 아니므로 함께 건너뛰지 않음)
- 차례 1 에서 멈추기: 차례 2~10 건너뜀. 계획은 실행 중. 알림 "노드 3 에서 멈췄습니다. 이어 하려면 /plan-run 7". 다음 실행에서 3 은 failed 그대로 (보류한 부분)
- 차례 1 도중 Claude Code 를 닫음: 2, 3 이 running 으로 남음. 다음 `/plan-run 7` 의 check_broken 이 2 는 result.md 가 있어 done, 3 은 파일이 없어 "아래 노드는 … 다시 실행할까요?"

## 단계별 상세                             상태: 0 / 20 확답

묶음마다 tool-workflow-planner 형식(종류, 결과 종류, 입력, 출력, 상세, 다시 수행)으로 채우고 확답받는다.

### 묶음 1: 준비 평가 (tool-planner 형식)

나누기
- 포트: 계획 조회·계획 상태·노드 상태 (plan_api, 있음), 계획 폴더의 result.md 유무·run.json (plan_folder, 있음)
- 공통 기능: 없음
- 워크플로로 넘길 것: 단계 전부

tool-assess-port: **충족**. `PlanApiReader.get_plan`, `PlanApiWriter.set_plan_status`, `PlanApiWriter.update_node(NodeChange(status=…))`, `PlanFolderReader.list_plan_ids / read_output / read_run`, `PlanFolderWriter.save_run`

tool-assess-model: **부분 충족**
- [기존 확장] model/node_run/node_run.py — NodeRun
  - 바꾸기 전: 동작 `start(now, read_inputs)`, `finish(status, now)`
  - 바꾼 뒤: 동작 `back_to_todo() -> NodeRun` 을 더함 (상태 todo, 시작·끝 시각 비움, 회차 그대로). 끊긴 노드를 다시 실행할 때 쓴다
  - 영향: 없음 (필드 그대로, 파일 모양 그대로)
  - 사용자 확인: 대기

다른 워크플로의 코드 (번들 규칙: 다른 워크플로 폴더를 import 하지 않음):
- 명령 줄에서 계획 id 읽기, 지금 대화의 기록 파일: confirm_plan 에 있다. plan_run 에 따로 둔다 (정규식이 `plan-run` 으로 다름, 기존 코드는 바꾸지 않음)
- 계획 상태를 한국어로(`status_label`): list_plans 에 있고 confirm_plan 이 이미 import 한다. 정할 것

### find_plan
- 종류: CODE
- 결과 종류: DATA
- 입력: 없음 (지금 대화의 기록 파일에서 사용자가 친 `/…plan-run <id>` 줄)
- 출력: → { plan_id: int, title: str, status: str }
- 상세: 명령 줄의 id 로 계획 저장소에서 계획을 읽는다. 이 작업 폴더에 계획 폴더(`.plan/<id>/`)가 있는지 본다. 승인·실행 중이 아니면 PlanNotRunnableError 로 멈춘다 (글은 아래). 쓸 model·port: Plan, PlanStatus, PlanApiReader, PlanFolderReader.list_plan_ids, engine 의 DefaultSessionReader
- 다시 수행: 해당 없음 (읽기만)
- 상태: 확답 전

멈출 때의 글:
```
명령에서 계획 id 를 찾지 못했습니다. /task-planner:plan-run <계획 id> 로 다시 불러 주세요
대화 기록 경로가 없어 명령의 계획 id 를 읽지 못했습니다
계획 {id} 이 계획 저장소에 없습니다
계획 {id} 의 계획 폴더가 이 작업 폴더에 없습니다. 계획을 만든 폴더에서 불러 주세요
계획 {id} 은 작성 중 상태라 실행할 수 없습니다. 계획을 다 만든 뒤 /task-planner:plan-go {id} 로 확정해 주세요
계획 {id} 은 검토 중 상태라 실행할 수 없습니다. 확정은 /task-planner:plan-go {id}
계획 {id} 은 불허 상태라 실행할 수 없습니다
계획 {id} 은 끝남 상태입니다. 모든 노드를 이미 실행했습니다
```

### start_run
- 종류: CODE
- 결과 종류: DATA
- 입력: ← find_plan.plan_id, ← find_plan.status
- 출력: → { was_running: bool }
- 상세: 승인이면 계획 상태를 실행 중으로 바꾼다. 이미 실행 중이면 바꾸지 않고 was_running 을 참으로. 쓸 port: PlanApiWriter.set_plan_status
- 다시 수행: 안전 (실행 중을 실행 중으로 다시 써도 같음)
- 상태: 확답 전

### resume/check_broken
- 종류: CODE
- 결과 종류: DATA
- 입력: ← find_plan.plan_id
- 출력: → { nodes: list[dict] (node_id: int, title: str), recorded_done: list[int] }
- 상세: 노드 상태가 running 인 노드마다 result.md 가 있으면 완료로 기록하고(노드 상태 done, run.json 끝), 없으면 nodes 에 넣는다. 쓸 model·port: NodeRun.finish, PlanApiWriter.update_node, PlanFolderReader.read_output·read_run, PlanFolderWriter.save_run
- 다시 수행: 안전 (두 번째에는 running 인 노드가 없음)
- 상태: 확답 전

끊긴 노드를 노드마다 묻던 첫 판(broken_each 반복)은 리뷰에서 "멈추기를 골라도 다음 노드를 또 묻고 상태를 바꿈"이 나와, 한 질문에 모아 묻는 것으로 바꿨다 (사용자 "가로 고치고", 2026-11-19). engine 의 항목마다 반복은 앞 항목의 답과 상관없이 모든 항목을 끝까지 돈다.

### resume/ask_rerun
- 종류: MAIN_SESSION_ASK
- 결과 종류: DATA
- 입력: ← check_broken.nodes
- 출력: → { answer: str }
- 상세: 질문 "아래 노드는 실행 중에 끊겼고 결과 파일이 없습니다.\n- 노드 {node_id} \"{title}\"\n…\n다시 실행할까요?", 선택지 "모두 다시 실행" / "멈추기", 선택지 밖의 답은 받지 않음. 조건 has_broken
- 다시 수행: 해당 없음
- 상태: 확답

### resume/apply_rerun
- 종류: CODE
- 결과 종류: DATA
- 입력: ← find_plan.plan_id, ← check_broken.nodes, ← ask_rerun.answer
- 출력: → { stopped: bool }
- 상세: "모두 다시 실행"이면 끊긴 노드마다 노드 상태 todo, run.json 을 NodeRun.back_to_todo() 로. "멈추기"면 쓰지 않고 stopped 참. 조건 has_broken
- 다시 수행: 안전
- 상태: 확답

### 조건
- `plan_run.was_running`: start_run.was_running
- `plan_run.has_broken`: check_broken.nodes 가 비어 있지 않음
- `plan_run.not_stopped`: apply_rerun 결과가 없거나(이어 가기가 아님, 끊긴 노드 없음) stopped 가 거짓이면 참. 묶음 2 이후 다른 멈춤을 더한다

### 묶음 1 시험용 임시 끝 단계: wip_notice
- 종류: MAIN_SESSION_SHOW. 묶음 5 의 notify 로 바꾼다
- 글: "계획 {plan_id} \"{title}\" 을 실행 중으로 두었습니다. (작업 지시 만들기부터는 아직 만들지 않았습니다)" / 멈췄으면 "노드 {id}, {id} 에서 멈췄습니다. 이어 하려면 /task-planner:plan-run {plan_id}"

### 묶음 2: 작업 지시 만들기 (prompts)

사용자 결정 (2026-11-19): "run_agent 를 지금 만들어서 여기 사용 하도록", 앞 노드 절은 "읽어서 한번에 유저 컨텍스트로 넣는 방식으로 수정", 끊긴 노드처럼 실패한 노드는 한 질문에 모아 묻기, prompt.md 가 이미 있으면 만들지 않기 (브리핑의 제안대로 "이대로 진행").

준비 평가 (tool-planner 형식)
- 나누기: 공통 기능 run_agent (claude_utils, 묶음 2 와 4 가 씀). 포트는 있는 것 (read_command, read_prompt, write_prompt, persona_api list_personas)
- tool-assess-port: 충족
- tool-assess-model: 충족 (NodeSpec, PlanNode, Persona 그대로)
- 공통 기능: [신규] claude_utils/agent/run_agent.py, dto/agent_result.py, agent_call_error.py. 기존 call_prompt 는 그대로

흐름도
```
├─ prompts              [IN_ORDER] [run_if: plan_run.not_stopped]
│  ├─ count_prompts     [CODE]                                         작업 지시가 없는 노드, 대략의 시간·비용
│  ├─ show_estimate     [MAIN_SESSION_SHOW] [run_if: plan_run.has_missing_prompts]
│  ├─ write_prompts     [CODE] [run_if: plan_run.has_missing_prompts]  run_agent(읽기 도구) 3개씩 동시
│  ├─ ask_retry         [MAIN_SESSION_ASK] [run_if: plan_run.has_failed_prompts]   한 질문에 모아: 모두 다시 만들기 / 멈추기
│  └─ retry_prompts     [CODE] [run_if: plan_run.has_failed_prompts]   한 번 더. 그래도 실패한 노드는 멈춤
```

단계 요지 (상세는 계획서 확답 뒤 같은 형식으로)
- count_prompts: 출력 { missing: list[{node_id, title}], minutes: int, cost_low: float, cost_high: float }. 계산: 노드 하나 1분 안팎, 3개씩 동시, $0.3~0.6 (기존 plan-go/procedure.md:51)
- show_estimate: "노드 {N}개의 작업 지시를 만듭니다. 약 {M}분, ${lo}~${hi} 안팎"
- write_prompts: 출력 { made: list[{node_id, cost_usd, seconds}], failed: list[{node_id, title, reason}] }. 실패: claude 오류, 시간 초과(15분), 첫 줄이 "## 전체 작업과 이 노드의 목표" 가 아님. 실패한 노드는 prompt.md 를 쓰지 않는다
- ask_retry: "아래 노드는 작업 지시를 만들지 못했습니다.\n- 노드 {id} \"{title}\": {이유}\n다시 만들까요?" 모두 다시 만들기 / 멈추기
- retry_prompts: 출력 { made, failed }. 그래도 failed 가 있으면 멈춤 (알림에 그 노드)
- 다시 수행: write_prompts·retry_prompts 는 안전 (prompt.md 가 생긴 노드는 다음에 건너뜀)

### 묶음 3: 다음 노드 계산 (model)

사용자 결정 (2026-11-20): 동시 실행은 빈 자리 채우기 ("B는 나안"), 계산 함수는 model 에 새 파일로 두고 Plan 클래스는 바꾸지 않음 ("C는 추천대로").

준비 평가 (tool-planner 형식)
- 나누기: model 만. 포트·공통 기능·워크플로 없음 (쓰는 곳은 묶음 4 의 run_nodes, apply_failed, 묶음 5 의 finish_plan, notify)
- tool-assess-port: 해당 없음
- tool-assess-model: 미충족
  - [신규] model/plan/plan_schedule.py — 함수 `runnable_nodes`, `waiting_confirm_nodes`, `nodes_to_skip`, `plan_progress`
  - [신규] model/plan/plan_progress.py — PlanProgress (counts: dict[PlanNodeStatus, int], finished: bool, blocked: bool)
  - 기존 Plan, PlanNode 는 바꾸지 않는다. 노드 상태는 PlanNode.status (계획 저장소) 만 본다. run.json 은 읽지 않는다
  - 사용자 확인: 받음 (C)

규칙 (기존 schedule.py:21-75, run.py:263-281 에서 루프를 뺀 것)
- 끝난 노드 = 완료(done) 또는 건너뜀(skipped)
- runnable_nodes(plan, limit): 상태 todo, 확인 노드가 아님, 선행 노드가 모두 끝남. node_id 작은 순으로 limit 개. 실패한 노드의 뒤 노드는 선행 노드가 안 끝났으므로 저절로 빠진다. limit 은 부르는 쪽이 "3 - 지금 도는 수" 로 준다 (빈 자리 채우기)
- waiting_confirm_nodes(plan): 확인 노드(hitl), 상태 todo, 선행 노드가 모두 끝남. node_id 작은 순
- nodes_to_skip(plan, node_id): 그 노드와, 들어오는 간선이 모두 건너뛴(또는 이번에 건너뛸) 노드에서 오는 뒤 노드. 완료·실행 중인 노드는 넣지 않는다
- plan_progress(plan): 상태별 개수. finished = 모든 노드가 끝남. blocked = 안 끝났는데 실행할 노드, 확인 노드, 실행 중인 노드, 실패한 노드가 모두 없음

동시 실행 (묶음 4 에서 씀): 빈 자리 채우기. 하나가 끝날 때마다 노드 상태를 다시 읽고 runnable_nodes(plan, 3 - 도는 수) 로 빈 자리에 새 노드를 띄운다. 도는 노드가 없고 고를 노드도 없으면 안쪽 루프를 끝낸다

앞 노드 결과를 노드 실행에 넘기는 방식 (정할 것 A, 2026-11-20 사용자 질문 "result 하위의 자료들을 전부 텍스트로 읽어오는게 필요할까?"): 정할 것 4 로 묶음 4 에서

### 묶음 4: 노드 실행 루프 (정한 것, 계획서는 확인 시험 뒤)

사용자 결정 (2026-11-20):
- 노드 실행 입력: 작업 지시(prompt.md)는 본문을 넣고, 앞 노드 결과는 위치만 넘긴다 (실행 데이터 (확정) 3 절의 조회 결과: 노드 id, 제목, 상태, 회차, result.md 경로, files 목록, 건너뛴 이유). 노드가 Read 로 필요한 만큼 읽는다 ("아 오케이 이렇게 합시다")
- 코드 노드(kind code)는 순차로 실행한다. 같은 저장소를 동시에 고치면 서로 덮을 수 있어서다 ("순차적으로 수행하게 해야 할듯")
- 노드 실행 도구: Read Write Edit Glob Grep Bash WebSearch WebFetch 를 켜고 묻지 않고 쓴다 ("보여준 것 그대로 허용")
- 노드 실행은 Claude Code 기본 시스템 프롬프트에 지시문을 덧붙인다 (--append-system-prompt). run_agent 에 덮어쓸지 덧붙일지 고르는 인자를 더한다 ("동의")
- 진행 화면 표시는 묶음 5 로 ("다음 묶음에 둡시다")
- 확인 노드: 메인 세션이 확인 노드의 prompt.md 대로 앞 노드 결과에서 확인할 부분을 골라 보이고 질문에 답한 뒤(MAIN_SESSION_TALK), 허가 / 허가하지 않음을 묻는다(MAIN_SESSION_ASK) ("오키 나로 고고"). 예전 plan-run SKILL.md:35 와 같은 방식
- 10분 한도: 메인 세션의 Bash 는 앞에서 기다릴 때 최대 10분이다. 백그라운드로 부르면 한도가 없다. engine 의 "기다림" 지시와 멈춤 훅(engine/hook/stop_hook.py:25)이 이 경우를 받친다. 실제 Claude Code 에서 맞물리는지 작은 시험 흐름으로 먼저 확인한다

### 묶음 4: 계획서 (2026-11-20)

더 정한 것 (사용자, 2026-11-20):
- 명령 시간: 백그라운드 명령에도 기본 10분 제한이 있다 (시험 slow720: 10분에 [killed], engine 이 단계를 처음부터 다시 돌림). 제한 시간을 직접 주면 넘길 수 있다 (2시간으로 준 명령이 12분 동안 끊기지 않음)
- run_nodes 한 번은 시작하고 30분이 지나면 새 노드를 띄우지 않고, 돌던 노드가 끝나면 "계속"으로 돌아온다 ("마감 30분으로 하고"). 그래서 명령 한 번은 길어야 30분 + 노드 하나 30분 + 여유. plan-run 스킬은 next·done 을 백그라운드, 제한 70분(4200000)으로 부른다 (묶음 5 스킬 전문에서 검수)

준비 평가 (tool-planner 형식)
- 나누기: 공통 기능 run_agent 바꿈, 포트 plan_folder 에 멈춤 표시 더함, model 없음
- tool-assess-port: 부분 충족
  - [기존 확장] PlanFolderWriter.save_stop(plan_id, StopMark), PlanFolderReader.read_stop(plan_id) -> StopMark | None. 파일 `.plan/<id>/stop.json`
  - 이유: 바깥 차례(rounds) 안의 단계는 앞 차례의 결과를 읽을 수 없다 (선언 검사: reads 의 노드는 먼저 실행되어야 함. engine/runner/scenario/check_definition.py:64). 그래서 "이번 실행에서 사용자가 멈추기를 골랐다"를 다음 차례의 run_nodes 가 알 길이 없어, 실패한 노드를 차례마다 다시 묻게 된다. 멈춤 표시를 engine 실행 id 와 함께 계획 폴더에 남기고, run_nodes 가 처음에 읽는다. 다음 /plan-run 은 실행 id 가 달라 표시를 무시한다
  - 사용자 확인: 대기
- tool-assess-model: 충족 (NodeRun.start·finish, plan_schedule). 새 dto StopMark(run_id, reason, node_ids, message) 는 port/local/plan_folder/dto 에
- 공통 기능: [기존 확장] run_agent 에 system_prompt 를 덮어쓸지 덧붙일지 (append: bool). 자식 프로세스 그룹을 기록해 우리 프로세스가 SIGTERM·SIGINT 를 받거나 끝날 때 함께 끝낸다 (리뷰 지적 2). 사용자 확인: 대기

흐름도
```
├─ rounds               [FOR_EACH_ITEM: plan_run.rounds] [run_if: plan_run.not_stopped(upto=prompts)]
│  ├─ run_nodes         [CODE]    멈춤 표시가 있으면 바로 stopped. 아니면 우리 루프
│  ├─ continue_notice   [MAIN_SESSION_SHOW] [run_if: plan_run.stopped_at("continue")]   마친 노드와 결과 위치. next 를 여기서 끝냄
│  ├─ confirm           [IN_ORDER] [run_if: plan_run.stopped_at("confirm")]
│  │  ├─ show_confirm   [MAIN_SESSION_TALK]
│  │  ├─ ask_confirm    [MAIN_SESSION_ASK]   허가 / 허가하지 않음
│  │  └─ finish_confirm [CODE]
│  └─ failed            [IN_ORDER] [run_if: plan_run.stopped_at("failed")]
│     ├─ ask_failed     [MAIN_SESSION_ASK]   다시 실행 / 작업 지시를 고쳐 다시 / 건너뛰기 / 멈추기
│     └─ apply_failed   [CODE]
```
- 차례 수: 노드 수 × 2 + 2. 차례마다 노드 하나 이상이 끝나거나, 사용자 답 하나가 기록되거나, 30분 마감으로 "계속"이다. 끝남·막힘·멈춤 뒤의 차례는 run_nodes 가 바로 돌아오고 confirm·failed 는 건너뛴다
- stopped_at 조건은 같은 차례의 run_nodes 결과만 읽는다 (앞 형제라 읽을 수 있음)

run_nodes 출력: { stop_at: "failed" | "confirm" | "finished" | "blocked" | "continue" | "stopped", node_id: int | None, ran: list[{node_id, status, summary, reason, cost_usd, seconds}] }

노드 실행 지시문 (rounds/run_nodes/node_run_message.md, --append-system-prompt 로 덧붙임, 전문 검수 대상):
```
너는 계획 노드 하나를 실행한다. 입력의 "작업 지시"를 그대로 수행한다.
앞 노드의 결과는 "앞 노드의 결과"에 위치가 있다. 작업 지시의 "앞 노드에서 받는 것"에 맞춰 필요한 파일을 읽는다.
결과 본문 전체는 "결과를 쓸 곳"의 본문 파일에 쓴다. 결과가 여러 파일이면 그 아래 files/ 에 두고 본문에서 가리킨다.
앞 노드의 결과가 작업 지시의 예상과 다르면 받은 결과를 따르고, 다른 점을 본문에 적는다.
실행으로 확인하지 못한 완료 기준은 "확인 못 함"으로 적는다. 그런 기준이 있으면 막힘으로 끝낸다.
마지막 답은 첫 줄에 "status: done" 또는 "status: blocked", 그다음 세 줄 이내 요약만 쓴다. 결과 본문을 답에 붙이지 않는다.
```

노드 실행 입력 (user):
```
# 작업 지시
{prompt.md 전문}

# 앞 노드의 결과
- 노드 {id} "{title}": 완료, {round} 회차
  - 결과: {result.md 절대 경로}
  - 결과 파일: {files/ 아래 파일 절대 경로, 없으면 이 줄 없음}
- 노드 {id} "{title}": 건너뜀. 이유: {skipped_reason}
(없으면 "(없음. 계획의 첫 노드)")

# 결과를 쓸 곳
- 본문: {result.md 절대 경로}
- 여러 파일이면: {files/ 절대 경로}
```

확인 노드 글 (사용자 화면, 검수 대상)
- show_confirm (MAIN_SESSION_TALK)
  - 목표: "확인 노드 {id} \"{title}\" 의 작업 지시 {prompt.md 경로} 를 읽고, 거기 적힌 대로 앞 노드 결과({result.md 경로들})에서 사용자가 확인할 부분만 골라 보인다. 사용자의 질문에 답한다. 질문이 없으면 바로 끝낸다. 넘어가도 되는지는 묻지 않는다 (다음 단계가 묻는다)."
  - 첫 말: "노드 {id} \"{title}\" 을 확인할 차례입니다. 확인하실 부분을 모아 보여 드리겠습니다."
- ask_confirm: "노드 {id} \"{title}\": 다음으로 넘어가도 될까요?" 허가 / 허가하지 않음
- finish_confirm: 허가면 확인 노드 result.md(아래), run.json confirm(대화에서 사용자가 한 말), 노드 상태 done. 허가하지 않음이면 멈춤 표시 (reason confirm_denied)
  ```
  # 확인: {title}

  사용자가 확인하고 다음으로 넘어가도 된다고 허가했다.

  ## 사용자가 한 말
  {확인 대화 구간의 사용자 말, 없으면 "(말하지 않음)"}

  ## 확인한 앞 노드 결과
  - 노드 {id} "{title}": {result.md 경로}
  ```

실패 처리 글 (검수 대상)
- ask_failed: "노드 {id} \"{title}\" 이 끝나지 못했습니다.\n이유: {reason}\n요약: {summary, 없으면 줄 없음}\n결과: {result.md 경로, 없으면 \"없음\"}\n어떻게 할까요?" 다시 실행 / 작업 지시를 고쳐 다시 / 건너뛰기 / 멈추기
- apply_failed
  - 다시 실행: archive_round (runs/<회차>/ 로 보관, 회차 +1, run.json todo), 노드 상태 todo
  - 작업 지시를 고쳐 다시: 위와 같고 멈춤 표시 (message "작업 지시 {prompt.md 경로} 를 고친 뒤 /task-planner:plan-run {plan_id}")
  - 건너뛰기: nodes_to_skip 의 노드마다 run.json finish(skipped) 와 skipped_reason "사용자가 건너뜀", 노드 상태 skipped
  - 멈추기: 멈춤 표시 (reason failed_stop)

우리 루프 (rounds/run_nodes/run_nodes_task.py 와 같은 폴더의 함수, 초안)
```python
PARALLEL = 3
LAUNCH_CUTOFF_SECONDS = 1800      # 이 뒤로는 새 노드를 띄우지 않는다 (사용자, 2026-11-20)
NODE_TIMEOUT_SECONDS = 1800       # 노드 하나 (사용자, 2026-11-19)

def run_until_question(plan_id: int, run_id: str) -> dict[str, Any]:
    if _stopped_in_this_run(plan_id, run_id):
        return {"stop_at": "stopped", "node_id": None, "ran": []}
    deadline = time.monotonic() + LAUNCH_CUTOFF_SECONDS
    running: dict[Future[NodeOutcome], PlanNode] = {}
    ran: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
        while True:
            plan = plan_api_reader().get_plan(plan_id)
            if time.monotonic() < deadline:
                for node in _pick(plan, running.values()):          # 빈 자리, 코드 노드는 하나만
                    start_node(plan, node.node_id)                    # run.json 시작, 노드 상태 running
                    running[pool.submit(execute_node, plan, node)] = node
            if not running:
                break
            done = next(as_completed(running))
            node = running.pop(done)
            ran.append(finish_node(plan_id, node, done.result()))    # 끝나는 대로 바로 기록
    return _next_question(plan_api_reader().get_plan(plan_id), ran, past_deadline=time.monotonic() >= deadline)


def _pick(plan: Plan, running: Iterable[PlanNode]) -> list[PlanNode]:
    """빈 자리만큼, 코드 노드는 도는 것이 없을 때 하나만 (사용자, 2026-11-20 "순차적으로")."""
    running = list(running)
    code_busy = any(node.kind is NodeKind.CODE for node in running)
    picked: list[PlanNode] = []
    for node in runnable_nodes(plan, len(plan.nodes)):
        if len(running) + len(picked) >= PARALLEL:
            break
        if node.node_id in {r.node_id for r in running}:
            continue
        if node.kind is NodeKind.CODE:
            if code_busy:
                continue
            code_busy = True
        picked.append(node)
    return picked


def _next_question(plan, ran, past_deadline) -> dict[str, Any]:
    """실패 > 확인 > 마감 지나 남은 일(계속) > 끝남 > 막힘."""
```
- execute_node (작업 스레드): 입력 글을 만들고 run_agent(지시문, 입력, 모든 도구, 작업 폴더, opus, 30분, append=True) → judge (답 첫 줄 "status: done" 이고 result.md 있음이면 done, 아니면 failed 와 이유). 기록은 하지 않는다
- start_node, finish_node 는 부르는 스레드에서만 계획 저장소와 run.json 을 쓴다
- 노드 실행 도구: Read, Write, Edit, Glob, Grep, Bash, WebSearch, WebFetch (사용자, 2026-11-20 "보여준 것 그대로 허용")

시험 계획
- 가짜 claude 로 시뮬레이션 그대로 (노드 5개: 1 → 2·3 → 4(확인) → 5, 3 이 한 번 실패 → 다시 실행 → 확인 허가 → 끝)
- 코드 노드 둘이 동시에 뜨지 않음, 문서 노드는 3개까지
- 건너뛰기 번짐, 고쳐서 다시와 멈추기 뒤 다음 차례가 다시 묻지 않음, 다음 /plan-run 에서 다시 물음
- 마감: 마감을 시험에서 짧게 주고 "계속" 뒤 다음 차례가 이어 감
- run_agent: 덧붙이기 인자, 신호로 끝날 때 자식 그룹을 끝냄

### 노드 수행 이력이 남는 곳 (사용자 요청 "각 노드의 수행 이력이 어디에 표시되는지는 기록해주세요", 2026-11-20)

| 무엇 | 어디 | 누가 쓰나 | 있음 / 묶음 4 에서 |
|---|---|---|---|
| 노드 상태 (원본) | 계획 저장소 PlanNode.status (지금 `.mockData/`, 나중 서버 PATCH /plans/{id}/nodes/{node_id}) | 우리 코드 | 있음 |
| 회차, 상태 사본, 시작·끝 시각, 읽은 선행 노드와 그 회차, 확인한 말, 건너뛴 이유 | `<작업 폴더>/.plan/<계획 id>/nodes/<노드 id>/run.json` | 우리 코드 | 있음 (start·finish·back_to_todo), 시작·끝 기록은 묶음 4 |
| 이 회차의 작업 지시 | `…/nodes/<노드 id>/prompt.md` | 묶음 2 생성기 (사람이 고쳐도 됨) | 있음 |
| 이 회차의 결과 | `…/nodes/<노드 id>/result.md`, `files/` | 노드 실행 claude -p. 확인 노드는 우리 코드 | 묶음 4 |
| 지난 회차 | `…/nodes/<노드 id>/runs/<회차>/` (prompt.md 복사, result.md·files/ 옮김) | 우리 코드 (archive_round) | 있음, 부르는 곳은 묶음 4 |
| claude -p 답의 요약, 비용, 걸린 시간, 실패 이유 | engine 실행 기록 `.task_planner/sessions/<세션>/runs/<실행>/run_nodes_*/result.json` (그 차례에 돌린 노드마다) | engine (run_nodes 의 결과) | 묶음 4 |
| 실행 중 진행 줄 | 미정 (묶음 5) | | |

### 묶음 5-1: finish_plan (계획서, 2026-11-20)

요청: "1,2 / 3&4 를 3번에 나눠서 할건데, 1번 같은 경우 먼저 dk-claude-tool-bundle 로 검사 & 계획 해줄 수 있나?" (사용자, 2026-11-20). 1 은 계획 끝내기, 2 는 끝 알림, 3·4 는 plan-run 스킬과 e2e.

나누기 (tool-planner 형식)
- 포트: 계획 조회, 계획 상태 바꾸기
- 공통 기능: 없음
- 워크플로로 넘길 것: finish_plan 단계 (tool-add-code-task)

tool-assess-port
- 판정: 충족
| 필요한 접근 | 판정 | 포트 | 메서드 |
|---|---|---|---|
| 계획과 노드 상태 읽기 | 충족 | plan_api | PlanApiReader.get_plan(plan_id) -> Plan |
| 계획 상태를 끝남으로 | 충족 | plan_api | PlanApiWriter.set_plan_status(plan_id, PlanStatus.DONE) -> Plan |
- model 층 요청: 모든 노드가 끝났는지 판정

tool-assess-model
- 판정: 충족
| 요청 | 판정 | model |
|---|---|---|
| 모든 노드가 완료·건너뜀인지 | 충족 | plan_schedule.plan_progress(plan).finished (묶음 3) |
| 실행 중 → 끝남을 허용하는지 | 충족 | PlanStatus.can_move_to: RUNNING → (DONE,) |

흐름도 (바뀌는 곳)
```
├─ rounds   …
├─ finish_plan          [CODE]               새로. 모든 노드가 완료·건너뜀이면 실행 중 → 끝남
└─ wip_notice           [MAIN_SESSION_SHOW]  임시 끝 단계. 묶음 5-2 에서 notify 로 바꾼다
```

### finish_plan
- 종류: CODE
- 결과 종류: DATA
- 입력: ← find_plan.plan_id
- 출력: → { finished: bool }
- 상세: 계획을 읽고, 모든 노드가 완료·건너뜀이면 계획 상태를 실행 중에서 끝남으로 바꾼다. 끝나지 않았으면(멈춤, 막힘, 차례를 다 씀) 바꾸지 않는다. 쓸 model·port: PlanApiReader.get_plan, plan_progress, PlanApiWriter.set_plan_status
- 조건: 없음. 끝나지 않았으면 쓰지 않으므로 조건을 따로 붙이지 않는다
- 다시 수행: 안전 (이미 끝남이면 쓰지 않는다)
- 상태: 확답 (사용자 "아 오키오키", 2026-11-20)

### 묶음 5-2: notify 끝 알림 (계획서, 2026-11-20)

요청: "ㅇㅇ 이 방향으로 계획 세워줘" (사용자, 2026-11-20). 방향: 임시 끝 단계(wip_notice)를 지우고 notify 로 바꾼다. 모두 끝남·막힘이면 노드별 표, 멈춤은 지금 글 그대로.

나누기 (tool-planner 형식)
- 포트: 계획 읽기, 노드마다 run.json 읽기, 결과 파일 위치
- 공통 기능: 없음
- 워크플로로 넘길 것: notify 단계 (tool-add-session-task), 표 만들기 함수 (단계 폴더)

tool-assess-port
- 판정: 충족
| 필요한 접근 | 판정 | 포트 | 메서드 |
|---|---|---|---|
| 계획과 노드 상태 | 충족 | plan_api | PlanApiReader.get_plan(plan_id) -> Plan |
| 노드의 회차, 확인한 말, 건너뛴·실패 이유 | 충족 | local/plan_folder | PlanFolderReader.read_run(plan_id, node_id) -> NodeRun \| None |
| 결과 파일 위치 | 충족 | local/plan_folder | plan_folder_location.result_file(plan_id, node_id) |
| 이번 실행의 멈춘 자리 | 충족 | local/plan_folder | PlanFolderReader.read_stop (stopped_node.stop_point 안에서) |

tool-assess-model
- 판정: 충족
| 요청 | 판정 | model |
|---|---|---|
| 막힘 판정 | 충족 | plan_schedule.plan_progress(plan).blocked |
| 노드 기록 | 충족 | NodeRun (round, confirm, skipped_reason, failed_reason) |
- 상태의 한국어 이름(완료, 건너뜀 …)은 보이는 글이라 model 이 아니라 단계 폴더에 둔다

흐름도 (바뀌는 곳)
```
├─ finish_plan          [CODE]
└─ notify               [MAIN_SESSION_SHOW]  wip_notice 를 바꿈. 멈춤 / 끝남(표) / 막힘(표) / 남음
```

### notify
- 종류: MAIN_SESSION_SHOW
- 결과 종류: DATA
- 입력: ← find_plan.plan_id, ← find_plan.title, ← check_broken, ← apply_rerun, ← retry_prompts (멈춘 자리, stop_point), ← finish_plan.finished
- 출력: 없음
- 보일 글 (위에서부터 처음 맞는 것):
  1. 노드 실행 중 멈춤: 멈춤 표시의 글 그대로. 예: `노드 3 "화면 설계" 에서 멈췄습니다. 이어 하려면 /task-planner:plan-run 7`
  2. 끊긴 노드에서 멈춤: `노드 {id, …} 에서 멈췄습니다. 이어 하려면 /task-planner:plan-run {plan_id}` (지금 글)
  3. 작업 지시를 못 만듦: `노드 {id, …} 의 작업 지시를 만들지 못해 멈췄습니다. 이어 하려면 /task-planner:plan-run {plan_id}` (지금 글)
  4. 끝남 (finish_plan.finished): `계획 {plan_id} "{title}" 을 마쳤습니다. {노드 수 줄}` + 빈 줄 + 표
  5. 막힘: `계획 {plan_id} "{title}" 에서 더 실행할 수 있는 노드가 없습니다. {노드 수 줄}. 이어 하려면 /task-planner:plan-run {plan_id}` + 빈 줄 + 표
  6. 그 밖(차례를 다 씀): `계획 {plan_id} "{title}" 에 남은 노드가 있습니다. 이어 하려면 /task-planner:plan-run {plan_id}`
- 노드 수 줄: `노드 5개: 완료 4, 건너뜀 1` (0 인 상태는 뺌. 순서 완료, 건너뜀, 실패, 실행 중, 할 일)
- 표: `| 노드 | 제목 | 상태 | 회차 | 결과 / 이유 |`, 계획의 노드 순서. 회차는 run.json 이 없으면 `-`
- 결과 / 이유:
  - 완료 + 확인한 말 있음: `확인: "<첫 줄 60자, 넘으면 …>"`
  - 완료: 결과 파일 위치 (작업 폴더 기준, 예 `.plan/13/nodes/53/result.md`)
  - 건너뜀: 건너뛴 이유. 실패 이유가 있으면 ` (실패 이유: 막힘)` 를 붙임
  - 실패: `실패 이유: <failed_reason>`
  - 할 일, 실행 중: 빈칸
- 상태: 확답 (사용자 "ㅇㅇ 이대로 고고고", 2026-11-20. 의미 단위로 함수를 나눠 달라는 요청을 반영: notify_task 는 순서만, notify_messages 는 경우마다 글, node_table 은 칸마다 함수)

### 묶음 5-3: plan-run 스킬과 e2e (계획서, 2026-11-20)

요청: "넵" (사용자, 2026-11-20, 묶음 5 의 3·4번 계획). 흐름은 FLOWS 에 이미 "plan_run" 으로 등록되어 있다. 남은 조립은 사용자가 부를 스킬 하나.

나누기
- 포트·model·공통 기능: 없음
- 플러그인: plugin/skills/plan-run/SKILL.md (새로)

스킬 전문: 아래 "plan-run 스킬" (plan-go 스킬과 같은 모양. 다른 점은 명령을 백그라운드·70분으로 부르는 것과 Stop 훅 안내 한 줄, 끝 글을 그대로 보이는 것)

일괄 시험(2026-11-20)에서 본 것과 반영
- 세 회차 모두 실행 시작 직후 Stop 훅이 "next 로 다음 지시를 받으세요" 로 끼어듦. start 가 작업 지시 견적(show)을 곧바로 돌려줘 백그라운드 명령이 이미 끝났기 때문 (훅은 명령이 도는 중이면 막지 않음, engine/hook/stop_hook.py). 3회에서는 세션이 앞 명령의 출력을 읽기 전에 next 를 불렀다. → 스킬에 "훅이 next 를 부르라고 하면 먼저 앞 명령의 출력을 읽어 그 지시를 처리한다" 한 줄
- 끝 글을 세션이 줄이거나 덧붙이지 않게 "그대로" 를 적는다

e2e
- 코드 사본: 이번 커밋의 git worktree (scratchpad), mock 저장소는 페르소나·지식만 복사
- 할 일 하나: 문서 노드 3~4개 + 확인 노드 하나
- 확인할 것: /task-planner:plan-run (id 없이) → 계획 목록, /task-planner:plan-run <id> → 견적 → 노드 실행 → 확인 대화 → 허가 → 끝 알림 표가 그대로 보임, 계획 상태 끝남, Stop 훅이 끼어들어도 앞 출력을 먼저 처리함

## 같이 쓰는 코드

- 조건 함수: `workflow/plan_run/` 아래 (묶음 1 에서 위치 확정). 쓰는 단계: resume, prompts, rounds 안 묶음
- 작업 지시 만들기 함수: write_prompts 가 만들고 retry_prompt 가 쓴다
- 다음 노드 계산(`runnable_nodes`, `waiting_confirm_nodes`), 건너뛰기 전파, 진행 상태 계산: model 에 둘지 묶음 3 의 준비(tool-planner)에서 정한다
- 노드 실행용 claude -p: `claude_utils/agent/run_agent.py`

## 하위 작업 순서

진행 단위 (사용자, 2026-11-19): "호흡이 길기 때문에 … 하나씩 만들고 검수받으면서 가는게 적절할듯". 묶음마다 상세 확답 → 준비(필요하면 tool-planner) → tool-add-*-task → 시험 → 별도 에이전트 리뷰 → 검수 → 다음 묶음.

| 묶음 | 단계 | 검수받을 원문 | 묶음 끝 시험 |
|---|---|---|---|
| 1 | find_plan, start_run, resume (check_broken, ask_rerun, apply_rerun) | 질문 글 | 흐름을 묶음 1 까지 선언하고 임시 끝 단계를 붙여 CLI 로 |
| 2 | prompts (count_prompts, show_estimate, write_prompts, ask_retry, retry_prompt) | 작업 지시 프롬프트 전문 (node_prompt.md 를 옮기고 "앞 노드에서 받는 것" 절을 고침), 입력 글 예시 | 가짜 claude 로 prompt.md 가 생기는지 |
| 3 | rounds 의 다음 노드 계산 (runnable_nodes, waiting_confirm_nodes, 건너뛰기 전파) | — | 시뮬레이션의 경우들을 단위 시험으로 |
| 4 | run_agent, run_nodes, confirm, failed | 노드 실행 지시문 전문, 질문 글 | 먼저 확인: run_agent 의 권한·훅 설정이 먹는지, 긴 명령을 백그라운드로 부르고 기다리는 것이 engine 과 맞물리는지. 그 뒤 가짜 claude 로 시뮬레이션 그대로 |
| 5 | finish_plan, notify, 조립(선언, FLOWS, plan-run 스킬) | 알림 글, plan-run 스킬 전문 | CLI 로 끝까지, e2e (노드 3~4개, 확인 노드 하나) |

## 정할 것

1. 메인 세션이 긴 명령(run_nodes 가 도는 next·done)을 백그라운드로 부르고 기다리게 할지 (묶음 4 전에 확인)
2. 루프가 도는 동안 진행이 화면에 안 보임. 첫 판은 기록 파일에 노드 시작·끝만 남기는 안 (묶음 4)
3. 명령이 끊겨도(예: 메인 세션의 10분 한도) run_agent 가 띄운 claude -p 는 끝까지 돌고 그 결과는 버려진다. 자식을 새 프로세스 그룹으로 띄우기 때문이다. 묶음 2 리뷰 지적, 실제로 생긴 적은 없음. 노드 실행은 10분을 넘기는 것이 보통이라 묶음 4 에서 1 과 함께 본다
4. 노드 실행에 앞 노드 결과를 넘기는 방식: 결과 본문을 읽어 넣을지, 실행 데이터 (확정) 3 절의 조회 결과(노드 id, 제목, 상태, 회차, result.md 경로, files 목록, 건너뛴 이유)만 넘기고 claude -p 가 Read 로 읽게 할지 (묶음 4)

## 확인 결과

## 계획서 확답                             상태: 흐름도·루프 설계 확답, 단계별 상세는 묶음마다

## 진행 기록
- 2026-11-19 묶음 1 (사용자 "ㅇㅇ 이대로 진행해"):
  - model: NodeRun.back_to_todo() (model/node_run/node_run.py), 시험 tests/model/node_run/test_node_run.py, specs/models.md 갱신
  - find_plan: find_plan/find_plan_task.py, command_plan_id.py, current_transcript.py, runnable_check.py, plan_not_runnable_error.py. 키 plan_run.find_plan
  - start_run: start_run/start_run_task.py. 키 plan_run.start_run
  - resume/check_broken: check_broken_task.py. 키 plan_run.check_broken
  - resume/broken_each: broken_nodes_items.py(plan_run.broken_nodes), rerun_choices.py, ask_rerun/ask_rerun_task.py(plan_run.ask_rerun), apply_rerun/apply_rerun_task.py(plan_run.apply_rerun)
  - 조건: was_running.py(plan_run.was_running), not_stopped.py(plan_run.not_stopped, 묶음 2 부터 씀), stopped_node.py
  - 임시 끝 단계: wip_notice/wip_notice_task.py(plan_run.wip_notice). 묶음 5 에서 notify 로 바꿈
  - 선언 plan_run_flow.py, registry.py 에 "plan_run"
  - 시험: tests/workflow/test_plan_run.py (처음 실행, 이어 가기 완료 기록·다시 실행·멈추기·선택지 밖의 답, run.json 없는 노드, 실행할 수 없는 상태 셋, 없는 계획), tests/workflow/plan_run/test_command_plan_id.py, test_runnable_check.py
  - 검증: ruff check, mypy, lint-imports 4/4, pytest 175 통과. 시작 확인: 대화 기록이 없을 때 find_plan 이 멈춤 글을 냄
  - 계획서 고침: 흐름도 check_broken 줄과 시뮬레이션 마지막 줄의 "result.md 첫 줄로 판정" → "result.md 가 있으면 완료" (사용자 확인)
- 2026-11-19 묶음 1 리뷰 반영 (별도 에이전트 리뷰 지적 1 건, 사용자 "가로 고치고 테스트 고고"):
  - 끊긴 노드를 한 질문에 모아 묻기. resume/broken_each 와 broken_nodes_items.py 를 지우고 resume/ask_rerun, resume/apply_rerun, resume/rerun_choices.py 로. 조건 has_broken.py 더함. stopped_node.py 의 stopped_nodes 는 apply_rerun 결과 하나만 본다
  - 시험: 끊긴 노드 둘을 한 번에 다시 실행, 둘에서 멈추면 상태 그대로·알림에 둘 다, 끊긴 노드 없는 이어 가기
  - 검증: ruff check, mypy, lint-imports 4/4, pytest 177 통과
- 2026-11-19 묶음 2 (사용자 "오케이 좋소 이대로 한번 해봅시다"):
  - 공통 기능: claude_utils/agent/run_agent.py, agent_call_error.py, dto/agent_result.py. 시험 tests/claude_utils/test_run_agent.py. 실제 claude(haiku)로 작업 폴더 파일 읽기 확인
  - 단계: prompts/count_prompts, show_estimate, write_prompts(write_node_prompts.py, node_prompt_input.py, prompt_write_node_prompt.md, writing.md), ask_retry, retry_prompts, retry_choices.py. 조건 has_missing_prompts, has_failed_prompts
  - 바꿈: stopped_node.py 를 stop_point(context, upto) 로 (멈춘 자리 종류와 노드). not_stopped 에 upto 인자 (선언의 읽기 검사가 뒤 단계 읽기를 막으므로). wip_notice 에 만든 작업 지시 수와 작업 지시 실패 멈춤 글
  - 프롬프트: 기존 node_prompt.md 에서 맨 위 주석 줄을 빼고, 확인받은 두 문장만 고침. writing.md 그대로
  - 시험: 묶음 1 시험의 노드에 작업 지시를 미리 넣어 작업 지시 만들기를 건너뜀. 더한 것: 원문 절·글쓰기 규칙 붙임과 입력 글(앞 노드 산출물 스펙, 담당, 결과 위치 없음), 있는 prompt.md 지킴, 실패 한 질문 → 다시 만들기, 멈추기·다시 실패면 멈춤, 끊긴 노드에서 멈추면 작업 지시 만들기 건너뜀
  - 검증: ruff check, mypy, lint-imports 4/4, pytest 189 통과
- 2026-11-20 묶음 2 리뷰 (지적 3 건): 반영하지 않음 (사용자). 1 다시 돌면 덮어씀(일어나지 않을 상황 전제), 3 claude 실행 파일 없음(다시 만들어도 실패). 2 자식 claude 가 남음은 정할 것 3 으로 묶음 4 에서
- 2026-11-20 묶음 3 (사용자 "오케이 진행 후에 테스트 까지 진행 해주세요"):
  - model: model/plan/plan_schedule.py (runnable_nodes, waiting_confirm_nodes, nodes_to_skip, plan_progress), model/plan/plan_progress.py (PlanProgress). Plan, PlanNode 는 그대로. specs/models.md 갱신
  - 시험: tests/model/plan/test_plan_schedule.py 18 개 (시뮬레이션의 노드 상태마다 고를 노드와 확인 노드, limit, 건너뛰기 번짐 다섯 경우와 실행 중 뒤 노드, 진행 상태, 막힘)
  - 검증: ruff check, mypy, lint-imports 4/4, pytest 207 통과
  - 아직 흐름에서 쓰지 않음. 묶음 4 의 run_nodes, apply_failed 와 묶음 5 의 finish_plan, notify 가 쓴다
- 2026-11-20 묶음 4 (사용자 "네 그렇게 바꿔서 진행 해주세요"):
  - port: StopMark (dto/stop_mark.py), stop_mark_file_converter.py, read_stop / save_stop (`.plan/<id>/stop.json`), plan_folder_location.stop_file. specs/ports.md 갱신
  - port 더한 것 (계획서에 빠졌던 것): PlanFolderWriter.write_result. 확인 노드의 result.md 를 우리 코드가 쓰는 데 필요 (계획서의 finish_confirm 이 쓰기로 한 것)
  - run_agent: append 인자 (--append-system-prompt), install_child_cleanup (SIGTERM·SIGINT·끝날 때 돌던 자식 그룹을 끝냄). write_node_prompts 도 부른다
  - 단계: rounds/run_nodes (run_nodes_task, run_until_question, node_steps, node_run_input, node_outcome, node_run_message.md), confirm (show_confirm TALK, ask_confirm, finish_confirm), failed (ask_failed, apply_failed), round_items, stopped_at, save_stop
  - 바꿈: stopped_node 에 rounds 단계(멈춤 표시), wip_notice 에 끝남·막힘·남음, plan_run_flow 에 rounds 묶음
  - 확인 대화 구간: engine 의 대화 결과 from 은 흐름 시작 시각이라, 사용자 말은 run_nodes 가 돌아온 시각(finished_at)부터 대화가 끝난 시각까지로 읽는다
  - 시험: 시뮬레이션 그대로(3 실패 → 다시 실행 2 회차 → 확인 대화 → 허가 → 끝), 코드 노드 겹치지 않음·문서 노드 동시, 건너뛰기 번짐, 멈추기 뒤 남은 차례가 묻지 않고 다음 /plan-run 이 다시 물음, 고쳐서 다시, 허가하지 않음, 30분 마감 뒤 "계속". run_agent 덧붙이기, 부모가 SIGTERM 을 받으면 자식이 끝남. stop.json, write_result
  - 묶음 1·2 시험: 흐름이 노드 실행까지 이어지므로 가짜 claude 로 노드도 실행하게 함 (끊긴 노드를 다시 실행하면 이어서 완료까지)
  - 검증: ruff check, mypy, lint-imports 4/4, pytest 218 통과
- 2026-11-20 묶음 4 리뷰 반영 (사용자 "ㅇㅇㅇ 이렇게 해주라"):
  - 지적: run_nodes 가 30분 마감으로 "계속"을 돌려줘도 뒤에 알림·질문 단계가 없어, engine 이 같은 next 안에서 다음 차례를 바로 돌린다. next 한 번이 70분 제한을 넘고 그때 돌던 노드의 작업을 잃는다
  - 고침: rounds 안 run_nodes 다음에 continue_notice (MAIN_SESSION_SHOW, run_if stopped_at("continue")). 글은 "노드 N개를 마쳤습니다. 남은 노드 M개를 이어서 실행합니다." 와 노드마다 `- 노드 <id> "<제목>": .plan/<계획 id>/nodes/<노드 id>/result.md`
  - 작업 지시 만들기 뒤에도 알림을 두는 안은 뺐다. 작업 지시 하나에 1분 안팎이라, 첫 차례(최대 60분)와 합쳐도 70분 안에 든다
  - 시험: 30분 마감 시험이 첫 차례 뒤 알림을 보고, 다음 next 에서 둘째 차례가 도는지 확인하게 바꿈. pytest 218 통과
- 2026-11-20 묶음 4 리뷰 반영 2 (사용자 "아 오케이 해보자"):
  - 지적: 실패 이유와 요약을 그 차례의 run_nodes 결과에만 둬서, 같은 차례의 두 번째 실패 노드나 다음 /plan-run 에서 다시 묻는 노드는 "지난 실행에서 끝나지 못하고 남음"으로 보였다
  - 고침: NodeRun 과 run.json 에 failed_reason, failed_summary (기본 None, 키가 없는 기존 run.json 도 읽힘). finish_node 가 실패면 쓰고, start 가 비우고, _failure_detail 이 run.json 에서 읽는다. specs/models.md, 실행 데이터 (확정) 1 절 갱신
  - 시험: 다음 /plan-run 이 실제 이유를 보임(기대값 바꿈), 같은 차례 두 실패 뒤 둘째의 이유, start 가 비움, run.json 저장·옛 모양 읽기. pytest 221 통과
- 2026-11-20 묶음 5-1 finish_plan (사용자 "아 오키오키"):
  - 평가: port 충족 (PlanApiReader.get_plan, PlanApiWriter.set_plan_status), model 충족 (plan_progress, PlanStatus.can_move_to). 준비 단계 없음
  - 단계: finish_plan/finish_plan_task.py (plan_run.finish_plan). 선언에서 rounds 다음, wip_notice 앞
  - 바꿈: wip_notice 글 "(계획 끝내기와 결과 표는 아직 …)" → "(결과 표는 아직 …)". 시험 test_should_move_approved_plan_to_running 의 기대 상태 RUNNING → DONE (노드 없는 계획은 바로 끝남)
  - 시험: 모든 노드를 마친 시험 3개와 끊긴 마지막 노드를 완료로 기록하는 시험에 계획 상태 끝남(리뷰 지적), 멈추기 시험에 실행 중 그대로
  - 검증: ruff check, mypy, lint-imports 4/4, pytest 221 통과
- 2026-11-20 A~D 일괄 시험 3회 (별도 사본 b7ed3de + 임시 plan-run 스킬, 보고서 scratchpad/e2e/e2e-batch-report.md): 3회 모두 끝까지 감, 계획 상태 끝남. 사용자 판단:
  - 계획을 만든 직후 표가 안 보임: 계획을 서버로 보내 웹 뷰어로 보일 것이라 해결로 봄
  - 병합한 지식에 어긋나는 규칙이 같이 남음: 사용자가 고르는 것이라 두고, 나중에 웹 뷰어에서 확인
  - 노드가 사람만 판단할 기준으로 막힘: 그대로 둠. 막힌 뒤 "작업 지시를 고쳐 다시" → 대화로 prompt.md 고침 → plan-run 다시 부르기로 이어 갈 수 있음 ("대화만 가능하면 상관이 없기는 해")
  - 빈 작업 폴더에서 인터뷰가 이 도구 자신을 대상으로 권함: 대상을 물었으므로 고치지 않음 ("물어봤다면 상관없어. 100% 자동화 할 순 없거든")
  - Stop 훅이 실행 시작 직후 끼어듦: 묶음 5-3 plan-run 스킬을 만들 때 같이 봄
- 2026-11-20 묶음 5-2 notify (사용자 "ㅇㅇ 이대로 고고고"):
  - 평가: port 충족 (get_plan, read_run, result_file, stop_point), model 충족 (plan_progress, NodeRun)
  - 단계: notify/notify_task.py (plan_run.notify), notify_messages.py, node_table.py. wip_notice 지움. 선언 reads 에서 write_prompts 를 빼고 finish_plan 을 더함
  - 시험 기대값: 끝 글 "실행 중으로 두었습니다", "모든 노드를 마쳤습니다", "작업 지시 2개를 새로 만들었습니다" → "을 마쳤습니다". 시뮬레이션 시험에 노드 수 줄·표 머리·회차 2 줄·확인 칸 확인 더함
  - 새 시험: tests/workflow/plan_run/test_node_table.py (노드 수 줄, 상태별 칸), test_notify_messages.py (멈춤 세 경우, 막힘, 남음)
  - 시험에서 본 것: 확인한 말을 대화 기록에서 초 단위로 자르므로, 1초 안에 몰린 시험 대화에서는 명령 줄 "/task-planner:plan-run 1" 까지 확인한 말로 잡힌다. 실제 대화(명령과 확인이 몇 분 떨어짐)에서는 생기지 않음 (e2e9 의 run.json confirm 은 사용자 답만 담김). 시험은 확인 칸의 시작만 본다
  - 리뷰 지적 (사용자 "넵"): claude -p 가 오류로 끝나 여러 줄 stderr 가 실패 이유로 남은 노드를 건너뛰면 표가 깨짐 → 표 칸의 실패 이유를 한 줄로, | 를 \| 로 (node_table.one_line). 시험 하나 더함
  - 검증: ruff check, mypy, lint-imports 4/4, pytest 227 통과
- 2026-11-20 묶음 5-3 plan-run 스킬 (사용자 "두는 쪽으로 하고 맥락에 대한 설명을 주석으로 잘 남겨줘", "스킬에 저걸 넣으면 그냥 컨텍스트에 추가되는거 아님? 적고 싶으면 별도 파일에"):
  - plugin/skills/plan-run/SKILL.md: plan-go 와 같은 모양 + 백그라운드·70분, Stop 훅 안내 한 줄, finished 는 그대로. spawn 줄은 둠
  - 맥락 설명은 plugin/skills/plan-run/README.md (SKILL.md 는 세션 컨텍스트에 그대로 들어가므로)
  - e2e10 (사본 f182994 + 이 스킬, 보고서 scratchpad/e2e/e2e10-report.md): 성공. 끝 알림이 명령의 글과 한 글자도 다르지 않게 보임, Stop 훅 뒤 앞 출력부터 처리, 명령 6개 모두 백그라운드·4200000, id 없이 부르면 목록, 계획 끝남
  - e2e10 에서 본 것 (하, 두기로): 확인 대화가 "통과/수정 요청"을 예고했는데 질문은 허가/허가하지 않음. 계획 만들기가 "확인 → 수정 반영" 으로 나눠 통과해도 수정 반영 노드가 돎
