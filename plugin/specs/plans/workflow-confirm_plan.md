# 워크플로: B 계획 확정 (거시 계획, 초안)

2026-11-19 작성. 단계별 상세 전의 큰 그림이다. 정하지 않은 것은 "정할 것"에 모았다.
표시: `(사용자)` 정한 것, `(Claude 제안)` 확인 전.

## 요청

re_code.html "도식화 - B", "도식화 - C" 탭의 B 계획 확정(`/plan-go` 승인, `/plan-cancel` 불허)과 그 안의 C 지식 다듬어 저장을 워크플로로 만든다.

근거 문서
- B·C 흐름과 결정: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-flow-diagrams.md "## B", "## C"
- 단계별 입출력: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-flow-io.md "## B", "## C"
- 지식 추출 프롬프트 초안: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-prompt-extract-knowledge-draft.md
- 지식 다듬기 프롬프트 초안 (0~3 단계): /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-prompt-refine-knowledge-draft.md
- 계획 id 인자, 보여 준 기록: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-19-data-confirmed.md 4 절

## 정해진 흐름 (사용자, 2026-11-18 ~ 19)

```
/plan-go <계획 id>  또는  /plan-cancel <계획 id>      승인과 불허 모두 같은 순서
  0. 대상 계획 확인     id 없으면 계획 목록을 보이고 끝. 검토 중이 아니면 알리고 끝
  1. 지식 추출          보여 준 기록의 시각부터 지금까지의 대화 → 지식 후보 (plan / domain)
  2. C 지식 다듬어 저장  후보가 없으면 건너뜀
     0 기존 지식 미리 찾기 → 1 후보 고르기 → 2 합칠지 정하기 → 3 설명과 예시 구체화 → 저장
  3. 간선 확인          순환, 간선 끝, 담당 없음. 문제가 있으면 대화로 고치고 다시 확인
  4. 승인 또는 불허 기록  검토 중 → 승인 / 불허. 이유는 받지 않는다
  5. 알리기             결정, 저장한 지식 수. 승인이면 /plan-run <id> 안내, 불허면 "이 계획은 끝남"
```

## 이미 있는 것

| 필요한 것 | 있는 곳 |
|---|---|
| 계획 조회, 상태 바꾸기, 허용 검사 | `plan_api_reader/writer()`, `PlanStatus.can_move_to` |
| 보여 준 기록 (시각, 대화 기록 경로) | `PlanFolderReader.read_shown` (A 의 prepare_show 가 남김) |
| 대화 구간 읽기 | `claude_utils.transcript.read_dialogue.dialogue` |
| 지식 검색, 만들기, 덧붙이기 | `memory_api_reader/writer()` |
| 참여 페르소나 | 계획의 `persona_ids` |
| 프롬프트 초안 | 지식 추출, 지식 다듬기 1~3 단계 |

없는 것: 간선 확인 함수(`check_plan`, 초안만 있음), 대화로 고치기 스킬(A 5 단계), `/plan-go`·`/plan-cancel` 명령(플러그인 스킬).

## 흐름도                                  상태: 확답 (사용자, 2026-11-19)

```
plan_go                                              plan_cancel 도 같은 모양. 기록·알리기의 decision 만 rejected
├─ find_plan           [CODE]                        대화 기록의 마지막 /plan-go <id> 줄 → 계획(검토 중이어야), 보여 준 기록
├─ check_edges         [CODE]                        순환, 간선 끝, 담당 없음. 문제면 목록을 담아 실패로 멈춤. plan_cancel 에는 없음
├─ extract_knowledge   [CLAUDE_P]                    보여 준 시각부터의 대화 → {candidates: [{type, theme, content, quotes}]}
├─ refine_each         [FOR_EACH_ITEM: extract_knowledge.candidates]   앞 16 개까지
│  ├─ find_existing    [CODE]                        같은 종류로 기존 지식 10 개 (plan→plan, domain→knowledge)
│  ├─ choose_action    [MAIN_SESSION_ASK]            새로 저장 / 덧붙이기: 가까운 기존 지식 두 개 / 넣지 않기
│  └─ keep_each        [IN_ORDER] [run_if: confirm_plan.keeps_candidate]
│     ├─ write_knowledge    [CLAUDE_P]               본문(설명과 예시) 초안
│     ├─ review_knowledge   [MAIN_SESSION_TALK]      초안을 보이고, 고칠 말이 있으면 고쳐 다시 보이며 확인받음
│     ├─ finalize_knowledge [CLAUDE_P]               그 대화에서 마지막으로 확인한 본문과 저장 여부
│     └─ save_knowledge     [CODE]                   저장이면 만들기 / 덧붙이기. 페르소나는 계획의 페르소나 전부
├─ record_decision     [CODE]  Ref args decision     검토 중 → 승인 / 불허
└─ notify              [MAIN_SESSION_SHOW]  Ref args decision   결정, 저장한 지식 수, 승인이면 /plan-run <id>

list_plans                                           /plan-go, /plan-cancel, /plan-run 을 id 없이 불렀을 때
├─ collect_plans       [CODE]                        .plan/ 의 id → 계획마다 제목·상태
└─ show_plans          [MAIN_SESSION_SHOW]           "계획 id 를 넣어 다시 불러 주세요." + 목록
```

- keep_each 의 조건 (사용자, 2026-11-19): choose_action 이 남긴 답을 읽어 "넣지 않기"가 아니면 계속한다. 조건 함수 `confirm_plan.keeps_candidate` 하나를 등록해 묶음에 건다. 각 단계 안에서 읽고 건너뛰는 방식은 CLAUDE_P·TALK 단계가 호출과 대화를 막을 수 없어 쓰지 않는다
- 플러그인 명령: `/plan-go`, `/plan-cancel` 스킬 두 개. 인자에 id 가 없으면 list_plans, 있으면 plan_go / plan_cancel 을 시작한다 (run 스킬의 지시 처리 규칙을 따른다)

## 번들 engine 에 맞추면서 생기는 문제와 안 (정할 것)

| # | 정해진 흐름 | engine 의 제약 | 안 (Claude 제안) |
|---|---|---|---|
| 1 (정함: 가, 사용자 2026-11-19) | `/plan-go <계획 id>` | run 스킬은 흐름 이름만 CLI 에 넘기고 나머지 글은 대화 기록에 남긴다. 흐름에 인자를 넘길 길이 없다 | 가. find_plan 이 대화 기록의 마지막 슬래시 명령에서 인자를 읽는다 (read_dialogue 가 슬래시 명령과 인자를 넣어 준다). 나. 첫 단계에서 ASK 로 계획 id 를 묻는다 |
| 2 (정함: 나, 사용자 2026-11-19. id 가 없으면 `/plan-go` 스킬이 list_plans 흐름을 시작. 검토 중이 아니면 find_plan 이 실패로 멈춤) | id 가 없거나 검토 중이 아니면 "목록을 보이고 끝" | 조건으로 건너뛰는 것은 ASK 답(`answer_is`)으로만 된다. CODE 단계가 흐름을 정상으로 끝낼 수 없다 | 가. find_plan 이 실패(failed)로 멈추며 그 글에 계획 목록이나 이유를 담는다. 나. 플러그인의 `/plan-go` 스킬 글이 흐름을 시작하기 전에 id 가 있는지 본다 |
| 3 (정함: 흐름 두 개, 사용자 2026-11-19) | 승인과 불허 | 흐름 하나에 결정 값을 넘길 길이 없다 (1 과 같은 이유) | 같은 단계들을 쓰는 흐름 두 개(`plan_go`, `plan_cancel`)를 선언하고, 기록 단계만 다르게 한다 |
| 4 (정함: 후보마다 한 질문, 사용자 2026-11-19) | C1 후보 고르기는 선택 창에서 여러 개를 고른다 (질문 하나에 4 개씩, 16 개까지) | engine 의 묻기는 선택지 하나만 고른다 | 후보마다 묻는다: C1(고를지)과 C2(합칠지)를 한 질문으로 합쳐 "새로 저장 / 기존 지식 N 에 덧붙이기 / 넣지 않기" |
| 5 (정함: 가 TALK, 사용자 2026-11-19) | "이 선택이 맞습니까?" 아니요면 다시, C3 고칠 말이 있으면 고쳐서 다시 보이기 | 앞 단계로 되돌아가기가 없다. 다만 묻기의 답을 거절하면 같은 질문을 다시 낸다 | 가. C3 를 대화(TALK) 단계로 두어 고칠 말을 대화로 받고, 다음 CLAUDE_P 가 대화에서 최종 본문을 뽑는다. 나. 고치기는 받지 않고 "저장 / 넣지 않기"만 묻는다 (첫 판) |
| 6 (정함: 간선 확인을 0 단계 뒤로 옮기고 문제면 실패로 멈춤. 불허는 간선 확인을 건너뜀, 사용자 2026-11-19) | 간선에 문제가 있으면 대화로 고치고 전체를 다시 확인 | 되돌아가기 없음. 대화로 고치기 스킬이 아직 없다 | 문제가 있으면 문제 목록을 보이고 실패로 멈춘다. 사용자가 고친 뒤 `/plan-go <id>` 를 다시 부른다 (지식 추출부터 다시. C 의 "이미 저장한 지식은 넣지 않기로 거른다"와 같은 원칙) |
| 7 (정함: claude -p, 사용자 2026-11-19) | 지식 추출은 "메인 세션이 따른다" (초안) | run 스킬은 메인 세션이 지시 하나만 처리하게 한다 | 지식 추출은 CLAUDE_P 로 한다. 입력은 보여 준 시각부터 지금까지의 대화 (write_request 와 같은 방식) |

## 만드는 순서 (A 와 같은 방식: 단계마다 계획 → 만들기 → 시험 → 단계 기록)

1. 위 1~7 을 정하고 흐름도 확답
2. `/plan-go`, `/plan-cancel` 명령 (플러그인 스킬 두 개. run 스킬처럼 흐름을 시작)
3. find_plan
4. extract_knowledge (프롬프트 초안을 옮기고 실제 대화로 시험)
5. C: find_existing → choose_action → write_knowledge → confirm_knowledge → save_knowledge (프롬프트 초안 1~3 단계를 옮김)
6. check_edges (`check_plan` 초안을 함수로)
7. record_decision, notify
8. 끝까지 시험: A 로 만든 계획에 대화로 피드백을 준 뒤 `/plan-go <id>`. CLI(가짜 claude)와 Claude Code(-p 이어 부르기) 둘 다

## 이번 범위 밖

- 대화로 고치기 스킬 (A 5 단계): 6 번에서 "고친 뒤 다시 부르기"로 미룬다. 만들면 6 번을 다시 본다
- 계획 상태 바꾸기 API 를 데이터·API 문서에 넣는 일: 서버 구현은 이미 `PATCH /plans/{id}/status`(가안)로 부른다

## 진행 기록

- notify: notify_task.py, saved_knowledge_count.py, 흐름에 더함. 흐름 시험이 마지막 show → next → finished 를 거치게 고침, 시험 2개 더함. 검증 통과 (pytest 120개). B 의 단계가 모두 흐름에 들어갔다
- record_decision: record_decision_task.py(결정 값을 Ref args 로), decision_not_allowed_error.py, 흐름에 더함, 시험 3개. 검증 통과 (pytest 118개)
- write_knowledge 프롬프트 다시 씀 (사용자: 지식에는 예시 하나만 필요할 때, 프롬프트에는 본보기 셋), review 대화 목표 줄임, 빈 본문이면 첫 말을 바꾸고 저장하지 않음. pytest 115개 통과
- refine_each (C): candidates_items, keeps_candidate, candidate_kind, find_existing, choose_action(+ action_choices), keep_each 의 write_knowledge(+ quoted_context, 프롬프트), review_knowledge(+ 대화 목표), finalize_knowledge(+ 프롬프트), save_knowledge, 흐름에 더함, 시험 4개. 검증 통과 (pytest 115개). 실제 opus 로 본문 쓰기 두 번 → 예시 품질 문제 발견 (아래)
- extract_knowledge: extract_knowledge_task.py, prompt_extract_knowledge.md, 출력 모양 2 개, feedback_dialogue.py, 흐름에 더함(승인·불허), 시험 4개(+ confirm_plan 시험을 가짜 claude·보여 준 대화 파일로 고침). 평가 자료 specs/eval/extract_knowledge/. 검증 통과 (pytest 111개)
- check_edges: Plan.problems() (model), check_edges_task.py, plan_has_problems_error.py, confirm_plan_flows.py(승인에만 check_edges), 시험 6개. 검증 통과 (pytest 107개)
- find_plan: find_plan_task.py, command_plan_id.py, plan_not_confirmable_error.py, confirm_plan_flows.py(plan_go·plan_cancel, find_plan 까지), registry.py 두 줄, 시험 7개. 검증 통과 (pytest 101개). Claude Code 에서 /plan-go (id 없음 → 목록, id 1 → find_plan) 확인
- `/plan-go`, `/plan-cancel` 명령: plugin/skills/plan-go/SKILL.md, plan-cancel/SKILL.md. 인자에 id 가 있으면 `start plan_go` / `start plan_cancel`, 없으면 `start list_plans`. 지시 처리 규칙은 run 스킬의 2·3 번을 그대로 옮김 (run 스킬은 모델이 부를 수 없게 되어 있어 불러 쓰지 못함). plan_go 흐름이 아직 없어 시험은 find_plan 을 만든 뒤에 한다

