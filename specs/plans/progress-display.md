# 계획: 진행 표시 (Claude Code 상태 줄에 지금 단계와 진행 상황)

## 요청

- 사용자 (2026-11-20): "지금 각 단계에서 지금 우리가 어느 단계인지, 그리고 현재 단계에서는 진행 상황이 어떤지를 클코에 상단에 뭔가 표시가 되어야 할듯"
- 설계 대화 기록: corbina/notes/2026-11-20-progress-display.md (re_code.html "진행 표시" 탭). 장면은 그 문서 6 절, 데이터 스펙은 7 절

정한 것 (사용자, 2026-11-20)
- 주요 상황마다 상태를 덧붙여 기록하는 문서를 하나 둔다. 흐름과 별개 모듈로 보여 주기용 model 과 port 를 두고, 각 단계가 이것을 부른다
- 기록은 계획 폴더 `.plan/<plan_id>/progress.jsonl`. 한 줄에 그 순간 보일 것 전체(스냅샷), 단계마다 담는 내용이 다르다
- 표시는 Claude Code 상태 줄. 5 초마다 다시 그린다. 상태 줄 설정은 작업 폴더마다 (`<작업 폴더>/.claude/settings.local.json`)
- 계획을 등록할 때부터 기록한다. 이 세션이 쓴 기록이 없으면 아무것도 보이지 않는다. 불허하면 보이지 않는다
- 실행 중인 노드가 여럿이면 "51 UI 문서 작성 외 1개"

## 1. 평가

### 나누기

- model: 진행 기록 (`model/progress/`)
- 포트
  - 진행 기록 읽기·쓰기 (`port/local/progress_log/`, 파일 `.plan/<plan_id>/progress.jsonl`)
  - 작업 폴더의 Claude Code 설정에 상태 줄 넣기 (`port/local/claude_settings/`, 파일 `.claude/settings.local.json`)
- 공통 기능: 없음
- 워크플로로 넘길 것 (이 계획서의 4 절에서 따로 다룸)
  - 진행 기록을 남기는 함수 `report_progress` 와, 흐름의 단계마다 부르는 곳
  - 상태 줄을 그리는 명령 `task_plan_manager statusline` (entry) 와 글 고르기

### tool-assess-port

- 진행 기록: 미충족. 새 포트 `ProgressLogWriter.append(event)`, `ProgressLogReader.latest_for_session(session_id)`. 경로 규칙은 `port/local/plan_folder/plan_folder_location.py` 에 `progress_file(plan_id)` 를 더한다 (계획 폴더의 경로 규칙을 한 곳에 두려고). 파일 형식 JSON Lines, 한 줄을 한 번의 쓰기로 덧붙인다
- Claude Code 설정: 미충족. 새 포트 `ClaudeSettingsWriter.ensure_statusline(command, refresh_seconds)`. 파일이 없으면 만들고, 있으면 다른 키는 그대로 두고 `statusLine` 만 넣는다. 이미 우리 명령이면 아무것도 하지 않는다
- 기존 포트 바꿈 없음

### tool-assess-model

- 미충족. 새 model `ProgressEvent`, 단계별 내용 `PlanningProgress`, `FeedbackProgress`, `ReinforceProgress`, `RunProgress`, `ClosedProgress`, 과정 enum `ReinforcePhase`, `RunPhase`, 실행 중 노드 `RunNode` (7 절 원문)
- 기존 model 바꿈 없음

## 2. 구현 계획

