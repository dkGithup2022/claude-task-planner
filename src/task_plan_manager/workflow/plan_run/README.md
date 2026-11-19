# plan_run (D 계획 실행)

승인된 계획의 계획 노드를 간선 순서대로 실행하는 워크플로. 계획서: `specs/plans/workflow-plan_run.md`.
2026-11-19 기준으로 묶음 1(계획 찾기와 실행 시작)까지 만들었다. 묶음 2~5 는 아직 없다.

## 지금 구성

```
plan_run
├─ find_plan        [CODE]               대화 기록의 /…plan-run <id> → 계획 조회. 승인·실행 중이 아니면 멈춤
├─ start_run        [CODE]               승인 → 실행 중. 이미 실행 중이면 그대로 (was_running)
├─ resume           [IN_ORDER] [run_if: plan_run.was_running]
│  ├─ check_broken  [CODE]               실행 중으로 남은 노드: result.md 가 있으면 완료로 기록, 없으면 목록
│  ├─ ask_rerun     [MAIN_SESSION_ASK] [run_if: plan_run.has_broken]   한 질문에 모아: 모두 다시 실행 / 멈추기
│  └─ apply_rerun   [CODE] [run_if: plan_run.has_broken]               모두 todo 로 / 멈춤 표시
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
| `was_running.py`, `has_broken.py`, `not_stopped.py` | 조건 |
| `stopped_node.py` | `stopped_nodes(context)`: 멈추기를 고른 자리의 노드 id. 조건과 알림이 같이 쓴다 |
| `wip_notice/wip_notice_task.py` | 임시 알림 |

쓰는 model·port: `Plan`, `PlanStatus`, `PlanNodeStatus`, `NodeRun`(`back_to_todo` 를 이번에 더함), `PlanApiReader.get_plan`, `PlanApiWriter.set_plan_status·update_node`, `PlanFolderReader.list_plan_ids·read_output·read_run`, `PlanFolderWriter.save_run`.

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
- **`not_stopped` 조건은 아직 쓰는 곳이 없다.** 묶음 2(작업 지시 만들기)부터 건다. 뒤 묶음의 멈춤(노드 실행 중 멈추기 등)은 `stopped_node.py` 에 더한다.
- **보류**: 지난 실행에서 실패로 남은 노드(멈추기를 고른 노드 등)를 다시 실패 처리로 묻는 자리가 없다. 묶음 3 의 다음 노드 계산에서 다룬다.
- **검증 (2026-11-19)**: ruff check, mypy, lint-imports 4/4, pytest 177 통과.