## 단계 기록

### find_plan (만들기 전 계획, 2026-11-19)

**하는 일**: 사용자가 친 `/plan-go <id>` (또는 `/plan-cancel <id>`) 에서 계획 id 를 읽고, 확정할 수 있는 계획인지 확인하고, 뒤 단계가 쓸 값(계획 id, 제목, 참여 페르소나, 보여 준 기록)을 남긴다.

1. 입력
   - 지금 대화의 기록 파일: engine 의 세션 기록(`session.json` 의 대화 기록 경로. 세션 시작 훅이 남김)을 `DefaultSessionReader().load_session(context.state.session_id)` 로 읽는다
   - 그 대화에서 마지막으로 사용자가 친 `/…:plan-go <숫자>` 또는 `/…:plan-cancel <숫자>` 줄 (`read_dialogue.dialogue` 가 슬래시 명령을 `명령 인자` 한 줄로 넣어 준다)
   - 포트: `plan_api_reader().get_plan(plan_id)`, `DefaultPlanFolderReader().read_shown(plan_id)`
2. 출력
   - 단계 결과: `{"plan_id": 7, "title": str, "persona_ids": [int], "shown_at": str, "transcript": str}`. transcript 는 계획을 보여 준 대화의 기록 파일 (지식 추출이 읽는다)
   - 실패로 멈추는 경우 (메시지는 메인 세션이 그대로 보인다)

     | 경우 | 메시지 |
     |---|---|
     | 대화 기록 경로가 없음 | 대화 기록 경로가 없어 명령의 계획 id 를 읽지 못했습니다 |
     | 대화에 `/plan-go <id>` 줄이 없음 | 명령에서 계획 id 를 찾지 못했습니다. /plan-go <계획 id> 로 다시 불러 주세요 |
     | 계획 저장소에 없음 | 계획 7 이 계획 저장소에 없습니다 |
     | 검토 중이 아님 | 계획 7 은 승인 상태라 확정할 수 없습니다 (상태는 한국어로) |
     | 보여 준 기록이 없음 (이 작업 폴더에 `.plan/7/shown.json` 이 없음) | 계획 7 을 이 작업 폴더에서 보여 준 기록이 없습니다. 계획을 만든 폴더에서 불러 주세요 |
3. 생길 파일 트리
   ```
   코드
   src/task_plan_manager/workflow/confirm_plan/
   ├─ __init__.py
   ├─ confirm_plan_flows.py           plan_go, plan_cancel 선언 (단계 목록을 만드는 함수 하나로 두 선언). 지금은 find_plan 까지
   └─ find_plan/
      ├─ __init__.py
      ├─ find_plan_task.py
      ├─ command_plan_id.py           대화에서 마지막 /plan-go·/plan-cancel 줄의 id 읽기
      └─ plan_not_confirmable_error.py   위 실패 경우들
   src/task_plan_manager/workflow/registry.py   FLOWS 에 "plan_go", "plan_cancel"
   tests/workflow/test_confirm_plan.py

   실행하면
   .task_plan_manager/sessions/<세션 id>/runs/<실행 id>/find_plan_<uuid8>/result.json
   ```
4. 프롬프트: 없음
5. 코드 (만들 모양)
   ```python
   @TASKS.register_as("confirm_plan.find_plan")
   class FindPlanTask(Task):
       request_type = CodeRequest
       output_kind = OutputKind.DATA

       def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
           # 명령 줄에서 계획 id 를 읽고, 검토 중인지와 보여 준 기록을 확인해 뒤 단계가 쓸 값을 남긴다
           plan_id = command_plan_id(_current_transcript(context))
           plan = _reviewing_plan(plan_id)
           shown = _shown_record(plan_id)
           return TaskOutput(
               {
                   "plan_id": plan_id,
                   "title": plan.title,
                   "persona_ids": list(plan.persona_ids),
                   "shown_at": shown.shown_at,
                   "transcript": shown.transcript,
               }
           )


   # command_plan_id.py
   COMMAND_LINE = re.compile(r"^/\S*plan-(go|cancel)\s+(\d+)")


   def command_plan_id(transcript: Path) -> int:
       """대화에서 사용자가 마지막으로 친 /plan-go·/plan-cancel 줄의 계획 id. 없으면 PlanNotConfirmableError."""
   ```
6. 시험 (만들 것)
   - 대화 기록에 `/task_plan_manager:plan-go 1` 줄을 쓰고, 계획 1(검토 중)과 `.plan/1/shown.json` 을 만들어 두고 `start plan_go` → find_plan 결과에 plan_id 1, 제목, 보여 준 기록 → finished (지금은 find_plan 뿐)
   - 같은 대화에 `/plan-go 1` 뒤에 `/plan-go 2` 가 있으면 2
   - 실패 경우 다섯 가지마다 failed 와 메시지

### find_plan (만듦, 2026-11-19)

계획대로 만들었다. 위 "만들기 전 계획"의 1~3 과 같다.