[정한 것]
- 상태 줄 명령은 받은 입력(stdin JSON)을 사용자 설정(`~/.claude/settings.json`)의 원래 상태 줄 명령에 그대로 넘긴 뒤 우리 줄을 찍는다. 작업 폴더 설정이 사용자 설정을 덮어써도 Orca 가 받던 데이터가 끊기지 않게 하려고 (Orca 스크립트는 화면에 찍지 않고 사용량 데이터를 넘긴다)
- 세션 id: 쓰는 쪽은 `CLAUDE_CODE_SESSION_ID` (CLI 가 이미 쓰는 값), 상태 줄은 입력의 `session_id`
- 기록에 실패해도 흐름은 멈추지 않는다 (보여 주기는 부가 기능)
- 화면 글은 기록하지 않는다. 상태 줄이 단계와 과정으로 정해진 글을 고른다
- 웹 주소는 서버 세션이 정한 뒤 넣는다. 그 전에는 넷째 줄의 "진행 상황 보기" 를 빼고 그린다
- 새 의존성 없음, 새 환경 변수 없음

[구현 순서]
1. add-model: `model/progress/` (7 절), 시험, specs/models.md
2. add-port: `port/local/progress_log/` (writer, reader, default 구현, `ProgressEventFileConverter`), `plan_folder_location.progress_file`, 시험, specs/ports.md
3. add-port: `port/local/claude_settings/` (writer, default 구현), 시험, specs/ports.md
4. 워크플로 쪽 (4 절)

## 3. 진행 기록

### 1. add-model (2026-11-20)
- 정함 (사용자, 2026-11-20): 승인 뒤 실행 전 장면은 초안대로 → `RunPhase.READY`
- 만든 파일: `model/progress/` 의 progress_event.py, planning_progress.py, feedback_progress.py, reinforce_phase.py, reinforce_progress.py, run_phase.py, run_node.py, run_progress.py, closed_progress.py
- 값을 바꾸는 동작이 없어 model 시험은 두지 않았다 (tool-add-model 6 절). 모양은 포트 변환기 시험에서 확인한다
- 처음 설계(진행 표시 탭 5-1)의 `ProgressStage`(첫 줄 단계)는 model 에 두지 않았다. detail 의 종류로 정해지고, 단계 이름과 순서는 상태 줄 글을 고르는 쪽이 갖는다
- 검증: ruff check·format 통과, lint-imports 4 kept, mypy 통과
- specs/models.md 에 progress 절

### 2. add-port: progress_log (2026-11-20)
- 만든 파일: `port/local/progress_log/` 의 progress_log_writer.py, progress_log_reader.py, default_progress_log_writer.py, default_progress_log_reader.py, progress_event_file_converter.py. `plan_folder_location.progress_file` 더함
- 읽기는 계획마다 파일 끝 64KB 만 본다. 다른 프로세스가 쓰는 중이라 반쯤 잘린 줄은 건너뛴다
- 시험: `tests/port/progress_log/test_progress_log.py` (다섯 종류 되읽기, 한 줄에 kind, 여러 계획 가운데 이 세션의 가장 최근, 다른 세션 것은 안 봄, 반쯤 쓴 줄 건너뜀)

### 3. add-port: claude_settings (2026-11-20)
- 만든 파일: `port/local/claude_settings/` 의 claude_settings_location.py, claude_settings_writer.py, claude_settings_reader.py, default_claude_settings_writer.py, default_claude_settings_reader.py, dto/statusline_setup.py
- 계획서와 다른 점 (Claude 판단, 작은 것)
  - `ClaudeSettingsReader.user_statusline_command` 를 더했다. 2 절 "원래 상태 줄 명령에 그대로 넘긴다" 를 하려면 사용자 설정을 읽어야 해서
  - 작업 폴더 설정에 사용자가 넣은 다른 상태 줄이 있으면 덮어쓰지 않는다 (`LEFT_ALONE`). 읽지 못하는 파일도 건드리지 않는다
- 시험: `tests/port/claude_settings/test_claude_settings.py`

검증 (1~3 끝): ruff check·format 통과, mypy 통과, lint-imports 4 kept, pytest 전체 통과

