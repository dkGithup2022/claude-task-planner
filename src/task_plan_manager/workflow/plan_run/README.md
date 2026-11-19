# plan_run (D 계획 실행)

승인된 계획의 계획 노드를 간선 순서대로 실행하는 워크플로. 계획서: `specs/plans/workflow-plan_run.md`.
2026-11-19 기준으로 묶음 1(계획 찾기와 실행 시작), 묶음 2(작업 지시 만들기)까지 만들었다. 묶음 3~5 는 아직 없다.

## 지금 구성

```
plan_run
├─ find_plan        [CODE]               대화 기록의 /…plan-run <id> → 계획 조회. 승인·실행 중이 아니면 멈춤
├─ start_run        [CODE]               승인 → 실행 중. 이미 실행 중이면 그대로 (was_running)
├─ resume           [IN_ORDER] [run_if: plan_run.was_running]
│  ├─ check_broken  [CODE]               실행 중으로 남은 노드: result.md 가 있으면 완료로 기록, 없으면 목록
│  ├─ ask_rerun     [MAIN_SESSION_ASK] [run_if: plan_run.has_broken]   한 질문에 모아: 모두 다시 실행 / 멈추기
│  └─ apply_rerun   [CODE] [run_if: plan_run.has_broken]               모두 todo 로 / 멈춤 표시
├─ prompts          [IN_ORDER] [run_if: plan_run.not_stopped(upto=resume)]
│  ├─ count_prompts [CODE]               prompt.md 가 없는 노드, 대략의 시간·비용
│  ├─ show_estimate [MAIN_SESSION_SHOW] [run_if: plan_run.has_missing_prompts]
│  ├─ write_prompts [CODE] [run_if: plan_run.has_missing_prompts]      run_agent(읽기 도구, opus) 3개씩 동시
│  ├─ ask_retry     [MAIN_SESSION_ASK] [run_if: plan_run.has_failed_prompts]   한 질문에 모아: 모두 다시 만들기 / 멈추기
│  └─ retry_prompts [CODE] [run_if: plan_run.has_failed_prompts]      한 번 더. 그래도 실패하면 멈춤
└─ wip_notice       [MAIN_SESSION_SHOW]  임시 끝 단계. 묶음 5 에서 notify 로 바꾼다
```

| 파일 | 하는 일 |
|---|---|
| `plan_run_flow.py` | 선언. `workflow/registry.py` 에 `"plan_run"` 으로 등록 |
| `find_plan/find_plan_task.py` | 읽기(명령 줄 id, 계획 저장소, 계획 폴더) → 판정. 출력 `{plan_id, title, status}` |
| `find_plan/command_plan_id.py` | 대화에서 사용자가 마지막으로 친 `/…plan-run <id>` 줄의 id |
| `find_plan/current_transcript.py` | 세션 시작 훅이 남긴 대화 기록 경로 |
| `find_plan/runnable_check.py` | 상태마다 멈출 때의 글 (작성 중, 검토 중, 불허, 끝남) |
| `find_plan/plan_not_runnable_error.py` | 멈춤 오류. 메시지를 사용자에게 그대로 보인다 |
| `start_run/start_run_task.py` | 출력 `{was_running}` |
| `resume/check_broken/check_broken_task.py` | 출력 `{nodes: [{node_id, title}], recorded_done: [id]}` |
| `resume/ask_rerun/ask_rerun_task.py` | 출력 `{answer}`. 선택지 밖의 답은 다시 묻는다 |
| `resume/apply_rerun/apply_rerun_task.py` | 출력 `{stopped}` |
| `resume/rerun_choices.py` | 선택지 `모두 다시 실행`, `멈추기` |
| `prompts/count_prompts/count_prompts_task.py` | 출력 `{missing: [{node_id, title}], minutes, cost_low, cost_high}` |
| `prompts/show_estimate/show_estimate_task.py` | "노드 N개의 작업 지시를 만듭니다. 약 M분, $lo~hi 안팎" |
| `prompts/write_prompts/write_prompts_task.py` | 출력 `{made: [{node_id, cost_usd, seconds}], failed: [{node_id, title, reason}]}` |
| `prompts/write_prompts/write_node_prompts.py` | 노드마다 생성기 호출 → 첫 줄 검사 → 산출물 스펙 원문 절·글쓰기 규칙 붙여 prompt.md. retry 도 씀 |
| `prompts/write_prompts/node_prompt_input.py` | 생성기 입력 글 (명령서, 노드, 산출물 스펙, 앞 노드의 산출물 스펙, 담당 페르소나, 지식 "(없음)") |
| `prompts/write_prompts/prompt_write_node_prompt.md`, `writing.md` | 생성기 프롬프트 (기존 node_prompt.md 에서 앞 노드 절 두 문장만 고침), 글쓰기 규칙 (그대로) |
| `prompts/ask_retry/`, `prompts/retry_prompts/`, `prompts/retry_choices.py` | 실패한 노드를 한 질문에 모아 다시 만들기 |
| `was_running.py`, `has_broken.py`, `has_missing_prompts.py`, `has_failed_prompts.py`, `not_stopped.py` | 조건 |
| `stopped_node.py` | `stop_point(context, upto)`: 멈춘 자리(끊긴 노드 / 작업 지시 없음)와 노드 id. 조건과 알림이 같이 쓴다 |
| `wip_notice/wip_notice_task.py` | 임시 알림 |