5. 코드 전문
   - `find_plan/find_plan_task.py`
     ```python
"""find_plan: 명령 줄에서 계획 id 를 읽고, 확정할 수 있는 계획인지 확인하고, 뒤 단계가 쓸 값을 남긴다.
뒤 단계가 쓰는 값: 계획 id, 제목, 참여 페르소나, 계획을 보여 준 시각과 그 대화의 기록 파일 (지식 추출이 읽는다)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.port.session.default_session_reader import DefaultSessionReader
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.model.plan.shown_record import ShownRecord
from task_plan_manager.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.port.plan_api.plan_not_found_error import PlanNotFoundError
from task_plan_manager.workflow.confirm_plan.find_plan.command_plan_id import command_plan_id
from task_plan_manager.workflow.confirm_plan.find_plan.plan_not_confirmable_error import PlanNotConfirmableError
from task_plan_manager.workflow.list_plans.show_plans.plan_status_label import status_label


@TASKS.register_as("confirm_plan.find_plan")
class FindPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 명령 줄에서 계획 id 를 읽고, 검토 중인지와 보여 준 기록을 확인해 뒤 단계가 쓸 값을 남긴다
        plan_id = command_plan_id(_current_transcript(context))
        plan = _reviewing_plan(plan_id)
        shown = _shown_record(plan_id)
        return TaskOutput(
            {
                "plan_id": plan_id,
                "title": plan.title,
                "persona_ids": list(plan.persona_ids),
                "shown_at": shown.shown_at,
                "transcript": shown.transcript,
            }
        )


def _current_transcript(context: FlowContext) -> Path:
    """지금 대화의 기록 파일. 세션 시작 훅이 session.json 에 남긴 경로."""
    session = DefaultSessionReader().load_session(context.state.session_id)
    if session is None or not session.transcript_path:
        raise PlanNotConfirmableError("대화 기록 경로가 없어 명령의 계획 id 를 읽지 못했습니다")
    return Path(session.transcript_path)


def _reviewing_plan(plan_id: int) -> Plan:
    """계획 저장소의 계획. 없거나 검토 중이 아니면 PlanNotConfirmableError."""
    try:
        plan = plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError as missing:
        raise PlanNotConfirmableError(f"계획 {plan_id} 이 계획 저장소에 없습니다") from missing
    if plan.status is not PlanStatus.REVIEWING:
        raise PlanNotConfirmableError(f"계획 {plan_id} 은 {status_label(plan.status.value)} 상태라 확정할 수 없습니다")
    return plan


def _shown_record(plan_id: int) -> ShownRecord:
    """이 작업 폴더에 남은, 계획을 보여 준 기록. 없으면 PlanNotConfirmableError."""
    shown = DefaultPlanFolderReader().read_shown(plan_id)
    if shown is None:
        raise PlanNotConfirmableError(
            f"계획 {plan_id} 을 이 작업 폴더에서 보여 준 기록이 없습니다. 계획을 만든 폴더에서 불러 주세요"
        )
    return shown
     ```
   - `find_plan/command_plan_id.py`
     ```python
"""대화에서 사용자가 마지막으로 친 /plan-go·/plan-cancel 명령의 계획 id 를 읽는다.
run 스킬 방식으로는 흐름에 인자를 넘길 수 없어, 대화 기록에 남은 명령 줄에서 읽는다 (사용자, 2026-11-19)."""

from __future__ import annotations

import re
from pathlib import Path

from task_plan_manager.claude_utils.transcript.read_dialogue import dialogue
from task_plan_manager.workflow.confirm_plan.find_plan.plan_not_confirmable_error import PlanNotConfirmableError

# 대화 읽기 함수는 슬래시 명령을 "/task_plan_manager:plan-go 7" 처럼 "명령 인자" 한 줄로 넣어 준다
COMMAND_LINE = re.compile(r"^/\S*plan-(?:go|cancel)\s+(\d+)")


def command_plan_id(transcript: Path) -> int:
    """대화에서 사용자가 마지막으로 친 /plan-go·/plan-cancel 줄의 계획 id. 없으면 PlanNotConfirmableError."""
    user_lines = [utterance.text.strip() for utterance in dialogue(transcript) if utterance.role == "user"]
    for line in reversed(user_lines):
        matched = COMMAND_LINE.match(line)
        if matched:
            return int(matched.group(1))
    raise PlanNotConfirmableError("명령에서 계획 id 를 찾지 못했습니다. /plan-go <계획 id> 로 다시 불러 주세요")
     ```
   - `confirm_plan_flows.py` (지금은 find_plan 까지. decision 은 기록·알리기 단계를 만들 때 쓴다)
     ```python
"""plan_go, plan_cancel 워크플로 선언. 계획서: specs/plans/workflow-confirm_plan.md

두 흐름은 단계가 같고, 기록·알리기 단계의 결정 값(승인 / 불허)만 다르다 (사용자, 2026-11-19).
단계 목록을 만드는 함수 하나로 두 선언을 만든다. 한 단계씩 만들며 시험한다. 지금은 find_plan 까지 있다.
"""

from __future__ import annotations

from task_plan_manager.engine.definition.flow_definition import FlowDefinition
from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.unit.builders import group, task
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.runner.child_run.child_run import ChildRun
from task_plan_manager.workflow.confirm_plan.find_plan import find_plan_task  # noqa: F401


def confirm_plan_flow(name: str, decision: str, description: str) -> FlowDefinition:
    """plan_go(decision approved), plan_cancel(decision rejected) 의 선언."""
    return FlowDefinition(
        name=name,
        description=description,
        root=group(name, ChildRun.IN_ORDER,
            task("find_plan", PerformedBy.CODE, Ref("confirm_plan.find_plan"))),
    )  # fmt: skip


PLAN_GO_FLOW = confirm_plan_flow("plan_go", "approved", "검토 중인 계획에서 지식을 다듬어 저장하고 승인으로 확정한다")
PLAN_CANCEL_FLOW = confirm_plan_flow(
    "plan_cancel", "rejected", "검토 중인 계획에서 지식을 다듬어 저장하고 불허로 확정한다"
)
     ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 101개 통과. 새 시험 7개: 마지막 명령 줄의 id(1 뒤의 2)와 보여 준 기록, /plan-cancel 줄, 실패 다섯 가지(명령 줄 없음, 계획 없음, 승인 상태, 보여 준 기록 없음, 대화 기록 경로 없음)
7. 실제 실행 (Claude Code -p, 새 세션, 할 일 CLI 계획이 있는 작업 폴더 tpm-try2)
   - `/task_plan_manager:plan-go` (id 없음) → list_plans 가 돌고, 메인 세션이 "명령 뒤에 계획 id 를 붙여 다시 불러 주세요. 예: /plan-go 1" 과 계획 표를 보였다
   - `/task_plan_manager:plan-go 1` → plan_go 가 돌고 find_plan 결과: plan_id 1, 제목, persona_ids [1], shown_at, transcript(계획을 보여 준 다른 세션의 대화 기록). 지금은 find_plan 뿐이라 바로 끝남

### check_edges (만들기 전 계획, 2026-11-19)

**하는 일**: 확정하기 전에 계획의 노드와 간선에 문제가 없는지 본다. 문제가 있으면 목록을 담아 실패로 멈추고, 사용자가 고친 뒤 명령을 다시 부르게 한다 (사용자, 2026-11-19: 간선 확인을 0 단계 뒤로 옮김).

근거: 유즈케이스 문서 B 섹션의 `check_plan` 초안 (/Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-usecase-candidates.md:67-74, 순환·간선 끝·담당 없음), 기존 규칙 검사 /Users/dankim/orca/workspaces/productivility/persona-enhancer-pg2/plugin/client/plan/generate.py:303-363 (`validate`)

1. 입력
   - 앞 단계 결과: `context.read("find_plan")["plan_id"]` (선언의 `reads=("find_plan",)`)
   - 포트: `plan_api_reader().get_plan(plan_id)` (노드, 간선)
2. 출력
   - 문제가 없으면 단계 결과 `{"problems": []}`
   - 문제가 있으면 실패로 멈춘다. 메시지 (메인 세션이 그대로 보인다):
     ```text
     계획 7 의 노드와 간선에 문제가 있어 확정하지 않았습니다.
     - 순환: 2 버너 손질 조건 설정 → 4 단계별 레시피 작성 → 2 버너 손질 조건 설정
     - 노드 5 장보기 목록 작성: 담당 페르소나가 없습니다
     고친 뒤 같은 명령을 다시 불러 주세요.
     ```
   - 보는 것 (초안의 세 가지를 문장으로)

     | 검사 | 문제로 보는 경우 | 메시지 |
     |---|---|---|
     | 순환 | 간선을 따라가다 처음 노드로 돌아옴 | 순환: 2 제목 → 4 제목 → 2 제목 |
     | 간선 끝 | 간선의 앞이나 뒤 노드가 계획에 없음 | 간선 5: 앞 노드 9 가 계획에 없습니다 |
     | 간선 끝 | 자기 자신을 잇는 간선 | 간선 6: 노드 3 이 자기 자신을 잇습니다 |
     | 간선 끝 | 같은 두 노드를 잇는 간선이 둘 이상 | 간선 3, 7: 같은 노드를 잇습니다 (1 → 2) |
     | 담당 | 확인 노드(hitl)가 아닌데 persona_ids 가 비었음 | 노드 5 장보기 목록 작성: 담당 페르소나가 없습니다 |
3. 생길 파일 트리
   ```
   src/task_plan_manager/model/plan/plan.py        동작 problems() -> tuple[str, ...] 를 더함
   src/task_plan_manager/workflow/confirm_plan/check_edges/
   ├─ __init__.py
   ├─ check_edges_task.py
   └─ plan_has_problems_error.py
   confirm_plan_flows.py                           check_edges 를 더함
   tests/model/plan/test_plan_problems.py
   tests/workflow/test_confirm_plan.py             흐름 시험 더함
   ```
   - 검사를 model(`Plan.problems()`)에 두는 이유: 같은 검사를 대화로 고치기 스킬(고칠 때마다 검사)과 D 실행에서도 쓴다. 계획 데이터만 보는 규칙이라 model 의 동작으로 둔다 (Claude 제안)
4. 프롬프트: 없음
5. 코드 (만들 모양)
   ```python
   # model/plan/plan.py
   def problems(self) -> tuple[str, ...]:
       """확정·실행 전에 고쳐야 할 문제. 순환, 간선 끝, 담당 없음. 없으면 빈 튜플."""
       return (*self._cycle_problems(), *self._edge_end_problems(), *self._persona_problems())


   # check_edges_task.py
   @TASKS.register_as("confirm_plan.check_edges")
   class CheckEdgesTask(Task):
       def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
           # 계획의 노드와 간선을 검사하고, 문제가 있으면 목록을 담아 실패로 멈춘다
           plan_id = context.read("find_plan")["plan_id"]
           problems = plan_api_reader().get_plan(plan_id).problems()
           if problems:
               raise PlanHasProblemsError(_problem_message(plan_id, problems))
           return TaskOutput({"problems": []})
   ```
6. 시험 (만들 것)
   - model: 문제 없는 계획은 빈 튜플, 순환·없는 노드·자기 자신·같은 간선 두 번·담당 없음마다 메시지, hitl 노드는 담당이 없어도 문제 아님
   - 흐름: 문제 없는 계획은 check_edges 를 지나 finished, 순환이 있는 계획은 failed 와 메시지

### check_edges (만듦, 2026-11-19)

정함 (사용자, 2026-11-19): 불허(plan_cancel)는 간선 확인을 건너뛴다. 불허하면 계획이 끝나는데 간선부터 고치라고 멈추는 것은 맞지 않다. 검사는 model 의 `Plan.problems()` 에 둔다 (대화로 고치기, D 실행에서도 쓴다).

5. 코드 전문
   - `model/plan/plan.py` 의 `problems` (와 그 아래 함수)
     ```python
    def problems(self) -> tuple[str, ...]:
        """확정·실행 전에 고쳐야 할 문제. 순환, 간선 끝(없는 노드, 자기 자신, 같은 간선), 담당 없음. 없으면 빈 튜플."""
        return (*self._cycle_problems(), *self._edge_end_problems(), *self._persona_problems())

    def _cycle_problems(self) -> list[str]:
        """간선을 따라가다 처음 노드로 돌아오는 길마다 한 줄. 같은 노드들로 된 순환은 한 번만."""
        titles = {node.node_id: node.title for node in self.nodes}
        next_ids: dict[int, list[int]] = {node_id: [] for node_id in titles}
        for edge in self.edges:
            if edge.from_node_id in titles and edge.to_node_id in titles and edge.from_node_id != edge.to_node_id:
                next_ids[edge.from_node_id].append(edge.to_node_id)
        found: list[str] = []
        seen_cycles: set[frozenset[int]] = set()
        for start in titles:
            for cycle in _cycles_from(start, next_ids):
                if frozenset(cycle) not in seen_cycles:
                    seen_cycles.add(frozenset(cycle))
                    found.append(
                        "순환: " + " → ".join(f"{node_id} {titles[node_id]}" for node_id in [*cycle, cycle[0]])
                    )
        return found

    def _edge_end_problems(self) -> list[str]:
        """간선의 앞·뒤 노드가 없거나, 자기 자신을 잇거나, 같은 두 노드를 잇는 간선이 여럿인 경우."""
        node_ids = {node.node_id for node in self.nodes}
        found: list[str] = []
        edge_ids_by_pair: dict[tuple[int, int], list[int]] = {}
        for edge in self.edges:
            if edge.from_node_id not in node_ids:
                found.append(f"간선 {edge.edge_id}: 앞 노드 {edge.from_node_id} 가 계획에 없습니다")
            if edge.to_node_id not in node_ids:
                found.append(f"간선 {edge.edge_id}: 뒤 노드 {edge.to_node_id} 가 계획에 없습니다")
            if edge.from_node_id == edge.to_node_id:
                found.append(f"간선 {edge.edge_id}: 노드 {edge.from_node_id} 이 자기 자신을 잇습니다")
            edge_ids_by_pair.setdefault((edge.from_node_id, edge.to_node_id), []).append(edge.edge_id)
        for (from_id, to_id), edge_ids in edge_ids_by_pair.items():
            if len(edge_ids) > 1:
                joined = ", ".join(str(edge_id) for edge_id in edge_ids)
                found.append(f"간선 {joined}: 같은 노드를 잇습니다 ({from_id} → {to_id})")
        return found

    def _persona_problems(self) -> list[str]:
        """확인 노드(hitl)가 아닌데 담당 페르소나가 없는 노드."""
        return [
            f"노드 {node.node_id} {node.title}: 담당 페르소나가 없습니다"
            for node in self.nodes
            if node.kind is not NodeKind.HITL and not node.persona_ids
        ]


def _cycles_from(start: int, next_ids: dict[int, list[int]]) -> list[list[int]]:
    """start 에서 출발해 start 로 돌아오는 길들. 길은 start 부터 돌아오기 직전 노드까지."""
    cycles: list[list[int]] = []
    waiting: list[list[int]] = [[start]]
    while waiting:
        path = waiting.pop()
        for next_id in next_ids[path[-1]]:
            if next_id == start:
                cycles.append(path)
            elif next_id not in path and next_id > start:  # 더 작은 id 에서 시작하는 순환은 그 id 에서 찾는다
                waiting.append([*path, next_id])
    return cycles
     ```
   - `check_edges/check_edges_task.py`
     ```python
"""check_edges: 확정하기 전에 계획의 노드와 간선을 검사한다. 문제가 있으면 목록을 담아 실패로 멈춘다.
지식 추출 전에 둔다. 고친 뒤 다시 불러도 지식을 다시 다루지 않게 하기 위해서다 (사용자, 2026-11-19).
불허(plan_cancel)에서는 이 단계를 두지 않는다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.confirm_plan.check_edges.plan_has_problems_error import PlanHasProblemsError


@TASKS.register_as("confirm_plan.check_edges")
class CheckEdgesTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 계획의 노드와 간선을 검사하고, 문제가 있으면 목록을 담아 실패로 멈춘다
        plan_id = context.read("find_plan")["plan_id"]
        problems = plan_api_reader().get_plan(plan_id).problems()
        if problems:
            raise PlanHasProblemsError(_problem_message(plan_id, problems))
        return TaskOutput({"problems": []})


def _problem_message(plan_id: int, problems: tuple[str, ...]) -> str:
    head = f"계획 {plan_id} 의 노드와 간선에 문제가 있어 확정하지 않았습니다."
    lines = "\n".join(f"- {problem}" for problem in problems)
    return f"{head}\n{lines}\n고친 뒤 같은 명령을 다시 불러 주세요."
     ```
   - `confirm_plan_flows.py`
     ```python
"""plan_go, plan_cancel 워크플로 선언. 계획서: specs/plans/workflow-confirm_plan.md