### 리뷰 반영 (2026-11-20, 사용자 허락)
- 상태 줄 설정: 플러그인을 마켓플레이스로 설치하면 실행 파일 경로에 버전 폴더(`…/task_plan_manager/0.1.0/bin/…`)가 들어간다. 버전이 바뀐 뒤에도 예전 경로가 남지 않게, 명령이 `/bin/task_plan_manager statusline` 으로 끝나는 우리 줄은 지금 명령으로 바꿔 적는다. 사용자가 넣은 다른 상태 줄은 그대로 둔다
- 진행 기록 읽기: 줄을 `\n` 으로만 나눈다. `splitlines()` 는 제목 안의 U+2028 같은 문자에서도 나눠 그 기록을 건너뛰었다
- 진행 기록 읽기: 파일 경로를 `progress_file(plan_id)` 로 만든다. `.plan/` 아래 이름이 숫자인 폴더만 본다
- 시험 3 개 더함 (예전 버전의 우리 줄 바꾸기, U+2028 이 든 제목, 계획이 아닌 폴더 무시). U+2028 시험은 고치기 전 코드에서 실패하는 것을 확인했다
- 검증: ruff check·format 통과, mypy 통과, lint-imports 4 kept, pytest 244 passed
- 4 절로 넘긴 것: 상태 줄 명령의 실행 파일 경로를 만드는 방법(지금 돌고 있는 코드 위치에서 계산하는 안), 상태 줄 입력의 `workspace.current_dir` 를 기준 폴더로 쓰기, 사용자 설정의 상태 줄이 우리 명령이면 다시 부르지 않기

## 4. 워크플로 쪽 (구현 순서 4)

### 정한 것 (사용자, 2026-11-20)
- 계획 고치기는 `plan edit` 명령이 시작할 때와 끝날 때 기록한다 (노드를 나누거나 넣으면 간선을 다시 정하느라 1 분 안팎이 걸린다)
- 실행을 마친 뒤에는 "계획을 마쳤습니다" 줄을 남긴다. 그 세션에서 다른 계획을 시작하면 바뀐다
- 설계 문서 6 절에 글이 없는 순간(후보 뽑기, 저장할지 고르기, 본문 확인, 최종 정리, 작업 지시 만들기, 확인 노드, 실패 처리)은 첫 줄(단계 표시)만 그린다
- 하나씩 만들고, 단계마다 사용자 검수를 받는다. 번들(dk-claude-tool-bundle) 규칙을 따른다

### 번들 규칙 때문에 처음 생각과 달라진 곳 (사용자 확인 필요)
- 처음 생각: `workflow/progress/report_progress.py` 에 기록 함수를 두고 흐름들이 부른다
- 번들 규칙(tool-add-code-task 4 절 금지): "다른 워크플로 폴더의 코드를 import 하지 않는다". 기록 함수는 계획 만들기, 계획 고치기, 계획 확정, 계획 실행이 모두 부르므로 workflow 아래에 둘 수 없다
- 안: 기록 포트가 시각과 세션 id 를 채우고 실패를 삼킨다. `ProgressLogWriter.append(event)` 를 `ProgressLogWriter.report(plan_id, detail)` 로 바꾼다

### 단계

| 단계 | 할 일 | 따르는 번들 규칙 | 검수 받을 것 |
|---|---|---|---|
| 1 | 기록 포트를 `report(plan_id, detail)` 로 바꿈 | tool-add-port (기존 포트 바꿈) | 바뀐 인터페이스와 시험 |
| 2 | 화면 글: `workflow/statusline/statusline_text.py` 의 `statusline_text(event, now) -> list[str]` | tool-add-code-task 로직 규칙 (순수 함수, 함수마다 시험) | 장면마다 실제로 찍힌 글 |
| 3 | 상태 줄 명령: `workflow/statusline/draw_statusline.py` 와 entry 의 `statusline` | entry 규칙 (인자 해석과 조립만). `workflow/plan_edit` 처럼 흐름이 아닌 기능 폴더 | 표준 입력을 넣어 찍힌 글, 원래 상태 줄 명령에 넘기기 |
| 4 | 계획 만들기·고치기에 붙임 (등록 직후 상태 줄 설정 포함) | tool-add-code-task, tool-add-session-task (기존 Task 바꿈) | 바뀐 곳 as-is / to-be, 흐름 시험에 남은 기록 |
| 5 | 계획 확정에 붙임 | tool-add-code-task, tool-add-session-task, tool-add-prompt-task | 같음 |
| 6 | 계획 실행에 붙임 | tool-add-code-task, tool-add-session-task | 같음 |
| 7 | 시험 작업 폴더(`tpm-trial/work`)에서 실제 화면 확인, 상태 줄 명령이 5 초 간격에 충분히 빠른지 | — | 실제 화면 |