쓰는 공통 기능: `claude_utils/agent/run_agent.py` (도구를 쓰는 claude -p. 작업 폴더에서, 켠 도구만 묻지 않고, 훅 끄고).

쓰는 model·port: `Plan`, `PlanNode`, `Persona`, `PersonaApiReader.list_personas`, `PlanFolderReader.read_command·read_prompt`, `PlanFolderWriter.write_prompt`,, `PlanStatus`, `PlanNodeStatus`, `NodeRun`(`back_to_todo` 를 이번에 더함), `PlanApiReader.get_plan`, `PlanApiWriter.set_plan_status·update_node`, `PlanFolderReader.list_plan_ids·read_output·read_run`, `PlanFolderWriter.save_run`.

시험: `tests/workflow/test_plan_run.py` (CLI 로 끝까지), `tests/workflow/plan_run/` (명령 줄 읽기, 상태별 판정), `tests/model/node_run/test_node_run.py`.

## 특이사항

- **사용자는 아직 부를 수 없다.** plan-run 스킬은 묶음 5 에서 만든다. 지금은 CLI 시험으로만 돈다.
- **계획 id 는 대화 기록의 명령 줄에서 읽는다.** run 스킬 방식으로는 흐름에 인자를 넘길 수 없기 때문이다 (confirm_plan 과 같은 방식). 대화 읽기 함수는 Claude 가 도구로 부른 스킬은 빼고 읽는다. 그래서 끝 지시가 다음 `/plan-run` 을 스스로 부르는 방식은 id 를 못 찾는다. 노드 실행의 반복을 흐름 안(우리 루프)에 두기로 한 이유 가운데 하나다.
- **다른 워크플로의 코드를 가져오지 않는다** (번들 규칙). 명령 줄 읽기와 대화 기록 경로는 confirm_plan 의 것을 plan_run 에 따로 두었다 (정규식만 plan-run). 계획 상태를 한국어로 바꾸는 list_plans 의 `status_label` 은 쓰지 않고, 멈출 때의 글을 상태마다 직접 적었다.
- **engine 의 항목마다 반복(FOR_EACH_ITEM)은 앞 항목의 답과 상관없이 모든 항목을 끝까지 돈다.** 첫 판은 끊긴 노드마다 물었다. 그랬더니 리뷰에서 "멈추기를 골라도 다음 노드를 또 묻고 상태를 바꾼다"가 나왔다. 그래서 한 질문에 모아 묻는 것으로 바꿨다. 반복 안에서 "앞에서 멈췄으면 건너뛰기"가 필요하면, 앞 번호의 결과만 보는 조건을 따로 둬야 한다.
- **흐름의 마지막 보이기 단계의 글은 끝 지시(`finished`)에 실려 온다.** `show` 가 따로 오지 않는다.
- **끊긴 노드의 판정은 result.md 가 있는지로만 한다.** 첫 줄 `status:` 는 claude -p(run_agent)의 답에 있고 result.md 에는 없다. 끊긴 노드는 그 답을 잃은 상태다 (HTML D 1-1, 기존 plan-run SKILL.md:19 와 같음).
- **run.json 없이 실행 중인 노드가 있을 수 있다.** 시작 기록을 쓰기 전에 끊긴 경우다. 결과 파일이 있으면 1회차 기록을 새로 만들어 완료로 남긴다.
- **상태의 원본은 계획 저장소의 노드 상태다.** run.json 의 상태는 같은 값의 사본이다. 쓰는 순서는 run.json 을 먼저, 계획 저장소를 다음으로 한다. 그 사이에 끊겨도 다시 돌면 같은 기록을 다시 쓸 뿐이다.
- **`not_stopped` 는 `upto` 인자를 받는다.** 선언의 읽기 검사는 조건이 자기보다 뒤에 도는 단계를 읽지 못하게 막는다. 그래서 조건마다 "어느 묶음까지의 멈춤을 볼지"를 준다 (`{"upto": "resume"}`). 뒤 묶음의 멈춤(노드 실행 중 멈추기 등)은 `stopped_node.py` 의 `STAGES` 에 더한다.
- **작업 지시 생성기는 도구를 쓴다.** 프롬프트가 생성기의 조사(라이브러리, 웹 검색)를 전제하므로 run_agent 에 읽기 도구(Read, Glob, Grep, WebSearch, WebFetch)만 켜서 부른다. 한 노드 15분, opus. 실제 claude 로 작업 폴더 파일을 묻지 않고 읽는 것을 확인했다 (2026-11-19)
- **prompt.md 가 이미 있으면 만들지 않는다.** 사람이 고친 것을 지키려는 것이고, 해시는 남기지 않는다. 다시 만들고 싶으면 그 prompt.md 를 지우고 /plan-run 을 다시 부른다
- **작업 지시 만들기는 한 단계 안에서 노드 전부를 만든다.** 노드 30개를 넘으면 10분(메인 세션이 명령을 기다리는 한도)을 넘길 수 있다. 백그라운드로 부르고 기다리기는 묶음 4 에서 확인한다
- **`TASK_PLAN_MANAGER_CLAUDE_BIN`** 을 run_agent 도 쓴다. 시험의 가짜 claude 가 call_prompt 와 run_agent 를 함께 대신한다
- **보류**: 지난 실행에서 실패로 남은 노드(멈추기를 고른 노드 등)를 다시 실패 처리로 묻는 자리가 없다. 묶음 3 의 다음 노드 계산에서 다룬다.
- **검증 (2026-11-19)**: ruff check, mypy, lint-imports 4/4, pytest 189 통과.