두 흐름은 단계가 같고, 기록·알리기 단계의 결정 값(승인 / 불허)만 다르다 (사용자, 2026-11-19).
단계 목록을 만드는 함수 하나로 두 선언을 만든다. 불허는 간선 확인을 건너뛴다 (사용자, 2026-11-19).
한 단계씩 만들며 시험한다. 지금은 check_edges 까지 있다.
"""

from __future__ import annotations

from task_plan_manager.engine.definition.flow_definition import FlowDefinition
from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.unit.builders import group, task
from task_plan_manager.engine.definition.unit.unit import Unit
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.runner.child_run.child_run import ChildRun
from task_plan_manager.workflow.confirm_plan.check_edges import check_edges_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.find_plan import find_plan_task  # noqa: F401


def confirm_plan_flow(name: str, decision: str, description: str) -> FlowDefinition:
    """plan_go(decision approved), plan_cancel(decision rejected) 의 선언. 간선 확인은 승인에만 둔다."""
    return FlowDefinition(name=name, description=description, root=group(name, ChildRun.IN_ORDER, *_units(decision)))


def _units(decision: str) -> list[Unit]:
    units: list[Unit] = [task("find_plan", PerformedBy.CODE, Ref("confirm_plan.find_plan"))]
    if decision == "approved":
        units.append(task("check_edges", PerformedBy.CODE, Ref("confirm_plan.check_edges"), reads=("find_plan",)))
    return units


PLAN_GO_FLOW = confirm_plan_flow("plan_go", "approved", "검토 중인 계획에서 지식을 다듬어 저장하고 승인으로 확정한다")
PLAN_CANCEL_FLOW = confirm_plan_flow(
    "plan_cancel", "rejected", "검토 중인 계획에서 지식을 다듬어 저장하고 불허로 확정한다"
)
     ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 107개 통과. 새 시험 6개: model 4개(문제 없음, 순환 한 번만, 간선 끝 세 가지, hitl 을 뺀 담당 없음), 흐름 2개(순환이면 승인 실패와 메시지, 불허는 check_edges 없이 지나감)
7. 실제 계획(할 일 CLI, 노드 6개·간선 13개)으로 plan_go 를 CLI 로 돌림: check_edges 결과 `{"problems": []}`, finished

### extract_knowledge (만들기 전 계획, 2026-11-19)

#### 큰 그림: 지식이 어디서 나와 어디로 가나

```
A make_plan        계획을 보여 줌 (shown.json: 시각, 대화 기록)
   │ 사용자가 대화로 피드백 ("UI 설계는 셋으로 나눠", "FK 걸지 마")
B plan_go
   ├ extract_knowledge   대화 → 지식 후보 {type, theme, content, quotes}         ← 이번 일
   └ refine_each (C)     후보마다
        find_existing    기존 지식 검색 (theme + content 로, 같은 종류, 10 개)
        choose_action    새로 저장 / 가까운 기존 지식에 덧붙이기 / 넣지 않기
        write·review·finalize  본문(설명과 예시) → 사용자 확인
        save_knowledge   POST /memories 또는 /memories/{id}/append
다음 계획에서 쓰임
   ├ A split_tree        나눌지 판단마다 검색 → "# 검색 결과" (지금은 "없음". 연결은 나중)
   └ D 작업 지시 만들기   노드마다 검색 10 개 → 작업 지시의 참고 지식
```

- 추출에서 정하는 `theme`(작업 이름)과 `content` 가 C 의 검색어가 되고, 저장 뒤에는 다음 계획의 검색에 걸리는 이름이 된다. 그래서 theme 을 "이번 계획 이름"이 아니라 "다음에 같은 일을 할 때의 작업 이름"("{대상} {행위}")으로 쓰는 규칙이 중요하다
- 후보의 종류(type)와 지식 종류(kind): `plan` → `plan`, `domain` → `knowledge` (C 0 단계, 사용자 2026-11-18). 지식 종류 `attitude`(작업 전체의 판단 방식)는 추출 초안에서 뽑지 않는다 (2026-11-18 의 초안 구조. 사용자의 추출 목표 예시 문서에는 [태도] 예시가 있다 → 아래 확인할 것 1)

#### 1. 입력

| 무엇 | 방식 |
|---|---|
| 계획을 보여 준 대화의 기록 파일, 보여 준 시각 | `context.read("find_plan")` → `transcript`, `shown_at` |
| 대화 구간 | 그 파일에서 `shown_at` 부터의 사람·Claude 말 (`read_dialogue.dialogue`). 끝: 그 구간 안에 `/…:plan-go` 또는 `/…:plan-cancel` 줄이 있으면 마지막 그 줄 직전, 없으면(다른 대화에서 부른 경우) 파일 끝 |
| 계획의 노드 목록 (Claude 제안, 확인할 것 2) | `plan_api_reader().get_plan(plan_id)` 의 노드 id 와 제목. 대화에 계획 표가 빠졌어도(Claude Code 시험의 발견 3) 사용자 말이 어느 노드를 가리키는지 알 수 있게 |

입력 글 모양:
```text
# 계획
제목: 파이썬 할 일 목록 관리 CLI 도구(todo) 만들기
- 1 CLI 명령·데이터 형식 설계
- 2 패키지 골격 구성
…

# 대화
assistant: 계획 1 "…" 을 만들었습니다. 노드 6개 …
user: 테스트는 구현이랑 같이 하지 말고 따로 노드로 빼줘
assistant: …
user: 저장 파일은 홈 말고 XDG 경로 써. 우리 도구들은 다 그렇게 해
```

#### 2. 출력

```jsonc
// claude -p 출력 (ExtractKnowledgeOutput)
{
  "candidates": [
    {
      "type": "plan",                    // plan | domain
      "theme": "CLI 도구 개발",
      "content": "CLI 도구를 만들 때 테스트 작성은 구현과 나눠 별도 작업으로 둔다.",
      "quotes": ["테스트는 구현이랑 같이 하지 말고 따로 노드로 빼줘"]
    },
    ...
  ]
}
```
- 코드 정리: type 이 plan·domain 이 아니거나 theme·content 가 빈 후보는 버리고 경고. 앞 16 개만 남긴다 (사용자, 2026-11-18: 상위 16 개)
- 단계 결과: `{"candidates": [...], "warnings": [...]}`. refine_each 가 `extract_knowledge.candidates` 를 항목으로 반복한다. 빈 목록이면 C 는 0 번 돌고 지나간다 (후보가 없으면 C 를 건너뜀, 사용자 2026-11-18)
- 대화 기록 경로가 없으면 실패로 멈춘다 (write_request 와 같음)

#### 3. 프롬프트 (지식 추출 초안을 옮김. 모델 opus)

원문: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-prompt-extract-knowledge-draft.md (사용자가 정한 구조: 읽는 범위, 지식의 종류, 공통 규칙, 종류별 규칙과 예시, 목표, 출력)

| 곳 | 초안 | 바꿈 | 이유 |
|---|---|---|---|
| 하는 일 | "…`/plan-go` 또는 `/plan-cancel` 직전까지의 대화를 읽고" | 그대로 | |
| 읽는 범위 1·2 줄 | 사용자 말, 바로 앞 Claude 말 | 그대로 (입력에 그 구간이 들어 있다고 한 줄 더함) | 구간은 코드가 잘라 준다 |
| 읽는 범위 3 줄 | "대화 앞부분이 요약되어 원문이 없으면 대화 기록 원문을 읽습니다" | 뺌 | 코드가 원문에서 뽑아 넣는다 (사용자, 7 번 가) |
| 입력 | 없음 | "# 계획 (노드 목록)" 이 입력에 있다고 한 줄 더함 | 확인할 것 2 |
| 종류별 예시 2 | `"theme": "경쟁사"` | `"theme": "경쟁사 조사"` | 공통 규칙 "{대상} {행위}"에 맞춤 (확인할 것 3) |
| 출력 | "JSONL 로 답합니다. 한 줄에 후보 하나. 뽑을 것이 없으면 빈 답" | "JSON 하나로 답합니다. candidates 에 후보마다 {type, theme, content, quotes}. 뽑을 것이 없으면 candidates 를 빈 목록으로" | claude -p 구조화 출력은 JSON 하나 (사용자, 7 번 가) |
| 예시의 출력 모양 | 후보 하나씩 JSON 줄 | 그대로 (후보 하나의 모양은 같다) | |

#### 4. 시험

- 가짜 claude 로 (CLI)
  - 입력 글: 구간 자르기(보여 준 시각 이전 말 빠짐, 마지막 /plan-go 줄 이후 빠짐, 다른 대화면 파일 끝까지), 계획 노드 목록이 들어감
  - 출력 정리: 잘못된 type·빈 content 버림, 17 개면 16 개
  - 흐름: 후보 0 개면 C 없이 지나감 (C 를 만든 뒤)
- 실제 opus 로 (품질)
  - 평가 자료: 사용자가 직접 쓴 추출 목표 예시 (/Users/dankim/orca/workspaces/productivility/persona-enhancer-pg2/docs/extraction-target-examples.md) 와 초안의 예시들을 담은 피드백 대화를 대화 기록 파일 모양으로 만든다. 섞을 것: 노드 나누기(plan), 규칙(domain), 이번 계획에서만 쓰이는 말(뽑지 않음), "응·좋아"(뽑지 않음), 같은 말 두 번(하나로 묶음), 제품 이름(빼고 일반화)
  - 기대: 뽑아야 할 것과 뽑지 않아야 할 것을 미리 적고, 결과를 표로 비교. 같은 입력으로 두 번 돌려 흔들림을 본다
  - 실제 대화: 할 일 CLI 계획을 보여 준 대화(피드백 거의 없음) → 지어내지 않고 0 개에 가깝게 나오는지
- 비용: 한 번에 $0.05 안팎 (write_request 와 비슷한 길이)

#### 5. 생길 파일 트리

```
src/task_plan_manager/workflow/confirm_plan/extract_knowledge/
├─ __init__.py
├─ extract_knowledge_task.py
├─ prompt_extract_knowledge.md
├─ prompt_extract_knowledge_output.py      candidates: list[KnowledgeCandidate]
├─ knowledge_candidate.py                  type, theme, content, quotes
└─ feedback_dialogue.py                    보여 준 시각부터 명령 줄 직전까지 자르기
confirm_plan_flows.py                      extract_knowledge 를 더함 (승인·불허 모두)
tests/workflow/make_plan/… 가 아니라 tests/workflow/confirm_plan/test_extract_knowledge.py
실행하면: extract_knowledge_<uuid8>/result.json, calls/1/
```

#### 확인할 것

1. 태도(attitude): 사용자의 추출 목표 예시에는 [태도]("조사 결과가 확정되지 않았으면 섣불리 계획에 넣지 않는다")가 있다. 추출 초안은 plan·domain 두 종류만 뽑는다. 이번에도 두 종류만 둘지
2. 입력에 계획의 노드 목록(id, 제목)을 넣을지 (Claude 제안)
3. 예시 2 의 theme "경쟁사" → "경쟁사 조사"
4. 평가 자료를 위처럼 만들어 opus 로 두 번씩 돌려 볼지

### extract_knowledge (만듦, 2026-11-19)

정함 (사용자, 2026-11-19): 후보 종류는 plan·domain 두 가지 그대로 (태도는 나중에 따로). 입력에 계획의 노드 목록을 넣는다. 예시 2 의 theme 은 "경쟁사 조사". 평가 자료를 만들어 opus 로 두 번 돌린다.

1~2. 입력·출력: 위 "만들기 전 계획"과 같다. 대화 구간은 `feedback_dialogue` 가 자르고, 입력 글은 `# 계획`(제목, 노드 id·제목) + `# 대화`(역할: 말)
3. 프롬프트 전문 (`prompt_extract_knowledge.md`, opus). 초안에서 바꾼 곳: 읽는 범위 3 줄(요약이면 원문) → 입력 설명, 예시 2 theme "경쟁사" → "경쟁사 조사", 출력 JSONL → JSON 하나의 candidates
   ```markdown
## 하는 일
계획을 사용자에게 보여 준 뒤부터 `/plan-go` 또는 `/plan-cancel` 직전까지의 대화를 읽고, 사용자가 준 피드백에서 다음 계획에도 쓸 지식을 뽑습니다.
뽑은 것은 후보입니다. 저장은 사용자가 확인한 뒤에 합니다.

## 읽는 범위
- 계획을 보여 준 시각부터 지금 명령 직전까지, 사용자가 직접 입력한 말
- 그 말이 무엇을 보고 한 말인지 알기 위해, 바로 앞의 Claude 말
- 입력의 `# 대화` 에 이 구간이 들어 있습니다. `# 계획` 에는 이 계획의 노드 목록(id, 제목)이 있어, 사용자 말이 어느 노드를 가리키는지 알 수 있습니다

## 지식의 종류
1. 계획에 대한 피드백 (`plan`): 일을 어떻게 나누고, 어떤 순서로, 어디까지 할지에 대한 말
2. 도메인 정보에 대한 피드백 (`domain`): 그 일을 어떻게 해야 하는지의 방법, 규칙, 사실에 대한 말

## 공통 규칙
- 지엽적이거나 이번 계획에서만 쓸 수 있는 정보는 뽑지 않습니다. 다른 계획에서 같은 일을 할 때도 쓸 수 있는 것만 뽑습니다.
- 이번 계획에만 있는 이름(제품 이름, 서비스 이름)이 들어 있으면, 그 이름을 빼고 일반화해서 씁니다.
- 일반화해도 쓸 수 있을지 애매한 경우는, 중요도가 높다고 판단할 때만 후보로 올립니다.
- 동의만 한 말("응", "좋아"), 진행 지시("저장해"), 질문만 한 말은 뽑지 않습니다.
- 사용자 말에 있는 것만 씁니다. 사용자가 말하지 않은 이유나 방법을 지어내지 않습니다.
- `quotes` 에는 사용자 말을 글자 그대로 넣습니다. 고치거나 줄이지 않습니다.
- `content` 는 맥락이 없어도 이해되게, "어떤 일을 어떻게 한다"가 분명하게, 최대한 간단하게 씁니다.
- `theme` 은 그 지식을 꺼내 쓸 작업 이름입니다. 가능하면 "{대상} {행위}" 모양으로, 이번 계획에만 있는 이름(제품 이름, 기능 이름)은 넣지 않습니다.
- 같은 내용을 여러 번 말했으면 하나로 묶고 `quotes` 에 순서대로 넣습니다.

## 종류별 규칙과 예시

### 계획에 대한 피드백 (`plan`)
규칙: 사용자가 노드를 나누거나, 합치거나, 순서나 범위를 바꾸라고 한 말에서 뽑습니다. `content` 에는 그 일을 어떻게 나누는지를 씁니다.

예시 1. 뽑음
```
[Claude] "앱 전체 UI/UX 잡기" 노드 하나로 화면 설계를 맡겼습니다.
[사용자] 이건 와이어프레임, 디자인 테마, 공통 컴포넌트로 나눠줘
```
또는 앞의 Claude 말 없이 한 번에 말한 경우
```
[사용자] ui/ux 설계 단계는 와이어 프레임, 디자인 테마 선택, 공통 컴포넌트로 나누는 과정으로 나눠서 진행할 수 있게 해줘.
```
→
```json
{"type": "plan", "theme": "UI/UX 설계", "content": "UI/UX 설계는 와이어프레임 설계, 디자인 테마 설계, 공통 컴포넌트 설계로 나눈다.", "quotes": ["이건 와이어프레임, 디자인 테마, 공통 컴포넌트로 나눠줘"]}
```

예시 2. 애매한 경우: 이번 계획의 이름을 빼고 일반화해서 뽑음
```
[Claude] 카카오 스타일 서비스 조사 노드는 서비스 전체 페이지를 봅니다.
[사용자] 카카오 스타일 서비스 조사는 3 depth 까지의 페이지만 해
```
→
```json
{"type": "plan", "theme": "경쟁사 조사", "content": "경쟁사 서비스 조사는 메인 페이지로부터 3 depth 까지의 페이지를 조사한다.", "quotes": ["카카오 스타일 서비스 조사는 3 depth 까지의 페이지만 해"]}
```

### 도메인 정보에 대한 피드백 (`domain`)
규칙: 사용자가 일을 하는 방법, 지킬 규칙, 그 분야의 사실을 말한 것에서 뽑습니다. 이유를 말했으면 `content` 에 함께 씁니다.

예시 1. 뽑음
```
[Claude] 주문 테이블 설계 노드에서 주문 항목 테이블에 FK 를 겁니다.
[사용자] fk 걸지 마, 우리 서비스는 안 걸어
```
→
```json
{"type": "domain", "theme": "테이블 설계", "content": "기존 서비스가 FK 를 걸지 않으면 새 테이블에도 FK 를 걸지 않는다.", "quotes": ["fk 걸지 마, 우리 서비스는 안 걸어"]}
```

예시 2. 뽑음
```
[Claude] 주문 목록 조회는 주문, 주문 항목, 상품, 회원을 한 번에 조인하는 쿼리로 작성합니다.
[사용자] 조인 너무 깊게 하지 마. 3번 이하로 하고, 두 번 조회해서 풀 수 있으면 두 번 조회해도 돼
```
→
```json
{"type": "domain", "theme": "SQL 조회", "content": "조회할 때 join 은 3번 이하로 한다. 두 번 조회해서 풀 수 있으면 두 번 조회해도 된다.", "quotes": ["조인 너무 깊게 하지 마. 3번 이하로 하고, 두 번 조회해서 풀 수 있으면 두 번 조회해도 돼"]}
```

예시 3. 뽑지 않음 (이번 계획에서만 쓰임)
```
[Claude] 노드 제목은 "주문·결제 데이터 모델 변경"입니다.
[사용자] 노드 제목 좀 짧게 바꿔
```
→ 없음

## 목표
지금 대화를 읽고, 위 규칙과 예시대로 피드백마다 지식 후보를 뽑습니다.

## 출력
JSON 하나로 답합니다. `candidates` 에 후보마다 `{type, theme, content, quotes}` 를 넣습니다. 뽑을 것이 없으면 `candidates` 를 빈 목록으로 둡니다.
   ```
4. 코드 전문
   - `extract_knowledge_task.py`
     ```python
"""extract_knowledge: 계획을 보여 준 뒤의 피드백 대화에서 다음 계획에도 쓸 지식 후보를 뽑는다 (claude -p, opus).
후보의 종류는 plan(일을 나누는 방식)과 domain(그 일을 하는 방법·규칙) 두 가지다 (사용자, 2026-11-19).
결과의 candidates 를 C(refine_each)가 후보마다 반복한다. 비면 C 는 0 번 돈다."""

from __future__ import annotations

from pathlib import Path

from task_plan_manager.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.prompt_request import PromptRequest
from task_plan_manager.model.plan.plan import Plan
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader
from task_plan_manager.workflow.confirm_plan.extract_knowledge.feedback_dialogue import feedback_dialogue
from task_plan_manager.workflow.confirm_plan.extract_knowledge.knowledge_candidate import KnowledgeCandidate
from task_plan_manager.workflow.confirm_plan.extract_knowledge.prompt_extract_knowledge_output import (
    ExtractKnowledgeOutput,
)
from task_plan_manager.workflow.confirm_plan.find_plan.plan_not_confirmable_error import PlanNotConfirmableError

MAX_CANDIDATES = 16  # 후보가 많으면 앞의 16 개만 다룬다 (사용자, 2026-11-18)
CANDIDATE_TYPES = ("plan", "domain")

EXTRACT_KNOWLEDGE = PromptSpec(
    name="extract_knowledge",
    prompt_file=Path(__file__).parent / "prompt_extract_knowledge.md",
    output_type=ExtractKnowledgeOutput,
    model="opus",
)


@TASKS.register_as("confirm_plan.extract_knowledge")
class ExtractKnowledgeTask(Task):
    request_type = PromptRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> PromptRequest:
        # 계획의 노드 목록과, 계획을 보여 준 뒤의 피드백 대화를 입력 글로 넘긴다
        found = context.read("find_plan")
        plan = plan_api_reader().get_plan(found["plan_id"])
        return PromptRequest(EXTRACT_KNOWLEDGE, build_extract_input(plan, found["transcript"], found["shown_at"]))

    def build_output(self, context: FlowContext, result: ExtractKnowledgeOutput) -> TaskOutput:
        # 쓸 수 없는 후보를 버리고 앞의 16 개만 남긴다
        warnings: list[str] = []
        kept = [candidate for candidate in result.candidates if _is_usable(candidate, warnings)]
        if len(kept) > MAX_CANDIDATES:
            warnings.append(f"후보 {len(kept)} 개 가운데 앞의 {MAX_CANDIDATES} 개만 다룹니다")
        return TaskOutput(
            {"candidates": [_to_data(candidate) for candidate in kept[:MAX_CANDIDATES]], "warnings": warnings}
        )


def build_extract_input(plan: Plan, transcript: str | None, shown_at: str) -> str:
    """'# 계획' (제목, 노드 id 와 제목) 과 '# 대화' (보여 준 뒤의 '역할: 말' 줄)."""
    if not transcript:
        raise PlanNotConfirmableError("계획을 보여 준 대화의 기록 경로가 없어 지식을 뽑지 못했습니다")
    node_lines = "\n".join(f"- {node.node_id} {node.title}" for node in plan.nodes)
    talk_lines = "\n".join(
        f"{utterance.role}: {utterance.text}" for utterance in feedback_dialogue(Path(transcript), shown_at)
    )
    return f"# 계획\n제목: {plan.title}\n{node_lines}\n\n# 대화\n{talk_lines or '(대화 없음)'}"


def _is_usable(candidate: KnowledgeCandidate, warnings: list[str]) -> bool:
    if candidate.type not in CANDIDATE_TYPES:
        warnings.append(f'종류가 "{candidate.type}" 인 후보를 버림: {candidate.theme}')
        return False
    if not candidate.theme.strip() or not candidate.content.strip():
        warnings.append(f"작업 이름이나 내용이 빈 후보를 버림: {candidate.theme or candidate.content}")
        return False
    return True


def _to_data(candidate: KnowledgeCandidate) -> dict[str, object]:
    return {
        "type": candidate.type,
        "theme": candidate.theme.strip(),
        "content": candidate.content.strip(),
        "quotes": list(candidate.quotes),
    }
     ```
   - `feedback_dialogue.py`
     ```python
"""계획을 보여 준 뒤의 피드백 대화를 대화 기록에서 잘라 낸다.
시작: 보여 준 시각.
끝: 그 구간에 /plan-go·/plan-cancel 줄이 있으면 마지막 그 줄 직전, 없으면(다른 대화에서 부른 경우) 파일 끝."""

from __future__ import annotations

from pathlib import Path

from task_plan_manager.claude_utils.transcript.dto.utterance import Utterance
from task_plan_manager.claude_utils.transcript.read_dialogue import dialogue
from task_plan_manager.workflow.confirm_plan.find_plan.command_plan_id import COMMAND_LINE


def feedback_dialogue(transcript: Path, shown_at: str) -> list[Utterance]:
    """보여 준 시각부터 마지막 확정 명령 줄 직전까지의 사람·Claude 말."""
    after_shown = [utterance for utterance in dialogue(transcript) if utterance.at[:19] >= shown_at[:19]]
    command_indexes = [
        index
        for index, utterance in enumerate(after_shown)
        if utterance.role == "user" and COMMAND_LINE.match(utterance.text.strip())
    ]
    return after_shown[: command_indexes[-1]] if command_indexes else after_shown
     ```
5. 검증: ruff, import 검사 계약 4개, mypy, pytest 111개 통과. 새 시험 4개: 구간 자르기 2개(보여 준 시각부터 마지막 확정 명령 직전까지, 다른 대화면 끝까지), 입력 글(노드 목록과 보여 준 뒤 대화), 출력 정리(종류가 틀린 후보·빈 내용 버림, 17 개면 16 개). confirm_plan 흐름 시험은 가짜 claude 와 보여 준 대화 파일을 쓰게 고침
6. 품질 평가 (실제 opus)
   - 평가 자료: `specs/eval/extract_knowledge/make_feedback_transcript.py` (피드백 대화 20 줄과 기대). 입력 글 `feedback_input.txt`, 결과 `run1.json`, `run2.json`
   - 1 회 14.2 초 $0.096, 2 회 13.4 초 $0.064

     | 피드백 | 기대 | 1 회 | 2 회 |
     |---|---|---|---|
     | UI/UX 설계를 셋으로 나눠 | plan, UI/UX 설계 | ✓ | ✓ |
     | fk 걸지 마 (두 번 말함) | domain, 테이블 설계, quotes 둘로 묶음 | ✓ 묶음 | ✓ 묶음 |
     | 조인 3번 이하 | domain, SQL 조회 | ✓ | ✓ |
     | 카카오 스타일 조사 3 depth | plan, 경쟁사 조사, 이름 빼고 일반화 | ✓ "경쟁사 서비스 조사는…" | ✓ |
     | 테이블 최소 스펙 + 기존 DB 먼저 조회 | domain, 테이블 설계 | 둘로 나뉨: plan "최소 스펙부터" + domain "기존 DB 조회" | ✓ 하나 (domain) |
     | 조사 결과 전에 결론 가정 말고 비워 두고 물어봐 (태도에 가까움) | 판단 대상 | plan, "조사 후속 작업 계획" | 같음 |
     | 이건 왜 이렇게 나눴어? | 뽑지 않음 | ✓ 안 뽑음 | ✓ |
     | 노드 제목 좀 짧게 바꿔 | 뽑지 않음 | ✓ | ✓ |
     | 응 좋아 | 뽑지 않음 | ✓ | ✓ |

   - 피드백이 없는 실제 대화 (할 일 CLI 계획을 보여 준 대화, Claude 말 한 줄): 후보 0 개, 4.6 초 $0.008. 지어내지 않았다
   - 발견
     1. 한 말 안에 두 가지 규칙이 있으면 실행마다 하나로 묶기도, 둘로 나누기도 한다 (테이블 최소 스펙 + 기존 DB 조회). 종류도 plan / domain 사이에서 흔들린다
     2. 태도에 가까운 말은 plan 으로 뽑히고 theme 이 "조사 후속 작업 계획"처럼 "{대상} {행위}"에서 벗어난다

### refine_each (C) (만들기 전 계획, 2026-11-19)

**하는 일**: 지식 후보마다 기존 지식을 찾아 보이고, 사용자가 새로 저장 / 덧붙이기 / 넣지 않기를 고르고, 넣을 후보는 본문(설명과 예시)을 쓰고 대화로 확인받아 저장한다.
근거: 지식 다듬기 초안 /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-prompt-refine-knowledge-draft.md (0~3 단계), 정한 것 4·5 번과 keeps_candidate

```
refine_each            [FOR_EACH_ITEM: extract_knowledge.candidates]     후보마다 (16 개까지, 0 개면 안 돈다)
├─ find_existing       [CODE]               C0. 같은 종류로 기존 지식 10 개
├─ choose_action       [MAIN_SESSION_ASK]   C1+C2. 새로 저장 / 덧붙이기: 기존 두 개 / 넣지 않기
└─ keep_each           [IN_ORDER] [run_if: confirm_plan.keeps_candidate]  넣지 않기면 아래를 건너뜀
   ├─ write_knowledge    [CLAUDE_P]         C3. 본문 초안
   ├─ review_knowledge   [MAIN_SESSION_TALK] C3. 초안을 보이고, 고칠 말이 있으면 고쳐 다시 보이며 확인
   ├─ finalize_knowledge [CLAUDE_P]         C3. 그 대화에서 마지막으로 확인한 본문과 저장 여부
   └─ save_knowledge     [CODE]             저장 (만들기 / 덧붙이기)
```
- 반복 항목 함수 `confirm_plan.candidates`: `extract_knowledge` 결과의 `candidates` 를 그대로 돌려준다. 반복 묶음의 `reads=("extract_knowledge",)`
- 반복 안의 단계는 지금 후보를 `context.current_item()` 으로 읽고, 같은 후보의 앞 단계 결과를 `context.read("<단계>")` 로 읽는다 (항목 번호는 engine 이 맞춰 준다)

#### 1. find_existing [CODE] (C0)
- 입력: 지금 후보 `{type, theme, content, quotes}`, `context.read("find_plan")["persona_ids"]`
- 하는 일: `memory_api_reader().search(MemorySearchQuery(kind, query, persona_ids, limit=10))`
  - kind: 후보 plan → `plan`, domain → `knowledge` (C0, 사용자 2026-11-18)
  - query: `"{theme} {content}"`
- 출력: `{"existing": [{"memory_id", "kind", "theme", "body", "score"}, ...]}` (점수 높은 순, 10 개까지)
- 지금 mock 검색은 검색어와 상관없이 정해진 결과(테이블 설계 지식 둘)를 준다 (사용자, 2026-11-19)

#### 2. choose_action [MAIN_SESSION_ASK] (C1 + C2, 정한 것 4 번)
- 입력: 지금 후보, `context.read("find_existing")["existing"]`, 후보 수(`context.read("extract_knowledge")`)
- 질문 글:
  ```text
  지식 후보 2/5: [도메인] 테이블 설계
  기존 서비스가 FK 를 걸지 않으면 새 테이블에도 FK 를 걸지 않는다.
  근거: "fk 걸지 마, 우리 서비스는 안 걸어"

  ****** KNOWLEDGE SEARCHED 1 ********
  #2 테이블 설계
  배열은 별도 테이블로 둔다. FK 는 기존 서비스가 걸고 있을 때만 건다.

  ****** KNOWLEDGE SEARCHED 2 ********
  #1 테이블 설계
  최소 스펙부터, 꼭 필요한 스펙만 나열한다. …

  이 후보를 어떻게 할까요?
  ```
- 선택지 (선택 창 4 개 제한): `새 지식으로 저장`, `덧붙이기: #2 테이블 설계`, `덧붙이기: #1 테이블 설계`, `넣지 않기`. 기존 지식이 없으면 `새 지식으로 저장`, `넣지 않기` 둘
- 선택지 밖의 답은 받지 않는다 (같은 질문을 다시 낸다)
- 출력: `{"answer": "덧붙이기: #2 테이블 설계"}`
- 초안과 다른 점 (engine 의 묻기 단계가 할 수 있는 것에 맞춤. 확인할 것 1·2)
  - "(추천)" 표시를 두지 않는다: 추천은 "같은 일의 같은 판단인가"를 읽고 판단하는 일이라 코드만으로 할 수 없다
  - 선택지를 눌렀을 때 옆에 기존 지식을 보이는 기능(preview)이 engine 의 묻기 요청에 없다 → 질문 글에 검색한 기존 지식 두 개를 KNOWLEDGE SEARCHED 모양으로 넣는다 (본문은 200 자까지)
  - "이 선택이 맞습니까?"는 두지 않는다 (정한 것 4 번)

#### 3. keeps_candidate (조건 함수)
- `context.read("choose_action")["answer"] != "넣지 않기"` 면 keep_each 를 한다 (사용자, 2026-11-19)

#### 4. write_knowledge [CLAUDE_P, opus] (C3 본문 초안)
- 입력 글:
  ```text
  # 후보
  종류: domain (지식)
  작업 이름: 테이블 설계
  내용: 기존 서비스가 FK 를 걸지 않으면 새 테이블에도 FK 를 걸지 않는다.

  # 사용자 말과 바로 앞의 Claude 말
  assistant: 주문 테이블 설계 노드에서 주문 항목 테이블에 FK 를 겁니다.
  user: fk 걸지 마, 우리 서비스는 안 걸어

  # 덧붙일 기존 지식 (덧붙이기일 때만)
  #2 테이블 설계
  배열은 별도 테이블로 둔다. FK 는 기존 서비스가 걸고 있을 때만 건다.
  ```
  - "사용자 말과 바로 앞의 Claude 말": 보여 준 대화(find_plan 의 transcript)의 피드백 구간에서 quotes 의 말마다 그 사용자 말과 바로 앞 Claude 말을 찾는다 (초안의 "읽을 것")
- 프롬프트 (초안 3 단계를 옮김. 확인 묻기는 review_knowledge 로 옮기므로 뺌):
  ```markdown
  ## 목적
  맥락 없이 읽어도 쓸 수 있게, 지식 후보 하나의 본문(설명과 예시)을 씁니다.

  ## 읽을 것
  - 후보 하나 (종류, 작업 이름, 내용)
  - 사용자 말과 바로 앞의 Claude 말
  - 덧붙이기면 그 기존 지식

  ## 결과물
  - theme: 후보의 작업 이름. 덧붙이기면 기존 지식의 작업 이름을 씁니다.
  - body: md 줄글. 설명과 예시를 함께 씁니다.
    - 설명: "어떤 일을 어떻게 한다"가 분명하게, 최대한 간단하게 씁니다. 사용자가 이유를 말했으면 함께 씁니다.
    - 예시: 그 규칙을 적용한 짧은 장면 하나입니다. domain 이면 가능하면 쓰고, plan 이면 대화에 있을 때만 씁니다. 대화에 없는 예시를 만들었으면 "Claude 가 만든 예시"라고 표시합니다.
    - 덧붙이기면 이번에 더할 내용만 씁니다. 기존 본문 뒤에 붙이는 일은 코드가 합니다. 기존 본문과 겹치는 내용은 쓰지 않습니다.
  - 사용자 말에 없는 규칙이나 이유를 설명에 더하지 않습니다.
  ```
- 출력: `{"theme": str, "body": str}`

#### 5. review_knowledge [MAIN_SESSION_TALK] (C3 확인, 정한 것 5 번)
- 첫 말 (opening): 초안을 보이는 글
  ```text
  [도메인] 테이블 설계 (#2 에 덧붙이기)
  덧붙일 내용:
  FK 는 기존 서비스가 걸고 있으면 걸고, 새로 만들거나 기존에 걸려 있지 않으면 걸지 않는다.
  예 (Claude 가 만든 예시): …

  이대로 저장할까요? 고칠 곳이 있으면 말씀해 주세요.
  ```
- 대화 목표 (goal): "위 지식 본문을 사용자가 저장해도 된다고 할 때까지 다듬는다. 고칠 말이 있으면 고친 본문 전체를 다시 보이고 다시 묻는다. 사용자가 저장하지 말자고 하면 그렇게 정리한다. 사용자 말에 없는 규칙이나 이유를 더하지 않는다."
- 출력: `{from, to, transcript}` (대화 단계 공통)

#### 6. finalize_knowledge [CLAUDE_P, opus] (새 프롬프트)
- 입력 글: `# 초안` (write_knowledge 의 theme, body) + `# 대화` (review_knowledge 구간의 사람·Claude 말)
- 프롬프트:
  ```markdown
  ## 목적
  지식 초안을 사용자와 다듬은 대화를 읽고, 사용자가 마지막으로 확인한 본문과 저장할지를 정합니다.

  ## 결과물
  - save: 사용자가 저장하자고 했으면 true, 저장하지 말자고 했으면 false
  - theme: 초안의 작업 이름. 대화에서 사용자가 바꾸라고 했으면 바꾼 이름
  - body: 사용자가 마지막으로 확인한 본문을 그대로. 대화에서 고친 적이 없으면 초안 그대로
  - 대화에 없는 내용을 더하지 않습니다.
  ```
- 출력: `{"save": bool, "theme": str, "body": str}`

#### 7. save_knowledge [CODE]
- 입력: 지금 후보(quotes), choose_action 의 답, finalize_knowledge 결과, find_plan 의 plan_id·persona_ids
- 하는 일
  - save 가 false 면 저장하지 않는다
  - 답이 "새 지식으로 저장" → `memory_api_writer().create(NewMemory(kind, theme, body, persona_ids, sources))`
  - 답이 "덧붙이기: #<id> …" → `memory_api_writer().append(id, MemoryAddition(body, sources))`. 저장소가 본문 뒤에 `****** KNOWLEDGE APPENDED <n> ********` 를 달아 붙인다
  - persona_ids: 계획의 참여 페르소나 전부 (사용자, 2026-11-18). sources: quotes 마다 `{quote, plan_id}`
- 출력: `{"saved": bool, "action": "new" | "append" | "none", "memory_id": int | null}`
- 다시 수행: 만들기는 다시 하면 지식이 둘 생긴다. 중간에 멈추고 다시 부르면 지식 추출부터 다시 하고, 이미 저장한 지식은 choose_action 에서 "넣지 않기"로 거른다 (C, 사용자 2026-11-18)

#### 생길 파일 트리
```
src/task_plan_manager/workflow/confirm_plan/refine_each/
├─ __init__.py
├─ candidates_items.py              반복 항목 함수 confirm_plan.candidates
├─ keeps_candidate.py               조건 함수 confirm_plan.keeps_candidate
├─ candidate_kind.py                plan→plan, domain→knowledge, 보일 이름 [계획]/[도메인]
├─ find_existing/find_existing_task.py
├─ choose_action/choose_action_task.py, action_choices.py   선택지 만들기와 답 읽기
└─ keep_each/
   ├─ write_knowledge/write_knowledge_task.py, prompt_write_knowledge.md, prompt_write_knowledge_output.py, quoted_context.py
   ├─ review_knowledge/review_knowledge_task.py, review_goal.md
   ├─ finalize_knowledge/finalize_knowledge_task.py, prompt_finalize_knowledge.md, prompt_finalize_knowledge_output.py
   └─ save_knowledge/save_knowledge_task.py
confirm_plan_flows.py               refine_each 를 더함 (승인·불허 모두)
tests/workflow/test_confirm_plan.py, tests/workflow/confirm_plan/…
```

#### 시험
- 가짜 claude (CLI): 후보 3 개 → 1 번 새로 저장(대화 done) / 2 번 덧붙이기 / 3 번 넣지 않기 (keep_each 건너뜀) → mock 지식에 새 지식 하나, #2 에 APPENDED 머리와 근거, 3 번은 claude -p·대화 없음. finalize 가 save false 면 저장 안 함. 후보 0 개면 반복이 0 번
- 실제 (Claude Code -p 이어 부르기): 평가 피드백 대화로 만든 후보로 한두 개를 저장해 보고, 대화로 한 번 고쳐 본다

#### 확인할 것
1. choose_action 에 "(추천)" 을 두지 않는다 (코드만으로 판단 불가). 넣으려면 claude -p 를 한 번 더 부른다
2. 기존 지식 보기(preview)를 질문 글의 KNOWLEDGE SEARCHED 블록 두 개로 대신한다 (본문 200 자까지)
3. write_knowledge 의 대화 맥락은 quotes 마다 "그 사용자 말 + 바로 앞 Claude 말"만 넣는다 (초안대로)
4. finalize_knowledge 프롬프트 (새로 씀)

### refine_each (C) (만듦, 2026-11-19)

정함 (사용자, 2026-11-19): 본문의 예시는 3~4개. 조건: 1) 간단하면서 지식의 사례를 잘 나타낸다 2) 여러 기법이 섞인 예시는 지양하고, 간단하더라도 지금 쓰는 지식에 해당하는 것만 분명하게 보인다. 확인 대화에서 실제 사례를 받는다 (가 + 나 안). 실행 결과에서 사례를 붙이는 일(다 안)은 D 를 만들 때 본다.

- 만든 것은 위 "만들기 전 계획"과 같다. 바뀐 곳: write_knowledge 프롬프트의 예시 규칙(3~4개, 조건 둘, 서로 다른 상황, 적용하지 않는 경우), review_knowledge 대화 목표에 실제 사례 받기
- 반복 안 단계의 결과는 단계 폴더 하나의 result.json 에 항목 번호별로 들어가고(`by_item: {"1": …, "2": …}`), 호출 기록은 calls/1, calls/2 … 로 차례로 쌓인다
- 시험 4개: 후보 셋을 새로 저장 / 덧붙이기 / 넣지 않기로 → 새 지식(종류 plan, 페르소나 [1, 2]), #2 에 APPENDED 머리와 근거, 3 번은 본문 쓰기 없음 / 저장하지 않기로 하면 저장 없음 / 선택지 밖 답이면 같은 질문 / 후보 0 개면 반복 없음

실제 opus 로 본문 쓰기 (평가 대화의 후보 둘, 각 10 초 안팎 $0.03)
- UI/UX 설계 (새 지식): 설명 + 하위 단계 셋 설명 + 예시 3개. 예시 1 은 "대화에서 나온 장면: … 사용자가 고쳐 달라고 해서 …"로 이번 대화를 다시 이야기했다. 예시 2·3 (Claude 가 만든 예시)은 쇼핑몰 앱, 관리자 대시보드에 적용한 장면
- 테이블 설계 (#2 에 덧붙이기): "우리 서비스는 FK 를 걸지 않습니다 … 한 번 들은 뒤에는 이후 노드에서도 지킵니다 …". 예시 3개 가운데 둘은 "앞에서 'FK 걸지 마'라는 말을 이미 들었으므로 …, 사용자가 다시 말할 때까지 기다리지 않습니다"
- 발견
  1. 예시가 "이 규칙을 적용한 작업 장면"이 아니라 "이번 대화에서 있었던 일"을 다시 이야기한다 (맥락 없이 읽히지 않음)
  2. 덧붙이기 본문이 후보의 일반화된 규칙("기존 서비스가 FK 를 걸지 않으면")을 "우리 서비스는"으로 되돌렸고, "사용자가 두 번 말했다"는 대화 속 행동을 규칙처럼 적었다
  3. 기존 #2 의 "FK 는 기존 서비스가 걸고 있을 때만 건다"와 내용이 겹친다 (프롬프트는 겹치는 내용을 쓰지 말라고 했다)

### write_knowledge 프롬프트 다시 씀 (2026-11-19)

사용자 (2026-11-19): 지식 하나에 예시는 하나만 있으면 된다(일을 나누는 방식처럼 설명만으로 분명하면 없어도 된다). 대신 프롬프트에 본보기 셋을 둔다. 본보기는 사용자가 준 셋: FK(실제 SQL 예시), UI/UX 설계 나누기(예시 없음), 와이어프레임 설계 규칙(번호로 나열). 앞서 정한 "예시 3~4개"를 대신한다. 이전 판은 길고 지엽적이었다 (사용자).

- 이전 판의 문제 (실제 opus): 예시가 이번 대화를 다시 이야기함, "우리 서비스"로 좁아짐, 기존 지식과 겹침
- 함께 바꾼 것: review_knowledge 대화 목표를 두 줄로 줄임. write 가 본문을 비우면 첫 말이 "기존 지식 #N 에 이미 같은 내용이 있어 덧붙일 것이 없습니다. 저장하지 않을까요?…", 본문이 비면 저장하지 않음

프롬프트 전문 (이후)
```markdown
## 목적
지식 후보 하나를, 다른 계획에서도 바로 쓸 수 있는 지식으로 씁니다.

## 읽을 것
- 후보 (종류, 작업 이름, 내용)
- 그 근거가 된 대화
- 덧붙이기면 기존 지식

## 결과물
- theme: 이 지식을 꺼내 쓸 작업 이름. 덧붙이기면 기존 지식의 작업 이름.
- body: 무엇을 어떻게 하는지 짧게. 규칙이 여럿이면 번호를 붙여 나열한다.
  - 예시는 하나만, 규칙을 더 분명하게 할 때만 쓴다. 실제 모양(SQL, 코드, 화면 경로)으로 쓴다. 설명만으로 분명하면 쓰지 않는다.
  - 덧붙이기면 기존 지식에 없는 것만 쓴다. 더할 것이 없으면 비운다.
- 사용자 말에 없는 규칙은 더하지 않는다.

## 본보기

대화: user: fk 걸지 마, 우리 서비스는 안 걸어
```text
theme: 테이블 설계
body:
테이블 설계에서 FK 를 거는 것은 권장하지 않는다. tb1.a = tb2.a_key 처럼 키 컬럼으로 참조 관계를 둔다.

CREATE TABLE order_items (
  id       BIGINT PRIMARY KEY,
  order_id BIGINT NOT NULL   -- orders.id 를 가리키지만 FOREIGN KEY 는 걸지 않는다
);
```

대화: user: ui/ux 설계 단계는 와이어 프레임, 디자인 테마 선택, 공통 컴포넌트로 나눠서 진행할 수 있게 해줘.
```text
theme: UI/UX 설계
body:
UI/UX 설계는 한 작업으로 두지 않고 와이어프레임 설계, 디자인 테마 설계, 공통 컴포넌트 설계 세 작업으로 나눈다.
```
(일을 나누는 방식은 설명만으로 분명해서 예시가 없다)

대화: user: 와이어프레임 설계에서는 주요 페이지가 항상 1 depth 안에 파악이 가능해야 해. 주요 도메인 데이터와 주요 기능을 먼저 리스트업하고, 그 기능이나 도메인 정보를 조작하는 화면은 메인으로부터 3 depth 안에 와야 해.
```text
theme: UI/UX 설계 와이어프레임 설계
body:
와이어프레임, UI/UX 설계 때 아래를 지킨다.
1. 주요 기능과 서비스의 핵심 도메인 정보를 먼저 파악한다.
2. 주요 페이지는 메인에서 1 depth 안에서 파악할 수 있어야 한다.
3. 주요 도메인 데이터와 주요 기능을 조작하는 화면은 메인에서 3 depth 안에 둔다.
```
```

실제 opus (본보기와 겹치지 않는 후보 둘 + 기존 #2 에 덧붙이는 FK)
| 후보 | 결과 | 판단 |
|---|---|---|
| SQL 조회 (새 지식, 7.1 초 $0.029) | 설명 + 번호 규칙 둘 + 실제 SQL 예시 하나 (1차 주문·주문 항목, 2차 상품을 id 로) | 원하는 모양 |
| 경쟁사 조사 (새 지식, 6.7 초 $0.013) | 설명 두 문장, 예시 없음. "(예: 카카오 스타일)"이 남음 | 이번 계획의 이름이 남음 |
| 테이블 설계 (#2 에 덧붙이기, 7.6 초 $0.02) | "이 서비스는 FK 를 걸지 않는다 …" + SQL 예시. 비우지 않음 | 기존 #2 와 같은 뜻인데 비우지 못함, "이 서비스"로 좁아짐 |

### record_decision (만들기 전 계획, 2026-11-19)

**하는 일**: 계획 상태를 검토 중에서 승인(plan_go) 또는 불허(plan_cancel)로 바꾼다. 이유는 받지 않는다 (사용자, 2026-11-18).

1. 입력
   - 선언에서 받는 값: `Ref("confirm_plan.record_decision", {"decision": "approved"})`. plan_cancel 은 `"rejected"`. engine 은 Ref 의 args 를 Task 를 만들 때 넘긴다 (`engine/registry/registry.py:20-21`)
   - 앞 단계 결과: `context.read("find_plan")["plan_id"]` (선언의 `reads=("find_plan",)`)
   - 포트: `plan_api_reader().get_plan`, `plan_api_writer().set_plan_status`
2. 출력
   - 계획 저장소: 상태 reviewing → approved / rejected
   - 단계 결과: `{"plan_id": 7, "status": "approved"}`
   - 실패: 지금 상태에서 그 상태로 바꿀 수 없으면 (`PlanStatus.can_move_to` 가 거짓) 실패로 멈춘다. 메시지 "계획 7 은 승인 상태라 다시 확정할 수 없습니다". find_plan 이 이미 검토 중인지 봤으므로, find_plan 뒤에 다른 곳에서 상태가 바뀐 경우에만 생긴다
3. 생길 파일 트리
   ```
   src/task_plan_manager/workflow/confirm_plan/record_decision/
   ├─ __init__.py
   ├─ record_decision_task.py
   └─ decision_not_allowed_error.py
   confirm_plan_flows.py              refine_each 뒤에 record_decision (decision 을 Ref args 로)
   tests/workflow/test_confirm_plan.py
   ```
4. 프롬프트: 없음
5. 코드 (만들 모양)
   ```python
   @TASKS.register_as("confirm_plan.record_decision")
   class RecordDecisionTask(Task):
       request_type = CodeRequest
       output_kind = OutputKind.DATA

       def __init__(self, decision: str) -> None:
           self.decision = PlanStatus(decision)  # approved | rejected (선언의 Ref args)

       def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
           # 검토 중인 계획을 선언이 정한 결정(승인 / 불허)으로 바꾼다
           plan_id = context.read("find_plan")["plan_id"]
           plan = plan_api_reader().get_plan(plan_id)
           if not plan.status.can_move_to(self.decision):
               raise DecisionNotAllowedError(...)
           plan_api_writer().set_plan_status(plan_id, self.decision)
           return TaskOutput({"plan_id": plan_id, "status": self.decision.value})
   ```
6. 시험
   - plan_go 를 끝까지 (후보 0 개) → 계획 상태 approved, 결과 `{"plan_id": 1, "status": "approved"}`
   - plan_cancel → rejected
   - find_plan 뒤에 상태가 바뀐 경우를 흉내 (record_decision 만 따로 부름) → 실패와 메시지

### record_decision (만듦, 2026-11-19)

계획대로 만들었다. engine 이 Ref args 를 Task 를 만들 때 넘기는 것을 실제로 확인했다 (plan_go → approved, plan_cancel → rejected).

5. 코드 전문 (`record_decision/record_decision_task.py`)
   ```python
"""record_decision: 검토 중인 계획을 선언이 정한 결정(plan_go 는 승인, plan_cancel 은 불허)으로 바꾼다.
결정 값은 선언의 Ref args 로 받는다. 이유는 받지 않는다 (사용자, 2026-11-18)."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.code_request import CodeRequest
from task_plan_manager.model.plan.plan_status import PlanStatus
from task_plan_manager.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_plan_manager.workflow.confirm_plan.record_decision.decision_not_allowed_error import DecisionNotAllowedError
from task_plan_manager.workflow.list_plans.show_plans.plan_status_label import status_label