단계마다: 만들기 → ruff·mypy·lint-imports·pytest → 별도 에이전트 리뷰 → 사용자 검수 → 진행 기록

### 기록하는 곳

| 흐름 | 파일 · 기록 시점 | 남기는 것 |
|---|---|---|
| 계획 만들기 | `register_plan_task` 마무리 (계획 id 가 생긴 직후) | `PlanningProgress(지금)`. 이때 `ensure_statusline(상태 줄 명령, 5)` |
| 계획 만들기 | `show_plan_task` 준비 | `FeedbackProgress(None)` |
| 계획 고치기 | `plan edit` 명령 시작 / 끝 | `FeedbackProgress(지금)` / `FeedbackProgress(None)` |
| 계획 확정 | `extract_knowledge_task` 준비 | `ReinforceProgress(EXTRACT, None, None, None, 지금)` |
| 계획 확정 | `choose_action_task` 준비 | `ReinforceProgress(CHOOSE, k, n, 주제, None)` |
| 계획 확정 | `write_knowledge_task` 준비 | `ReinforceProgress(DRAFT, k, n, 주제, 지금)` |
| 계획 확정 | `review_knowledge_task` 준비 | `ReinforceProgress(REVIEW, k, n, 주제, None)` |
| 계획 확정 | `finalize_knowledge_task` 준비 | `ReinforceProgress(FINALIZE, k, n, 주제, 지금)` |
| 계획 확정 | `record_decision_task` 마무리 | 승인 `RunProgress(READY, 0, 노드 수)`, 불허 `ClosedProgress()` |
| 계획 실행 | `write_node_prompts` 노드 하나 끝날 때마다 | `RunProgress(PROMPTS, k, n)` |
| 계획 실행 | `run_until_question` 노드를 띄울 때, 끝날 때 | `RunProgress(NODES, 완료 수, 전체, 실행 중 노드들)` |
| 계획 실행 | `show_confirm_task` 준비 / `ask_failed_task` 준비 | `RunProgress(CONFIRM / FAILED, …, 그 노드)` |
| 계획 실행 | `finish_plan_task` 마무리 | `RunProgress(FINISHED, 전체, 전체)` |

- 흐름의 단계는 준비(`build_request`)와 마무리(`build_output`) 사이에 시간이 걸리는 일(claude -p, 대화)을 한다. 그래서 대부분 준비에서 기록한다
- k 는 지금 후보가 후보 목록에서 몇 번째인지로 센다

### 상태 줄 명령이 하는 일
1. 표준 입력 JSON 에서 `session_id`, `workspace.current_dir` 를 읽는다
2. `workspace.current_dir` 로 폴더를 옮긴다 (기록은 그 작업 폴더의 `.plan/`)
3. 사용자 설정의 원래 상태 줄 명령에 같은 입력을 넘긴다 (Orca 사용량 데이터). 그 명령이 우리 명령이면 넘기지 않는다. 그 명령이 찍은 글은 버린다
4. `latest_for_session(session_id)` 로 읽어 2 단계의 글을 찍는다. 기록이 없거나 `ClosedProgress` 면 찍지 않는다

### 상태 줄 명령의 경로
- 지금 돌고 있는 코드 위치에서 `<저장소>/plugin/bin/task_plan_manager statusline` 을 계산한다 (`common/mock_data.py` 가 같은 방식으로 저장소 위치를 찾는다)
- 이 계산은 파이썬 코드가 `plugin` 폴더와 같은 저장소 안에 있어야 맞다. 마켓플레이스 배포 방식을 정할 때 다시 확인한다

### 4 의 1 단계: 기록 포트에 report (2026-11-20)
- 정함 (사용자, 2026-11-20): 기록 함수는 workflow 가 아니라 포트에 둔다 (번들 규칙: 다른 워크플로 폴더를 import 하지 않음)
- `ProgressLogWriter.report(plan_id, detail)`: 지금 시각과 `CLAUDE_CODE_SESSION_ID` 로 `append` 를 부른다. 세션 id 가 없으면 남기지 않고, OSError 는 삼킨다. `append` 는 시각을 넣어 시험하려고 남겼다
- 시험 3 개 (지금 시각과 세션으로 남김, Claude Code 밖이면 남기지 않음, 쓰지 못해도 오류 없음). 마지막 시험은 실패를 삼키는 부분을 빼면 실패하는 것을 확인했다
- specs/ports.md 의 progress_log 표에 report 줄
- 검증: ruff check·format 통과, mypy 통과, lint-imports 4 kept, pytest 247 passed
- 별도 에이전트 리뷰: 지적 없음 (report 밖으로 나갈 수 있는 실제 실패는 모두 OSError, 동시 덧붙이기도 줄이 섞이지 않음)

### 4 의 2 단계: 화면 글 (2026-11-20)
- 만든 파일: `workflow/statusline/statusline_text.py` (`statusline_text(event, now) -> list[str]`), 시험 `tests/workflow/statusline/test_statusline_text.py`
- 설계 문서 6 절의 장면 그대로. "진행 상황 보기" 링크는 웹 주소가 정해진 뒤 넣는다
- Claude 판단 (작은 것): 실행을 마치면 첫 줄의 "실행" 에도 ✓. 노드가 여럿이면 이름과 걸린 시간은 가장 먼저 시작한 노드 기준
- 검증: ruff check·format 통과, mypy 통과, lint-imports 4 kept, pytest 266 passed
- 별도 에이전트 리뷰: 지적 없음. 6 단계에서 볼 것: 노드 하나가 끝나고 다음 노드를 띄우기 전에 실행 중 노드가 빈 기록을 남기면 둘째·셋째 줄이 잠깐 사라진다
- 리뷰 참고 반영 (사용자, 2026-11-20 "(1) 만 고치면 될거 같은데"): 파일 안에서만 쓰는 함수 이름 앞에 `_` (저장소 관례). 시험이 첫 줄을 확인하게 하는 것은 하지 않음

### 4 의 3 단계: 상태 줄 명령 (2026-11-20)
- 만든 파일: `workflow/statusline/draw_statusline.py` (`draw_statusline(stdin_text) -> list[str]`), entry `cli.py` 에 `statusline`
- 하는 일: 사용자 설정의 원래 상태 줄 명령에 같은 입력을 넘김 (2 초까지 기다림, 찍은 글은 버림, 우리 명령이면 넘기지 않음) → 입력의 `workspace.current_dir` (없으면 `cwd`) 로 폴더를 옮김 → 이 세션의 마지막 기록을 그림
- 시험: `tests/workflow/statusline/test_draw_statusline.py` (작업 폴더의 기록을 그림, 세션이 없거나 입력이 깨지면 그리지 않음, 다른 세션·불허는 그리지 않음, 원래 명령에 같은 입력을 넘기고 그 글은 버림, 원래 명령이 우리 것이면 부르지 않음), `tests/test_cli.py` (기록이 없으면 아무것도 찍지 않음)
- 실제 실행 (`plugin/bin/task_plan_manager statusline`, 표준 입력으로 세션 정보): 한 번에 0.3~0.5 초, 처음 한 번 1.3 초
- 검증: ruff check·format 통과, mypy 통과, lint-imports 4 kept, pytest 274 passed
- 별도 에이전트 리뷰 지적 5 개는 모두 두기로 함 (사용자, 2026-11-20 "걍 내비 두자"): 원래 상태 줄 명령이 멈추면 손자 프로세스가 남음, 원래 명령에 이 저장소의 가상 환경이 넘어감, 기록 한 줄이 JSON 객체가 아니면 오류, CLI 시험이 현재 폴더를 바꾼 채 끝남, 원래 명령의 글을 버리는지 보는 시험이 약함