@TASKS.register_as("confirm_plan.record_decision")
class RecordDecisionTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def __init__(self, decision: str) -> None:
        self.decision = PlanStatus(decision)  # approved | rejected (선언의 Ref args)

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 검토 중인 계획을 선언이 정한 결정(승인 / 불허)으로 바꾼다
        plan_id = context.read("find_plan")["plan_id"]
        plan = plan_api_reader().get_plan(plan_id)
        if not plan.status.can_move_to(self.decision):
            raise DecisionNotAllowedError(
                f"계획 {plan_id} 은 {status_label(plan.status.value)} 상태라 다시 확정할 수 없습니다"
            )
        plan_api_writer().set_plan_status(plan_id, self.decision)
        return TaskOutput({"plan_id": plan_id, "status": self.decision.value})
   ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 118개 통과. 새 시험 3개: plan_go → approved 와 결과, plan_cancel → rejected, 이미 승인된 계획이면 실패와 메시지


### notify (만들기 전 계획, 2026-11-19)

**하는 일**: 확정 결과를 사용자에게 알린다. 결정, 저장한 지식 수, 승인이면 `/plan-run <id>` 안내, 불허면 "이 계획은 끝났습니다" (사용자, 2026-11-18).

1. 입력
   - 선언에서 받는 값: `Ref("confirm_plan.notify", {"decision": "approved"})` (plan_cancel 은 "rejected")
   - 앞 단계 결과
     - `context.read("find_plan")` → plan_id, title
     - `context.read("extract_knowledge")["candidates"]` → 후보 수 (항목 번호 1 … n)
     - 후보마다 `context.read("save_knowledge", "<항목 번호>")` → `{saved, action}`. 넣지 않기를 골라 keep_each 를 건너뛴 후보는 결과가 없다 (OutputMissingError) → 세지 않는다
     - 선언의 `reads=("find_plan", "extract_knowledge", "save_knowledge")`