### 4 의 4 단계: 계획 만들기·고치기 (2026-11-20)
- 정함 (사용자, 2026-11-20): 흐름마다 `show_progress.py` 하나에 뜻 이름 함수로 묶고, 단계는 한 줄로 부른다
- 만든 파일: `workflow/make_plan/show_progress.py` (`show_planning_started`, `show_feedback_turn`), `workflow/make_plan/statusline_command.py`, `workflow/plan_edit/show_progress.py` (`showing_edit`)
- 바꾼 곳: `register_plan_task` (계획 폴더를 만든 뒤 `show_planning_started`), `show_plan_task` (`show_feedback_turn`), `edit_plan` (본문을 `_edit_plan` 으로 옮기고 `with showing_edit(plan_id)`)
- `tests/conftest.py`: 모든 시험에서 `CLAUDE_CODE_SESSION_ID` 를 지운다. 이 값이 있는 환경에서 시험을 돌리면 저장소 폴더에 `.plan/` 이 생길 수 있어서
- 별도 에이전트 리뷰 반영 (사용자 허락): 상태 줄 설정을 쓰지 못하면 `LEFT_ALONE` (계획 등록이 실패해 다시 돌리면 계획이 겹치는 것을 막음), 진행 기록은 이 작업 폴더에 그 계획 폴더가 있을 때만 (다른 폴더에서 `plan edit` 을 불러 빈 계획 폴더가 생기는 것을 막음)

### 4 의 5·6 단계: 계획 확정, 계획 실행 (2026-11-20)
- 만든 파일: `workflow/confirm_plan/show_progress.py` (`show_knowledge_step`, `show_decision`), `workflow/plan_run/show_progress.py` (`show_run_started`, `show_writing_prompts`, `show_running_nodes`, `show_waiting_answer`, `show_finished`)
- 부르는 곳: 후보 뽑기·고르기·초안·확인·최종 정리의 준비, 결정 기록, 실행 시작, 작업 지시 만들기 시작, 노드를 띄운 뒤와 차례가 끝난 뒤, 확인 노드·실패 처리 질문의 준비, 계획 끝내기
- 흐름 선언(`confirm_plan_flows.py`)의 reads: write_knowledge, review_knowledge, finalize_knowledge 에 extract_knowledge, 그리고 choose_action, review_knowledge, finalize_knowledge 에 find_plan 을 더함 (후보 수와 계획 id 를 읽으려고)
- 처음 표와 다른 곳 (사용자 확인, 2026-11-20): 실행 시작 기록을 더함, 작업 지시는 시작할 때 한 번, 차례가 끝나면 빈 목록 한 번 (노드 사이에는 남기지 않음)
- 시험: 계획 확정 (승인: 후보 뽑기 → 고르기 → 초안 → 확인 → 최종 정리 → 고르기 → 고르기 → 실행 전, 불허: 후보 뽑기 → 닫힘), 계획 실행 (시작 → 실패 처리 → 노드 → 확인 노드 → 노드 → 마침, 작업 지시 만들기)
- 별도 에이전트 리뷰 반영 (사용자, 2026-11-20 "2,3 만 고치고"): 실행 흐름 시험이 차례 끝의 정리 기록(실행 중 노드 없음)을 확인, 주석 두 곳을 코드에 맞춤. 변경 전에 시작해 멈춰 있던 계획 확정을 이어 가면 새 reads 가 없어 실패하는 것은 두기로 함 (시험 작업 폴더에 멈춰 있는 실행이 없음)
- 남은 것: 7 단계 (실제 화면 확인). 사용자가 서버와 함께 시험하는 것을 생각 중이라 대기 (2026-11-20)