2. 출력
   - 메인 세션에 show 지시. 보일 글:
     ```text
     승인:  계획 7 "검색 기능 설계" 을 승인했습니다. 저장한 지식 2개 (새로 1, 덧붙이기 1).
            실행은 /plan-run 7
     불허:  계획 7 "검색 기능 설계" 을 불허했습니다. 이 계획은 끝났습니다. 저장한 지식 1개 (새로 1, 덧붙이기 0).
     ```
   - 단계 결과: `{}`
   - `/plan-run` 은 아직 없는 명령(D)이지만 정한 안내 그대로 넣는다
3. 생길 파일 트리
   ```
   src/task_plan_manager/workflow/confirm_plan/notify/
   ├─ __init__.py
   ├─ notify_task.py
   └─ saved_knowledge_count.py        후보마다 save_knowledge 결과를 세기 (새로, 덧붙이기)
   confirm_plan_flows.py              record_decision 뒤에 notify
   tests/workflow/test_confirm_plan.py, tests/workflow/confirm_plan/test_refine_each.py
   ```
4. 프롬프트: 메인 세션에 넘기는 글은 위 보일 글. 보이는 방법은 run 스킬의 show 처리
5. 코드 (만들 모양)
   ```python
   @TASKS.register_as("confirm_plan.notify")
   class NotifyTask(Task):
       request_type = ShowRequest
       output_kind = OutputKind.DATA

       def __init__(self, decision: str) -> None:
           self.decision = decision

       def build_request(self, context: FlowContext) -> ShowRequest:
           # 결정, 저장한 지식 수, 다음에 할 일을 보인다
           found = context.read("find_plan")
           new_count, append_count = saved_knowledge_count(context)
           return ShowRequest(build_notice(self.decision, found["plan_id"], found["title"], new_count, append_count))
   ```
6. 시험
   - plan_go (후보 0 개) → show 글 "… 을 승인했습니다. 저장한 지식 0개 (새로 0, 덧붙이기 0).\n실행은 /plan-run 1" → next → finished
   - plan_cancel → "… 을 불허했습니다. 이 계획은 끝났습니다. …"
   - 후보 셋 (새로 저장 / 덧붙이기 / 넣지 않기) → "저장한 지식 2개 (새로 1, 덧붙이기 1)"

### notify (만듦, 2026-11-19)

계획대로 만들었다.

5. 코드 전문
   - `notify/notify_task.py`
     ```python
"""notify: 확정 결과를 알린다 (사용자, 2026-11-18).
결정, 저장한 지식 수, 승인이면 /plan-run <id> 안내, 불허면 이 계획은 끝났다고 알린다.
결정 값은 선언의 Ref args 로 받는다."""

from __future__ import annotations

from typing import Any

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_kind import OutputKind
from task_plan_manager.engine.definition.task.task import Task
from task_plan_manager.engine.definition.task.task_output import TaskOutput
from task_plan_manager.engine.registry.registries import TASKS
from task_plan_manager.engine.request.show_request import ShowRequest
from task_plan_manager.workflow.confirm_plan.notify.saved_knowledge_count import saved_knowledge_count


@TASKS.register_as("confirm_plan.notify")
class NotifyTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def __init__(self, decision: str) -> None:
        self.decision = decision  # approved | rejected (선언의 Ref args)

    def build_request(self, context: FlowContext) -> ShowRequest:
        # 결정, 저장한 지식 수, 다음에 할 일을 보인다
        found = context.read("find_plan")
        new_count, append_count = saved_knowledge_count(context)
        return ShowRequest(build_notice(self.decision, found["plan_id"], found["title"], new_count, append_count))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})


def build_notice(decision: str, plan_id: int, title: str, new_count: int, append_count: int) -> str:
    saved = f"저장한 지식 {new_count + append_count}개 (새로 {new_count}, 덧붙이기 {append_count})."
    if decision == "approved":
        return f'계획 {plan_id} "{title}" 을 승인했습니다. {saved}\n실행은 /plan-run {plan_id}'
    return f'계획 {plan_id} "{title}" 을 불허했습니다. 이 계획은 끝났습니다. {saved}'
     ```
   - `notify/saved_knowledge_count.py`
     ```python
"""후보마다의 save_knowledge 결과를 세어, 새로 저장한 수와 덧붙인 수를 돌려준다.
넣지 않기를 골라 keep_each 를 건너뛴 후보는 결과가 없으므로 세지 않는다."""

from __future__ import annotations

from task_plan_manager.engine.definition.context.flow_context import FlowContext
from task_plan_manager.engine.definition.task.output_missing_error import OutputMissingError


def saved_knowledge_count(context: FlowContext) -> tuple[int, int]:
    """(새로 저장한 수, 덧붙인 수)."""
    candidate_count = len(context.read("extract_knowledge")["candidates"])
    actions: list[str] = []
    for item_number in range(1, candidate_count + 1):
        try:
            saved = context.read("save_knowledge", str(item_number))
        except OutputMissingError:
            continue
        if saved["saved"]:
            actions.append(saved["action"])
    return actions.count("new"), actions.count("append")
     ```
   - `confirm_plan_flows.py` (B 의 단계 모두)
     ```python
"""plan_go, plan_cancel 워크플로 선언. 계획서: specs/plans/workflow-confirm_plan.md

두 흐름은 단계가 같고, 기록·알리기 단계의 결정 값(승인 / 불허)만 다르다 (사용자, 2026-11-19).
단계 목록을 만드는 함수 하나로 두 선언을 만든다. 불허는 간선 확인을 건너뛴다 (사용자, 2026-11-19).
find_plan → (승인만) check_edges → extract_knowledge → refine_each → record_decision → notify.
"""

from __future__ import annotations

from task_plan_manager.engine.definition.flow_definition import FlowDefinition
from task_plan_manager.engine.definition.ref import Ref
from task_plan_manager.engine.definition.unit.builders import group, task
from task_plan_manager.engine.definition.unit.unit import Unit
from task_plan_manager.engine.performer.performed_by import PerformedBy
from task_plan_manager.engine.runner.child_run.child_run import ChildRun
from task_plan_manager.workflow.confirm_plan.check_edges import check_edges_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.extract_knowledge import extract_knowledge_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.find_plan import find_plan_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.notify import notify_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.record_decision import record_decision_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each import candidates_items, keeps_candidate  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.choose_action import choose_action_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.find_existing import find_existing_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.finalize_knowledge import (  # noqa: F401
    finalize_knowledge_task,
)
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.review_knowledge import (  # noqa: F401
    review_knowledge_task,
)
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.save_knowledge import save_knowledge_task  # noqa: F401
from task_plan_manager.workflow.confirm_plan.refine_each.keep_each.write_knowledge import (  # noqa: F401
    write_knowledge_task,
)


def confirm_plan_flow(name: str, decision: str, description: str) -> FlowDefinition:
    """plan_go(decision approved), plan_cancel(decision rejected) 의 선언. 간선 확인은 승인에만 둔다."""
    return FlowDefinition(name=name, description=description, root=group(name, ChildRun.IN_ORDER, *_units(decision)))


def _units(decision: str) -> list[Unit]:
    units: list[Unit] = [task("find_plan", PerformedBy.CODE, Ref("confirm_plan.find_plan"))]
    if decision == "approved":
        units.append(task("check_edges", PerformedBy.CODE, Ref("confirm_plan.check_edges"), reads=("find_plan",)))
    units.append(
        task("extract_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.extract_knowledge"), reads=("find_plan",))
    )
    units.append(_refine_each())
    units.append(
        task("record_decision", PerformedBy.CODE, Ref("confirm_plan.record_decision", {"decision": decision}),
             reads=("find_plan",))
    )  # fmt: skip
    units.append(
        task("notify", PerformedBy.MAIN_SESSION_SHOW, Ref("confirm_plan.notify", {"decision": decision}),
             reads=("find_plan", "extract_knowledge", "save_knowledge"))
    )  # fmt: skip
    return units


def _refine_each() -> Unit:
    """C: 지식 후보마다 기존 지식 찾기 → 고르기 → (넣지 않기가 아니면) 본문 쓰기 → 대화로 확인 → 최종 본문 → 저장."""
    keep_each = group("keep_each", ChildRun.IN_ORDER,
        task("write_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.write_knowledge"),
             reads=("find_plan", "choose_action", "find_existing")),
        task("review_knowledge", PerformedBy.MAIN_SESSION_TALK, Ref("confirm_plan.review_knowledge"),
             reads=("write_knowledge", "choose_action")),
        task("finalize_knowledge", PerformedBy.CLAUDE_P, Ref("confirm_plan.finalize_knowledge"),
             reads=("write_knowledge", "review_knowledge")),
        task("save_knowledge", PerformedBy.CODE, Ref("confirm_plan.save_knowledge"),
             reads=("finalize_knowledge", "find_plan", "choose_action")),
        run_if=Ref("confirm_plan.keeps_candidate"), reads=("choose_action",))  # fmt: skip
    return group("refine_each", ChildRun.FOR_EACH_ITEM,
        task("find_existing", PerformedBy.CODE, Ref("confirm_plan.find_existing"), reads=("find_plan",)),
        task("choose_action", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_action"),
             reads=("find_existing", "extract_knowledge")),
        keep_each,
        for_each_item_in=Ref("confirm_plan.candidates"), reads=("extract_knowledge",))  # fmt: skip


PLAN_GO_FLOW = confirm_plan_flow("plan_go", "approved", "검토 중인 계획에서 지식을 다듬어 저장하고 승인으로 확정한다")
PLAN_CANCEL_FLOW = confirm_plan_flow(
    "plan_cancel", "rejected", "검토 중인 계획에서 지식을 다듬어 저장하고 불허로 확정한다"
)
     ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 120개 통과. 새 시험 2개: 승인 알림 글("… 을 승인했습니다. 저장한 지식 0개 (새로 0, 덧붙이기 0).\n실행은 /plan-run 1"), 불허 알림 글("… 을 불허했습니다. 이 계획은 끝났습니다. …"). refine 시험은 후보 셋에서 "저장한 지식 2개 (새로 1, 덧붙이기 1)." 을 본다. 다른 흐름 시험은 마지막 show → next → finished 를 거치게 고쳤다

