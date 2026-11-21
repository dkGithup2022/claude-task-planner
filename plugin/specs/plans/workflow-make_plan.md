# 워크플로: make_plan

번들 `tool-workflow-planner` 의 계획서 형식(extract-plan 2 절)을 따른 초안이다. 한 번에 다 만들지 않고 단계 하나씩 확답받고 만든다 (사용자, 2026-11-19).

## 진행 방식 (사용자, 2026-11-19)

interview 부터 show_plan 까지 한 단계씩 만들고 시험한다.
- 단계 하나를 만들 때마다 흐름 선언에 그 단계까지만 넣어 등록하고, 실제 CLI 로 처음부터 그 단계까지 돌려 본다. 번들 플래너는 모든 단계를 만든 뒤 한 번에 조립하는데, 이 계획은 단계마다 조립한다.
- 단계마다 아래 "단계 기록"을 남긴다. 만들기 전에는 계획을, 만든 뒤에는 실제 값과 코드 전문을 적는다.
  1. 입력: 무엇을, 어떤 방식으로 받나 (사용자 입력, 앞 단계 결과, 포트, 파일)
  2. 출력: 무엇을, 어떤 방식으로 내나 (단계 결과 파일, 포트에 쓰기, 사용자에게 보임)
  3. 생긴 파일 트리: 실행한 뒤 실제로 생긴 파일
  4. 프롬프트를 실행하는 단계면 프롬프트 전문
  5. 코드를 실행하는 단계면 코드 전문

표시: `(사용자)` 사용자가 정한 것, `(추론)` 번들의 추론 규칙이나 Claude 가 채운 것, `(보류)` 지금 정하지 않는 것.

## 요청

re_code.html "도식화 - A" 탭의 A 계획 만들기를 워크플로로 만든다. 근거 문서:
- 흐름과 단계별 참고 자료: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-flow-diagrams.md "## A"
- 단계별 입출력: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-18-flow-io.md "## A. 계획 만들기"
- 데이터와 포트: /Users/dankim/orca/workspaces/productivility/corbina/notes/2026-11-19-data-confirmed.md, 이 저장소의 specs/models.md, specs/ports.md

A 의 단계와 이 워크플로의 대응:

| A 단계 | 이 워크플로 | 비고 |
|---|---|---|
| 1. 인터뷰로 요청문 정리 | interview, write_request | 메인 세션이 대화하고, 그 안에서 grill-me(grilling 스킬)를 언급한다 (사용자) |
| 2. 페르소나 고르기 | register_plan 안 | 지엽적이라 나중에 더한다 (사용자). 첫 판은 고르는 단계 없이 등록한다 |
| 3. 노드와 간선으로 나누기 | split_plan | 실행하면서 시험해야 해서 지금은 넘어간다 (사용자) |
| 4. 계획 보여 주기 | prepare_show, show_plan | |
| 5. 대화로 고치기 | 이 워크플로 밖 | 별도 스킬이다 (사용자, 2026-11-18). 워크플로가 끝난 뒤 대화로 부른다 |

이 워크플로에 넣지 않는 것: 다시 생성, 규칙 검사, 이어 가기 (판정 전).

## 흐름도                                  상태: 확답 (사용자, 2026-11-19)

```
make_plan
├─ interview        [MAIN_SESSION_TALK]
├─ write_request    [CLAUDE_P]
├─ register_plan    [CODE]
├─ split_plan       [CODE]                (보류)
├─ prepare_show     [CODE]
└─ show_plan        [MAIN_SESSION_SHOW]
```

## 단계별 상세                             상태: 6 / 6 확답

### interview
- 종류: MAIN_SESSION_TALK
- 결과 종류: DATA
- 입력: 없음
- 출력: → { from: str, to: str, transcript: str | None }
- 상세
  - 대화 목표 (기존 계획 스킬의 "계획 정보 조사" 지시를 옮기고 grill-me 언급을 더함. 원문: /Users/dankim/orca/workspaces/productivility/persona-enhancer-pg2/plugin/skills/plan/SKILL.md:9-25):
    ```text
    먼저 Skill 도구로 `grilling` 스킬을 부르고, 그 스킬의 방식대로 사용자를 인터뷰한다. 인터뷰의 범위는 작업 계획을 세우는 데 필요한 결정이다.
    - 물을 것: 무엇을 하려는가(명령), 이미 있는 것과 지켜야 할 조건(맥락), 해야 할 일 목록, 결과를 판정할 중요한 것, 최종으로 받을 산출물, 하지 않을 일(범위 밖), 코드를 고칠 저장소 위치(있으면).
    - 묻지 않을 것: 일을 노드로 어떻게 나눌지, 세부 설계값, 구현 방법. 이것은 계획이 정한다.
    - 저장소나 문서를 보면 알 수 있는 사실은 직접 찾고 묻지 않는다.
    - 사용자가 명시적으로 말하지 않은 내용을 확답하지 않는다.
    질문이 남지 않으면 명령, 맥락, 할 일, 중요한 것, 산출물, 범위 밖, 저장소 목차로 정리해 보여 주고 확인받는다.
    ```
  - 첫 말: "어떤 일을 계획으로 만들까요?" (추론)
  - 대화가 끝나면 플러그인 run 스킬이 "정리할까요?"를 묻고 done 을 부른다 (번들 run 스킬의 talk 처리)
- 상태: 확답 (사용자, 2026-11-19)

### write_request
- 종류: CLAUDE_P
- 결과 종류: DATA (뒤 단계가 제목과 본문을 값으로 쓴다) (추론)
- 입력: ← interview.transcript, ← interview.from, ← interview.to
- 출력: → { title: str, request: str }
- 상세
  - 프롬프트 본문 (기존 계획 스킬 "2. 명령서 쓰기" 를 옮김. 원문: /Users/dankim/orca/workspaces/productivility/persona-enhancer-pg2/plugin/skills/plan/SKILL.md:27-61):
    ```text
    ## 목적
    아래 대화에서 사용자가 확인한 요청 정리를 명령서 md 로 옮깁니다.

    ## 읽을 것
    - 대화 기록 (인터뷰 시작부터 끝까지)

    ## 결과물
    - title: 명령을 한 줄로. 계획 이름으로 쓴다
    - request: 아래 목차의 md. 목차 이름은 정확히 이대로. 명령, 중요한 것, 산출물은 꼭 있어야 한다. 목차 사이에는 빈 줄 두 줄.
      # 명령 / # 맥락 / # 할 일 / # 중요한 것 / # 산출물 / # 범위 밖 / # 저장소 (없으면 뺌) / # 종류 (조사, 개발. 그 밖이면 뺌)
    - 인터뷰에서 사용자가 정한 것은 맥락에 "유저 인터뷰:"로 적는다
    - 사용자가 말하지 않은 것은 지어내지 않고 "(정하지 않음)"으로 둔다
    - 대화에서 사용자가 마지막으로 확인한 정리를 따른다
    ```
  - 출력 필드: title (str, 계획 이름), request (str, 명령서 md)
  - 입력 글 예시: 대화 기록 구간 "2026-11-19T10:00:00Z ~ 2026-11-19T10:12:00Z" 의 사용자·Claude 말
- 정함 (사용자, 2026-11-19): 모델은 opus. 대화 기록 경로가 없으면 실패로 멈춘다. 요청문 임시 파일(`.plan/drafts/`)은 없앤다. 이 단계의 결과가 그 역할을 한다
- 상태: 확답 (사용자, 2026-11-19)

### register_plan
- 종류: CODE
- 결과 종류: DATA
- 입력: ← write_request.title, ← write_request.request
- 출력: → { plan_id: int }
- 상세
  - 하는 일: 계획 저장소에 계획을 만들고(create_plan), 받은 plan_id 로 이 작업 폴더에 계획 폴더 `.plan/<plan_id>/command.md` 를 만든다
  - 쓸 model·port: `persona_api_reader().list_personas()`, `plan_api_writer().create_plan(NewPlan)`, `DefaultPlanFolderWriter().create_plan(plan_id, command_md)`
  - 참여 페르소나: 페르소나 목록의 첫 페르소나 하나 (사용자, 2026-11-19. mock 에서는 1 dankim-persona). 페르소나 고르기는 나중에 더한다
  - 페르소나가 하나도 없으면 실패로 멈춘다
- 다시 수행: 계획 등록 뒤 폴더 만들기에서 실패하고 다시 수행하면 계획이 하나 더 생긴다. 한 단계 안에서 바로 이어지는 두 줄 사이라 드물어 그대로 둔다
- 상태: 확답 (사용자, 2026-11-19)

### split_plan
- 종류: CODE (보류)
- 결과 종류: DATA
- 입력: ← register_plan.plan_id
- 출력: → { node_count: int } (보류)
- 정함 (사용자, 2026-11-19)
  - engine 에는 단계 하나(split_plan, CODE). 안에서 기능 넷을 차례로: split_tree(3-1, 한 층씩 반복, 동시 4개) → write_specs(3-2, 동시 4개) → write_edges(3-3, 1번) → save_graph(로컬 id → 서버 id 로 노드·간선 저장)
  - 프롬프트 세 개는 기존 것을 옮긴다. split 은 본문 그대로, spec 은 persona → persona_ids, work_type → kind, edges 는 필요 정보 → 선행 작업, from/to → from_id/to_id. 이대로 시험한다
  - 지식 검색 포트가 없으므로 split 입력의 검색 결과에는 "없음"이라고 적는다
  - mock 에 기본 페르소나 하나를 더한다. 계획 등록 때 그 페르소나를 참여 페르소나로 넣는다
  - 노드 id 는 로컬 id 로 간선까지 정한 뒤, 저장할 때 서버 정수 id 로 바꾼다
  - 이 단계 안의 임시 이름표는 이름에 `local_id` 를 붙인다 (사용자, 2026-11-19): 작업·노드 초안은 `local_id`, 간선 초안은 `from_local_id`, `to_local_id`. 서버가 준 정수 id(`node_id`, `from_node_id`)와 이름으로 구분한다. 모양은 트리 순서의 `n1`, `n2` … (Claude 추천, 반대 없으면 이대로)
- 상세 (아래는 2026-11-19 전의 보류 기록)
  - 보류 (사용자): 나누기(claude -p 를 n 번)는 실행하면서 시험해야 해서 지금은 넘어간다
  - 참고: 나누기는 몇 층 할지가 실행 전에 정해지지 않아 번들 반복(FOR_EACH_ITEM)으로 그릴 수 없다. 한 CODE 단계 안에서 claude_utils 로 반복 호출하는 안이 있다 (추론, 확인 전)
  - 노드 id 순서(로컬 id 로 간선을 정한 뒤 저장할 때 바꿀지)도 이때 정한다
  - 첫 판은 이 단계를 빼고 흐름을 돌려 볼 수 있다
- 상태: 확답 전

### prepare_show
- 종류: CODE
- 결과 종류: DATA
- 입력: ← register_plan.plan_id, ← split_plan.warnings, ← interview.transcript
- 출력: → { summary: str }
- 상세
  - 하는 일: 계획 상태를 작성 중에서 검토 중으로 바꾸고, 보여 준 기록(보여 준 시각과 대화 기록 경로)을 계획 폴더에 남기고, 사용자에게 보일 글(노드 표, 확인 노드, 경고)을 만든다
  - 쓸 model·port: `plan_api_reader().get_plan`, `plan_api_writer().set_plan_status`, `PlanStatus.can_move_to`, 새로 필요: `PlanFolderWriter.save_shown`, `PlanFolderReader.read_shown`, model `ShownRecord`
  - 보여 준 기록 (사용자, 2026-11-19): `shown_at`(보여 준 시각)과 `transcript`(그 대화의 기록 파일 경로). 위치 `.plan/<plan_id>/shown.json`. B 의 지식 추출이 계획 id 로 찾아 읽는다
- 다시 수행: 상태가 이미 검토 중이면 그대로 둔다. 보여 준 기록은 덮어쓴다 (마지막으로 보여 준 때가 기준)
- 상태: 확답 (사용자, 2026-11-19)

### show_plan
- 종류: MAIN_SESSION_SHOW
- 결과 종류: DATA
- 입력: ← prepare_show.summary, ← register_plan.plan_id
- 출력: 없음
- 상세
  - 보일 글:
    ```text
    {prepare_show.summary}

    고칠 곳이 있으면 대화로 말해 주세요.
    확정은 /plan-go {register_plan.plan_id}, 불허는 /plan-cancel {register_plan.plan_id}
    ```
  - 다음 명령을 id 까지 넣어 안내한다 (사용자, 2026-11-19)
- 상태: 확답 (사용자, 2026-11-19)

## 같이 쓰는 코드
- 없음 (추론)

## 확인 결과

(확답 전)

## 계획서 확답                             상태: 확답 전

## 진행 기록

- 끝까지 시험 (Claude Code, 대화 없이 -p 로 이어 부르기): 할 일 CLI 계획, 흐름 전부 통과. 발견 3개 (아래 기록)
- show_plan: show_plan_task.py, make_plan_flow.py(여섯 단계 모두), 흐름 시험이 show → next → finished 를 거치게 고침, 시험 1개. 검증 통과 (pytest 91개). make_plan 의 단계가 모두 흐름에 들어갔다
- prepare_show: prepare_show_task.py, plan_summary.py, plan_not_showable_error.py, model/plan/shown_record.py, 계획 폴더 포트에 read_shown·save_shown(+ shown_record_file_converter.py, shown_file), make_plan_flow.py(prepare_show 까지), 시험 5개. 검증 통과 (pytest 90개)
- split_plan 단계: split_plan_task.py (네 기능을 차례로 부름), make_plan_flow.py(split_plan 까지), write_specs 의 Participant 를 Persona model 로 바꾸고 participant.py 지움, 가짜 claude 를 네 종류 프롬프트에 답하게 넓힘, 시험 1개. 검증 통과 (pytest 85개)
- register_plan: register_plan_task.py, no_persona_error.py, make_plan_flow.py(register_plan 까지), 시험 2개 (+ 작업 폴더를 임시 폴더로 바꾸는 픽스처). 검증 통과 (pytest 84개)
- split_plan / save_graph: save_graph.py, saved_graph.py, plan_not_drafting_error.py, 시험 3개. 검증 통과 (pytest 69개)
- split_plan / write_edges (3-3): write_edges.py, prompt_edges.md, prompt_edges_output.py, edge_draft.py, edges_result.py, 시험 3개. 정의서 프롬프트의 needs 규칙을 고침 (사용자, 가 안). 검증 통과 (pytest 66개)
- split_plan / write_specs (3-2): write_specs.py, prompt_spec.md, prompt_spec_output.py(+ need, product), participant.py, prerequisite.py, node_draft.py, specs_result.py, prompt_caller.py(같이 씀), task_tree 에 leaves_under·path_of, 시험 2개. 검증 통과 (pytest 63개)
- split_plan / split_tree (3-1): split_tree.py, prompt_split.md, prompt_split_output.py, prompt_split_child.py, split_result.py, 같이 쓰는 task_tree/(work_item, work_kind, task_tree), request_md.py, prompt_call_log.py, 시험 3개. 아직 흐름 선언에는 넣지 않음 (register_plan 이 먼저 필요). 검증 통과 (pytest 61개)
- write_request: write_request_task.py, prompt_write_request.md, prompt_write_request_output.py, transcript_missing_error.py, make_plan_flow.py(write_request 까지), 시험 2개. 검증 통과 (pytest 58개)
- interview: interview_task.py, interview_goal.md, make_plan_flow.py(interview 까지), registry.py 한 줄, tests/workflow/test_make_plan.py. 검증 통과 (pytest 57개)

## 단계 기록

### interview (만듦, 2026-11-19)

1. 입력
   - 사용자: `/task-planner:run make_plan <맡긴 일>`. run 스킬은 흐름 이름만 CLI 에 넘기고(`task-planner start make_plan`), 맡긴 일의 글은 대화 기록에 남는다
   - 앞 단계 결과: 없음
2. 출력
   - CLI 가 메인 세션에 주는 지시 (실제 출력, goal 은 줄임):
     ```json
     {"type": "talk", "node_uuid": "76770d63-…", "item_key": "-",
      "payload": {"goal": "grill-me 방식(grilling 스킬)으로 사용자를 인터뷰해, 작업…", "opening": "어떤 일을 계획으로 만들까요?"}}
     ```
   - 메인 세션이 대화를 마치고 `task-planner done` 을 부르면 단계 결과 파일에 대화 구간과 대화 기록 경로를 쓴다 (실제 출력):
     ```json
     {"by_item": {"-": {"from": "2026-11-19T04:16:56Z", "to": "2026-11-19T04:16:56Z", "transcript": null}}}
     ```
   - 위 파일 트리의 `try1` 은 시험으로 CLI 를 직접 부를 때 `--session try1` 로 준 세션 id 다. Claude Code 에서 돌리면 그 대화의 세션 id(환경 변수 `CLAUDE_CODE_SESSION_ID`)가 들어간다
   - `transcript` 가 null 인 것은 CLI 만 따로 돌려서다. Claude Code 에서 플러그인으로 돌리면 세션 시작 훅이 대화 기록 경로를 `session.json` 에 적고, 이 값에 그 경로가 들어간다 (확인 전. Claude Code 에서 돌려 볼 때 본다)
3. 생긴 파일 트리 (작업 폴더 기준, 실제 실행)
   ```
   .task_planner/sessions/try1/
   ├─ session.json                                  {session_id, transcript_path, active_run_id, ...}
   └─ runs/r_20261119_041656/
      ├─ state.json
      ├─ history.jsonl
      └─ interview_76770d63/result.json             위 결과
   ```
   코드 쪽에 생긴 파일:
   ```
   src/task_planner/workflow/
   ├─ registry.py                                   FLOWS 에 "make_plan" 한 줄
   └─ make_plan/
      ├─ __init__.py
      ├─ make_plan_flow.py
      └─ interview/
         ├─ __init__.py
         ├─ interview_task.py
         └─ interview_goal.md                        대화 목표 글 (길어서 파일로 뺌)
   tests/workflow/test_make_plan.py
   ```
4. 프롬프트 전문: 메인 세션이 받는 프롬프트는 두 부분이다 (사용자 지적, 2026-11-19: 대화 목표도 프롬프트다)
   - 대화를 어떻게 하는지: 플러그인 run 스킬의 talk 처리 (`plugin/skills/run/SKILL.md` 2 번)
     ```text
     talk: payload.opening 으로 대화를 시작해 payload.goal 을 향해 사용자와 이야기합니다. 충분하면 AskUserQuestion 으로 "정리할까요?" (예 / 더 이야기) 를 묻고, 예면 task-planner done 을 부릅니다.
     ```
   - 무엇을 위해 대화하는지: 대화 목표 (`interview_goal.md`, 지시의 payload.goal 로 넘어감)
   ```text
먼저 Skill 도구로 `grilling` 스킬을 부르고, 그 스킬의 방식대로 사용자를 인터뷰한다. 인터뷰의 범위는 작업 계획을 세우는 데 필요한 결정이다.
- 물을 것: 무엇을 하려는가(명령), 이미 있는 것과 지켜야 할 조건(맥락), 해야 할 일 목록, 결과를 판정할 중요한 것, 최종으로 받을 산출물, 하지 않을 일(범위 밖), 코드를 고칠 저장소 위치(있으면).
- 묻지 않을 것: 일을 노드로 어떻게 나눌지, 세부 설계값, 구현 방법. 이것은 계획이 정한다.
- 저장소나 문서를 보면 알 수 있는 사실은 직접 찾고 묻지 않는다.
- 사용자가 명시적으로 말하지 않은 내용을 확답하지 않는다.
질문이 남지 않으면 명령, 맥락, 할 일, 중요한 것, 산출물, 범위 밖, 저장소 목차로 정리해 보여 주고 확인받는다.
   ```
   첫 말: "어떤 일을 계획으로 만들까요?"
5. 코드 전문
   - `src/task_planner/workflow/make_plan/interview/interview_task.py`
     ```python
"""interview: 메인 세션이 grill-me 방식으로 사용자를 인터뷰해, 계획을 세우는 데 필요한 결정을 모은다.
결과는 대화 구간과 대화 기록 경로. 다음 단계(write_request)가 이 구간의 대화로 명령서를 쓴다."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.conversation_request import ConversationRequest

# 대화 목표는 계획서(specs/plans/workflow-make_plan.md) interview 의 글 그대로. 길어서 md 파일로 둔다
GOAL = (Path(__file__).parent / "interview_goal.md").read_text(encoding="utf-8").strip()

OPENING = "어떤 일을 계획으로 만들까요?"


@TASKS.register_as("make_plan.interview")
class InterviewTask(Task):
    request_type = ConversationRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ConversationRequest:
        # 메인 세션에 대화 목표와 첫 말을 넘긴다. 대화는 run 스킬 글을 따르는 메인 세션이 한다
        return ConversationRequest(goal=GOAL, opening=OPENING)

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 수행자가 돌려준 대화 구간과 대화 기록 경로를 그대로 이 단계의 결과로 남긴다
        return TaskOutput(dict(result))
     ```
   - `src/task_planner/workflow/make_plan/make_plan_flow.py`
     ```python
"""make_plan 워크플로 선언. 계획서: specs/plans/workflow-make_plan.md

한 단계씩 만들며 시험한다. 지금은 interview 까지만 있다.
"""

from __future__ import annotations

from task_planner.engine.definition.flow_definition import FlowDefinition
from task_planner.engine.definition.ref import Ref
from task_planner.engine.definition.unit.builders import group, task
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.workflow.make_plan.interview import interview_task  # noqa: F401

MAKE_PLAN_FLOW = FlowDefinition(
    name="make_plan",
    description="사용자를 인터뷰해 명령서를 정리하고 계획을 만들어 보인다",
    root=group("make_plan", ChildRun.IN_ORDER,
        task("interview", PerformedBy.MAIN_SESSION_TALK, Ref("make_plan.interview"))),
)  # fmt: skip
     ```
   - `tests/workflow/test_make_plan.py`
     ```python
"""make_plan 을 CLI 로 돌린다. 한 단계씩 만들며 시험을 늘린다."""

import json

from task_planner.entry.cli import main
from task_planner.workflow.make_plan.interview.interview_task import GOAL, OPENING


def run(capsys, *args):
    main(["--session", "s", *args])
    return json.loads(capsys.readouterr().out)


def test_should_start_with_interview_talk_and_finish_after_done(capsys, package_home):
    talk = run(capsys, "start", "make_plan")
    assert talk["type"] == "talk"
    assert talk["payload"] == {"goal": GOAL, "opening": OPENING}

    assert run(capsys, "done")["type"] == "finished"

    result_files = list(package_home.glob("sessions/s/runs/*/interview_*/result.json"))
    assert len(result_files) == 1
    interview_result = json.loads(result_files[0].read_text(encoding="utf-8"))["by_item"]["-"]
    assert set(interview_result) == {"from", "to", "transcript"}
     ```
6. 검증: ruff 통과, import 검사 계약 4개 지킴, mypy 문제 없음, pytest 57개 통과 (새 시험 1개)
7. 첫 시험 (사용자, 2026-11-19, ~/tpm-try, 밤만쥬 1인분)
   - 흐름 시작 → 인터뷰 다섯 번 → 목차로 정리 → "정리할까요?" 예 → done → finished. `transcript` 에 대화 기록 경로가 들어옴
   - grilling 스킬을 부르지 않고 목표 글만 보고 인터뷰했다 → 목표 글 첫 줄을 "먼저 Skill 도구로 `grilling` 스킬을 부르고"로 고침 (사용자: 꼭 부르게)
   - "몰라"에 더 묻지 않고 "정하지 않음"으로 넘어갔다 (그대로 둠)

### write_request (만듦, 2026-11-19)

1. 입력
   - 앞 단계 결과 `context.read("interview")` 의 `from`, `to`, `transcript` (선언의 `reads=("interview",)`)
   - 대화 기록 파일에서 그 구간의 사람·Claude 말만 뽑는다 (`claude_utils.transcript.read_dialogue.dialogue`). 슬래시 명령의 스킬 본문, 도구 호출은 빠진다
   - claude -p 에 넘기는 입력 글은 `역할: 말` 줄. 밤만쥬 시험의 실제 입력 글은 1,794 자이고 `assistant: 어떤 일을 계획으로 만들까요? …` 로 시작한다
   - 대화 기록 경로가 없으면 `TranscriptMissingError` 로 단계가 실패하고, 메인 세션에 failed 지시가 간다
2. 출력
   - 단계 결과 파일 `write_request_<uuid8>/result.json` 에 `{"title": str, "request": str}`
   - 밤만쥬 대화로 실제 opus 를 돌린 결과 (7.5 초):
     - title: `가정집 재료와 에어프라이어로 밤만쥬 1인분 만들기`
     - request:
       ```markdown
       # 명령
       맛있는 밤만쥬를 1인분 만듭니다.


       # 맥락
       - 유저 인터뷰: 재료는 가정집에 흔히 있는 수준으로 씁니다.
       - 유저 인터뷰: 집에 없는 재료는 사 와도 됩니다. 앙금과 밤도 사 올 수 있습니다.
       - 유저 인터뷰: 쓸 수 있는 조리 도구는 에어프라이어와 버너입니다. 오븐은 없습니다.
       - 유저 인터뷰: 1인분을 만듭니다.


       # 할 일
       - 장보기 목록을 만듭니다.
       - 에어프라이어와 버너로 만드는 단계별 레시피를 씁니다. 분량, 온도, 시간을 포함합니다.


       # 중요한 것
       (정하지 않음) 사용자가 판단 기준을 정하지 않았습니다. 겉모양, 식감, 맛 같은 일반적인 기준은 계획에서 제안으로만 둡니다.


       # 산출물
       - 장보기 목록
       - 단계별 레시피(1인분 분량, 에어프라이어 온도와 시간 포함)


       # 범위 밖
       (정하지 않음) 알레르기 재료나 피할 재료도 정하지 않았습니다.
       ```
3. 생긴 파일 트리
   ```
   src/task_planner/workflow/make_plan/write_request/
   ├─ __init__.py
   ├─ write_request_task.py
   ├─ prompt_write_request.md
   ├─ prompt_write_request_output.py
   └─ transcript_missing_error.py
   실행하면 .task_planner/sessions/<세션 id>/runs/<실행 id>/write_request_<uuid8>/
   ├─ result.json
   └─ calls/1/request.json, response.json
   ```
4. 프롬프트 전문 (`prompt_write_request.md`, 모델 opus)
   ```markdown
## 목적
입력은 사용자와 Claude 가 작업 계획을 위해 나눈 인터뷰 대화입니다.
사용자가 마지막으로 확인한 정리를 명령서 md 로 옮깁니다.

## 결과물
- title: 명령을 한 줄로. 계획 이름으로 씁니다
- request: 아래 목차의 md. 목차 이름은 정확히 이대로 씁니다. 명령, 중요한 것, 산출물은 꼭 있어야 합니다. 목차 사이에는 빈 줄을 두 줄 둡니다.

  # 명령
  # 맥락
  # 할 일
  # 중요한 것
  # 산출물
  # 범위 밖
  # 저장소      (코드를 고치는 작업이 아니면 뺍니다)
  # 종류        (조사 / 개발. 그 밖이면 뺍니다)

## 규칙
- 대화에서 사용자가 마지막으로 확인한 정리를 따릅니다. 그 뒤에 고친 말이 있으면 고친 말을 따릅니다.
- 인터뷰에서 사용자가 정한 것은 맥락에 "유저 인터뷰:"로 적습니다.
- Claude 가 추천 답을 내고 사용자가 "예"처럼 받아들였으면, 그 추천 답이 사용자가 정한 것입니다.
- 사용자가 말하지 않은 것은 지어내지 않고 "(정하지 않음)"으로 둡니다. Claude 가 제안만 한 것은 사용자가 정한 것으로 옮기지 않습니다.
   ```
5. 코드 전문
   - `write_request_task.py`
     ```python
"""write_request: interview 구간의 대화를 읽어, 사용자가 확인한 정리를 제목과 명령서 md 로 옮긴다 (claude -p, opus)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.claude_utils.transcript.read_dialogue import dialogue
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.prompt_request import PromptRequest
from task_planner.workflow.make_plan.write_request.prompt_write_request_output import WriteRequestOutput
from task_planner.workflow.make_plan.write_request.transcript_missing_error import TranscriptMissingError

WRITE_REQUEST = PromptSpec(
    name="write_request",
    prompt_file=Path(__file__).parent / "prompt_write_request.md",
    output_type=WriteRequestOutput,
    model="opus",  # 사용자, 2026-11-19
)


@TASKS.register_as("make_plan.write_request")
class WriteRequestTask(Task):
    request_type = PromptRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> PromptRequest:
        # interview 구간의 대화를 "역할: 말" 줄로 이어 claude -p 의 입력 글로 넘긴다
        return PromptRequest(WRITE_REQUEST, build_write_request_input(context.read("interview")))

    def build_output(self, context: FlowContext, result: WriteRequestOutput) -> TaskOutput:
        # 제목과 명령서를 앞뒤 공백만 정리해 결과로 남긴다
        return TaskOutput({"title": result.title.strip(), "request": result.request.strip()})


def build_write_request_input(interview: dict[str, Any]) -> str:
    """대화 기록에서 interview 구간(from~to)의 사람·Claude 말만 뽑아 줄로 잇는다. 대화 기록 경로가 없으면 실패."""
    transcript = interview.get("transcript")
    if not transcript:
        raise TranscriptMissingError("interview 결과에 대화 기록 경로가 없습니다. 세션 시작 훅이 돌지 않았습니다")
    started_at, ended_at = interview["from"], interview["to"]
    utterances = [
        utterance for utterance in dialogue(Path(transcript), until=ended_at) if utterance.at[:19] >= started_at[:19]
    ]
    return "\n".join(f"{utterance.role}: {utterance.text}" for utterance in utterances)
     ```
   - `prompt_write_request_output.py`
     ```python
"""write_request 프롬프트의 출력 모양. 필드 이름이 claude -p 출력 JSON 의 키가 된다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WriteRequestOutput:
    title: str  # 명령을 한 줄로. 계획 이름
    request: str  # 명령서 md (명령, 맥락, 할 일, 중요한 것, 산출물, 범위 밖, 저장소, 종류)
     ```
6. 검증: ruff 통과, import 검사 계약 4개 지킴, mypy 문제 없음, pytest 58개 통과 (make_plan 시험 2개: 대화에서 명령서까지, 대화 기록 경로가 없을 때 실패)

### split_plan / split_tree (만듦, 2026-11-19)

흐름 선언에는 아직 넣지 않았다. split_plan 단계는 register_plan 의 plan_id 를 읽으므로 register_plan 을 만든 뒤 넣는다. 지금은 함수 단위로 시험했다.

1. 입력
   - 함수 인자: 계획 제목, 명령서 md, 호출 기록기(PromptCallLog), claude -p 호출 함수 (시험에서는 가짜)
   - 나누기 판단 하나의 입력 글: `# 명령서`(명령서 md 의 목차를 한 단계 내림) / `# 작업`(이름, 하는 일) / `# 지금까지의 작업 트리`(◀ 판단 대상 표시) / `# 쓸 수 있는 자료`(명령서의 맥락·저장소) / `# 검색 결과`("없음 (지식 검색은 아직 연결하지 않았습니다)")
   - 맨 위 작업의 하는 일: "명령서 전체. 산출물: " + 산출물 목차를 한 줄로 이은 것 (첫 실제 실행에서 여러 줄이 트리를 깨뜨려 한 줄로 바꿈)
2. 출력
   - `SplitResult(tree, warnings)`. tree 는 작업을 위치 순서로 펼친 `TaskTree`, 맨 아래 작업에 `local_id`(n1, n2 …)
   - 판단마다 `<폴더>/calls/split/<n>/request.json, response.json`
3. 생긴 파일 트리
   ```
   src/task_planner/workflow/make_plan/split_plan/
   ├─ __init__.py
   ├─ request_md.py                 명령서 md 의 목차별 글 꺼내기, 목차 내리기
   ├─ prompt_call_log.py            CODE 단계 안의 claude -p 기록
   ├─ task_tree/
   │  ├─ work_kind.py               작업 / HITL
   │  ├─ work_item.py               작업 하나 (item_key, name, scope, kind, depth, parent_key, why, local_id)
   │  └─ task_tree.py               작업 트리와 새 트리를 돌려주는 동작
   └─ split_tree/
      ├─ split_tree.py              한 층씩 반복 (동시 4개, 노드 40개, 깊이 5)
      ├─ prompt_split.md
      ├─ prompt_split_output.py     split, why, children
      ├─ prompt_split_child.py      name, kind, scope, source
      └─ split_result.py
   tests/workflow/make_plan/test_split_tree.py
   ```
4. 프롬프트 전문 (`prompt_split.md`, 모델 opus). 원문(/Users/dankim/orca/workspaces/productivility/persona-enhancer-pg2/plugin/client/plan/prompt_split.md)에서 바꾼 곳은 마지막 줄의 `from(` → `source(` 하나다. 출력 데이터 클래스의 필드 이름이 JSON 키가 되는데 `from` 은 파이썬 예약어라 필드로 쓸 수 없다
   ```markdown
## 하는 일
작업 하나를 받아, 그 분야 전문가가 이 작업을 보통 더 작은 작업으로 나눠서 진행하는지 판단합니다.
나눈다면 무엇으로 나누는지(작업 이름과 맡는 범위)까지 정합니다.
나눈 작업마다 작업 스펙을 쓰는 일은 다음 단계가 맡습니다.

## 입력
- 명령서: 이 plan 전체의 명령서. 지금 판단하는 작업이 전체 목표 중 어느 부분을 맡는지 파악하는 데 씁니다.
- 작업: 이번에 판단할 작업 스펙 (명령서, 또는 앞에서 분해된 작업)
- 지금까지의 작업 트리: 이미 만들어진 작업 전부. 이번에 판단할 작업은 "◀ 판단 대상"으로 표시됩니다.
- 쓸 수 있는 자료: 이 작업에 쓸 수 있는 자료. 명령서라면 명령서에 적히거나 첨부된 자료이고, 분해된 작업이라면 앞 작업들의 산출물입니다.
- 검색 결과: 이 작업으로 검색한 이전 plan과 지식 기록 (각각 상위 10개). 입력 맨 아래에 옵니다. 없으면 "없음"

## 무엇을 보고 판단하는가
아래 세 가지를 고려하여 적절한 깊이까지 나눕니다.
1. 별도의 작업 목표를 가질 수 있는가: 나눈 작업이 각자 따로 목표와 산출물을 가질 수 있어야 합니다. 하나의 산출물을 만드는 과정의 단계일 뿐이라면 나누지 않습니다.
2. 중요도: 최종 결과물에 중요한 부분일수록 더 세분화합니다. 덜 중요한 부분은 한 작업으로 둡니다.
3. 전문성과 복잡도: 전문성이 많이 필요하거나 복잡한 작업은 여러 단계로 나눕니다. 예를 들어 "주요 화면 흐름 설계"는 여러 단계로 나뉠 필요가 있습니다.

단, 검색 결과에 특정 작업을 더 세세하게, 혹은 덜 세세하게 작성하라는 자료나 근거가 있다면 그 지시를 참고하여 나눕니다.

## HITL
작업 과정에서 사용자의 허가나 확인이 꼭 필요한 시점에만, 그 자리에 kind 를 "HITL"로 한 작업 하나를 둡니다.
HITL 은 사용자가 여러 안 중에 고르는 자리가 아니라, 앞 작업의 결과를 사용자가 확인하고 다음으로 넘어가도 된다고 허가하는 자리입니다. 그 작업의 맡는 범위에는 사용자에게 무엇을 확인받을지 한 줄로 씁니다. HITL 은 더 나누지 않습니다.
단, HITL 이 많으면 자동화 효율이 떨어집니다. 꼭 필요한 부분에만, 그리고 작업 트리에서 맨 위 작업에 가까운 단계(얕은 단계)에서만 제한적으로 둡니다.
- 예: 메신저를 만드는 과정 중 "UI/UX 설계 확정" 단계에서는 다음 단계 이전에 HITL 이 필요할 수 있습니다.
- 예: 뉴스레터 발송 작업에서 "고객 전체 발송" 전에, 최종 원고와 발송 대상을 확인받는 HITL.
- 예: 시장 조사 작업에서 "경쟁사 비교와 방향 정리"가 끝난 뒤 제안서를 쓰기 전에, 정리한 방향을 확인받는 HITL (방향이 바뀌는 경우).

## 지킬 것
- 그 분야 전문가들이 공통으로 나누는 방식으로 나눕니다. 이번 일에만 쓰이는 지엽적인 분해는 하지 않습니다.
- 한 번에 바로 아래 단계까지만 나눕니다. 나눈 작업을 더 나눌지는 그 작업을 판단할 때 정합니다.
- 쓸 수 있는 자료에 이미 있는 것을 다시 만드는 작업은 두지 않습니다.
- 작업 트리의 다른 작업이 이미 맡은 일은 새로 만들지 않습니다. 겹치는 것이 있으면 빼고, 뺀 것을 why에 적습니다.
- 작업 이름은 "{대상} {행위}"로 씁니다.
- scope에는 그 작업의 목적을 한 줄로 씁니다. 진행 순서와 세부 조건은 담지 않습니다.

## 예시
들여쓰기 한 단계는 한 번 나눈 것을 뜻합니다. "(나누지 않음)"은 그 작업을 더 나누지 않는다는 뜻입니다.

예시 1. 브랜드 리뉴얼
- 브랜드 진단
  - 내부 인식 조사 (나누지 않음)
  - 경쟁 브랜드 분석 (나누지 않음)
- 브랜드 전략 수립 (나누지 않음)
- 비주얼 아이덴티티 디자인
  - 로고 디자인 (나누지 않음)
  - 브랜드 가이드라인 작성 (나누지 않음)
판단: 진단 결과가 이후 결정의 근거가 되므로 중요도가 높고, 내부 조사와 외부 분석은 목표와 방법이 달라 나눕니다. 전략 수립은 중요하지만 결론 하나(포지셔닝)를 내는 일이라 나누지 않습니다. 비주얼 아이덴티티는 로고 디자인과 사용 규칙 정리의 전문성이 달라 나눕니다.

예시 2. 결제 기능 추가 (저장소: shop-api)
- 현재 프로젝트 구조·규칙 조사
  - 필요한 범위의 소프트웨어 아키텍처 파악 (소스, DB 등) (나누지 않음)
  - 결제 관련 기존 로직 파악 (나누지 않음)
- 결제 흐름 설계 (나누지 않음)
- 주문·결제 데이터 모델 변경 (나누지 않음)
- PG 연동 구현 (나누지 않음)
판단: 기존 코드에 기능을 더하는 일이라 현재 프로젝트의 구조와 규칙을 먼저 조사합니다. 아키텍처 파악과 결제 관련 기존 로직 파악은 보는 범위와 목적이 달라 나눕니다. 조사, 흐름 설계, 데이터 변경, 외부 연동은 목표와 확인 방법이 다릅니다. PG 연동 구현은 복잡하지만 결제 요청·승인·취소를 한 번의 코드 변경으로 함께 확인하므로 더 나누지 않습니다.

예시 3. 신규 매장 오픈 준비
- 상권 분석 (나누지 않음)
- 매장 공간 설계
  - 공간 배치 설계 (나누지 않음)
  - 시공 업체 선정 (나누지 않음)
- 오픈 마케팅 기획 (나누지 않음)
- 운영 인력 계획 수립 (나누지 않음)
판단: 공간 설계는 비용이 가장 크고 되돌리기 어려워 중요도가 높고, 배치 설계와 업체 선정은 전문성이 달라 나눕니다. 나머지는 각자 목표가 하나라 나누지 않습니다.

예시 4. 직원 만족도 설문 분석
- 응답 데이터 정리 (나누지 않음)
- 항목별 결과 분석 (나누지 않음)
- 개선 과제 도출 (나누지 않음)
판단: 정리, 분석, 과제 도출은 산출물이 다릅니다. 항목별 결과 분석을 "보상 항목 분석, 문화 항목 분석…"으로 나누면 같은 방법을 항목마다 되풀이할 뿐이라 나누지 않습니다.

## 주의 사항
- 사용자 반응 조사, 설문 조사처럼 실제 컴퓨터로 할 수 있는 범위를 벗어나는 작업은 만들지 않습니다.

## 답
JSON 하나로 답합니다. split, why(한 문장. 세 가지 중 무엇을 보고 판단했는지, 겹쳐서 뺀 것이 있으면 함께 적음), children(name, kind("작업" 또는 "HITL"), scope(목적 한 줄. HITL 이면 확인받을 것), source("일반적인 분해" 또는 "검색 결과: <어느 기록>")).
   ```
5. 코드 전문
   - `split_tree/split_tree.py`
     ```python
"""3-1 나눌지 판단. 작업 트리를 한 층씩 넓힌다. 한 층 안의 작업은 동시에 판단한다.
멈추는 때: 더 나눌 작업이 없을 때, 노드 상한이나 깊이 상한에 닿았을 때. 규칙은 기존 generate.py 의 split_all 과 같다."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from task_planner.claude_utils.prompt.call_prompt import call_prompt
from task_planner.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.request_md import demoted, section
from task_planner.workflow.make_plan.split_plan.split_tree.prompt_split_output import SplitOutput
from task_planner.workflow.make_plan.split_plan.split_tree.split_result import SplitResult
from task_planner.workflow.make_plan.split_plan.task_tree.task_tree import TaskTree
from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem
from task_planner.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind

MAX_NODES = 40  # 맨 아래 작업(= 노드) 상한 (기존과 같음)
MAX_DEPTH = 5  # 이 깊이에 닿은 작업은 더 판단하지 않는다
PARALLEL = 4  # 한 층 안에서 동시에 부르는 claude -p 수

SPLIT = PromptSpec(
    name="split",
    prompt_file=Path(__file__).parent / "prompt_split.md",
    output_type=SplitOutput,
    model="opus",
)

PromptCaller = Callable[[PromptSpec, str], tuple[Any, PromptCallRecord]]


def split_tree(title: str, request_md: str, call_log: PromptCallLog, caller: PromptCaller = call_prompt) -> SplitResult:
    """명령서 전체에서 시작해 나눌 작업이 없어질 때까지 한 층씩 판단하고, 맨 아래 작업에 local_id 를 붙인다."""
    tree = TaskTree.start(title, "명령서 전체. 산출물: " + _one_line(section(request_md, "산출물")))
    warnings: list[str] = []
    frontier = tree.items
    while frontier:
        if len(tree.leaves()) >= MAX_NODES:
            warnings.append(f"노드 상한 {MAX_NODES}개에 닿아 작업 {len(frontier)}개를 더 나누지 않음")
            break
        judgments = _judge_layer(tree, frontier, request_md, call_log, caller)
        tree, frontier = _apply_layer(tree, frontier, judgments, warnings)
    return SplitResult(tree=tree.with_local_ids(), warnings=tuple(warnings))


def _judge_layer(
    tree: TaskTree, frontier: tuple[WorkItem, ...], request_md: str, call_log: PromptCallLog, caller: PromptCaller
) -> list[SplitOutput]:
    """한 층의 작업마다 나눌지 판단한다. 결과는 frontier 순서 그대로."""

    def judge(work_item: WorkItem) -> SplitOutput:
        output, record = caller(SPLIT, build_split_input(tree, work_item, request_md))
        call_log.save("split", record)
        return output  # type: ignore[no-any-return]

    with ThreadPoolExecutor(PARALLEL) as pool:
        return list(pool.map(judge, frontier))


def _apply_layer(
    tree: TaskTree, frontier: tuple[WorkItem, ...], judgments: list[SplitOutput], warnings: list[str]
) -> tuple[TaskTree, tuple[WorkItem, ...]]:
    """판단 결과를 판단한 순서대로 트리에 넣고, 다음 층에서 판단할 작업을 돌려준다."""
    next_frontier: list[WorkItem] = []
    for work_item, judgment in zip(frontier, judgments, strict=True):
        tree = tree.with_why(work_item.item_key, judgment.why)
        children = _children_to_add(tree, work_item, judgment, warnings)
        if not children:
            continue
        tree = tree.with_children(work_item.item_key, children)
        next_frontier += [child for child in children if _should_judge(child, warnings)]
    return tree, tuple(next_frontier)


def _children_to_add(
    tree: TaskTree, work_item: WorkItem, judgment: SplitOutput, warnings: list[str]
) -> tuple[WorkItem, ...]:
    """나누기로 했고, 자식이 2개 이상이고, 노드 상한을 넘지 않을 때만 자식 작업을 만든다."""
    named = [child for child in judgment.children if child.name.strip()]
    if not judgment.split or len(named) < 2:
        return ()
    leaf_count_after = len(tree.leaves()) + len(named) - 1
    if leaf_count_after > MAX_NODES:
        warnings.append(
            f"{work_item.name}: 나누면 노드가 {leaf_count_after}개가 되어 상한 {MAX_NODES}개를 넘으므로 나누지 않음"
        )
        return ()
    return tuple(
        WorkItem(
            item_key=f"{work_item.item_key}.{order}",
            name=child.name.strip(),
            scope=child.scope.strip(),
            kind=WorkKind.HITL if child.kind == WorkKind.HITL else WorkKind.TASK,
            depth=work_item.depth + 1,
            parent_key=work_item.item_key,
        )
        for order, child in enumerate(named, start=1)
    )


def _should_judge(child: WorkItem, warnings: list[str]) -> bool:
    """HITL 은 더 나누지 않는다. 깊이 상한에 닿은 작업도 더 판단하지 않는다."""
    if child.kind is WorkKind.HITL:
        return False
    if child.depth >= MAX_DEPTH:
        warnings.append(f"{child.name}: 깊이 상한 {MAX_DEPTH}에 닿아 더 판단하지 않음")
        return False
    return True


def build_split_input(tree: TaskTree, work_item: WorkItem, request_md: str) -> str:
    """나누기 판단 하나의 입력: 명령서, 판단할 작업, 지금까지의 작업 트리, 쓸 수 있는 자료, 검색 결과."""
    materials = "\n".join(text for text in (section(request_md, "맥락"), section(request_md, "저장소")) if text)
    return "\n\n".join(
        [
            "# 명령서\n사용자가 맡긴 원래 일입니다.\n\n" + demoted(request_md),
            f"# 작업\n- 이름: {work_item.name}\n- 하는 일: {work_item.scope}",
            "# 지금까지의 작업 트리\n" + tree.render(marked_key=work_item.item_key).rstrip(),
            "# 쓸 수 있는 자료\n" + (materials or "(없음)"),
            "# 검색 결과\n없음 (지식 검색은 아직 연결하지 않았습니다)",
        ]
    )


def _one_line(text: str) -> str:
    """여러 줄 목록을 한 줄로. 작업 트리의 한 줄에 들어가야 하므로 "- 장보기 목록\n- 레시피" → "장보기 목록, 레시피"."""
    return ", ".join(line.strip().removeprefix("- ").strip() for line in text.splitlines() if line.strip())
     ```
   - `task_tree/task_tree.py`
     ```python
"""작업 트리. 작업을 위치(item_key) 순서로 펼쳐 담고, 새 트리를 돌려주는 동작만 둔다."""

from __future__ import annotations

from dataclasses import dataclass, replace

from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem
from task_planner.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind

ROOT_KEY = "0"


@dataclass(frozen=True, slots=True)
class TaskTree:
    items: tuple[WorkItem, ...]  # 맨 위부터, 부모 다음에 그 자식들이 오는 순서

    @classmethod
    def start(cls, title: str, scope: str) -> TaskTree:
        """명령서 전체를 맨 위 작업 하나로 둔 트리."""
        return cls((WorkItem(item_key=ROOT_KEY, name=title, scope=scope, kind=WorkKind.TASK, depth=0),))

    def item(self, item_key: str) -> WorkItem:
        for work_item in self.items:
            if work_item.item_key == item_key:
                return work_item
        raise KeyError(f"작업 트리에 {item_key} 가 없습니다")

    def children(self, item_key: str) -> tuple[WorkItem, ...]:
        return tuple(work_item for work_item in self.items if work_item.parent_key == item_key)

    def leaves(self) -> tuple[WorkItem, ...]:
        """자식이 없는 작업. 이것들이 계획의 노드가 된다."""
        parent_keys = {work_item.parent_key for work_item in self.items}
        return tuple(work_item for work_item in self.items if work_item.item_key not in parent_keys)

    def with_why(self, item_key: str, why: str) -> TaskTree:
        """그 작업의 판단 근거를 적은 새 트리."""
        return TaskTree(tuple(replace(item, why=why) if item.item_key == item_key else item for item in self.items))

    def with_children(self, parent_key: str, children: tuple[WorkItem, ...]) -> TaskTree:
        """부모 바로 뒤(부모의 기존 자손 뒤)에 자식들을 넣은 새 트리."""
        insert_at = max(index for index, item in enumerate(self.items) if _is_within(item.item_key, parent_key)) + 1
        return TaskTree(self.items[:insert_at] + children + self.items[insert_at:])

    def with_local_ids(self) -> TaskTree:
        """맨 아래 작업에 트리 순서대로 n1, n2 … 를 붙인 새 트리."""
        leaf_keys = [leaf.item_key for leaf in self.leaves()]
        local_ids = {item_key: f"n{order}" for order, item_key in enumerate(leaf_keys, start=1)}
        return TaskTree(tuple(replace(item, local_id=local_ids.get(item.item_key)) for item in self.items))

    def render(self, marked_key: str | None = None, mark_text: str = "◀ 판단 대상") -> str:
        """프롬프트에 넣는 들여쓴 목록. HITL 은 [HITL] 을 앞에, 표시할 작업 뒤에 mark_text."""
        return "".join(_render_line(item, item.item_key == marked_key, mark_text) for item in self.items)


def _is_within(item_key: str, ancestor_key: str) -> bool:
    return item_key == ancestor_key or item_key.startswith(ancestor_key + ".")


def _render_line(item: WorkItem, marked: bool, mark_text: str) -> str:
    indent = "  " * item.depth
    hitl = "[HITL] " if item.kind is WorkKind.HITL else ""
    scope = f": {item.scope}" if item.scope else ""
    mark = f" {mark_text}" if marked else ""
    return f"{indent}- {hitl}{item.name}{scope}{mark}\n"
     ```
   - `task_tree/work_item.py`
     ```python
"""작업 트리의 작업 하나. split_plan 단계 안에서만 쓰는 저장 전 모양."""

from __future__ import annotations

from dataclasses import dataclass

from task_planner.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind


@dataclass(frozen=True, slots=True)
class WorkItem:
    item_key: str  # 트리 안의 위치. 맨 위 "0", 그 자식 "0.1", "0.2", 손자 "0.1.1"
    name: str
    scope: str  # 작업의 목적 한 줄. HITL 이면 확인받을 것
    kind: WorkKind
    depth: int  # 맨 위(명령서 전체)가 0
    parent_key: str | None = None
    why: str = ""  # 이 작업을 나눌지 판단한 근거
    local_id: str | None = None  # 맨 아래 작업에만 붙는 임시 이름표 ("n1", "n2" …). 저장할 때 서버 id 로 바뀐다
     ```
   - `request_md.py`
     ```python
"""명령서 md 에서 목차별 글을 꺼내고, 프롬프트 입력에 넣을 수 있게 목차를 한 단계 내린다."""

from __future__ import annotations

import re

_HEADING = re.compile(r"^# (.+)$", re.MULTILINE)


def section(request_md: str, heading: str) -> str:
    """'# <heading>' 아래의 글. 목차가 없으면 빈 글."""
    parts = _HEADING.split(request_md)  # [머리말, 제목1, 본문1, 제목2, 본문2, …]
    for title, body in zip(parts[1::2], parts[2::2], strict=True):
        if title.strip() == heading:
            return body.strip()
    return ""


def demoted(request_md: str) -> str:
    """md 의 모든 목차를 한 단계 내린 글. 입력의 '# 명령서' 아래에 넣을 때 목차가 섞이지 않게."""
    return re.sub(r"^(#+) ", r"#\1 ", request_md, flags=re.MULTILINE)
     ```
   - `prompt_call_log.py`
     ```python
"""split_plan 단계 안에서 부른 claude -p 의 요청·응답을 남긴다.
engine 은 CODE 단계 안의 호출을 기록하지 않으므로, CLAUDE_P 단계의 calls/<n>/ 와 같은 모양으로 직접 남긴다."""

from __future__ import annotations

import threading
from pathlib import Path

from task_planner.claude_utils.prompt.dto.prompt_call_record import PromptCallRecord
from task_planner.common import files


class PromptCallLog:
    def __init__(self, folder: Path) -> None:
        self.folder = folder  # 이 아래에 calls/<호출 묶음>/<n>/ 가 생긴다
        self._lock = threading.Lock()  # 동시 호출이 같은 번호를 쓰지 않게
        self._counts: dict[str, int] = {}

    def save(self, group: str, record: PromptCallRecord) -> None:
        """호출 묶음(split, spec, edges) 안에서 다음 번호의 폴더에 요청과 응답을 쓴다."""
        with self._lock:
            self._counts[group] = self._counts.get(group, 0) + 1
            call_dir = self.folder / "calls" / group / str(self._counts[group])
        files.write_json(call_dir / "request.json", record.request)
        files.write_json(call_dir / "response.json", record.response)
     ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 61개 통과 (새 시험 3개: 한 층씩 나누고 local_id 붙이기, 입력 글 모양, 노드 상한)
7. 실제 실행 (밤만쥬 명령서, opus, 판단 9번, 25.3 초, $0.252)
   ```
   - 가정집 재료와 에어프라이어로 밤만쥬 1인분 만들기
     - 밤만쥬 1인분 배합 설계
       - 만쥬 반죽 배합 설계                  n1
       - 밤앙금 소 배합 설계                  n2
     - 에어프라이어·버너 조리 공정 설계
       - 버너 준비 공정 설계                  n3
       - 에어프라이어 굽기 공정 설계            n4
     - 장보기 목록 작성                       n5
     - 단계별 레시피 작성                     n6
   ```
   HITL 은 두지 않았다 (맨 위 판단의 why: "손실 위험이 낮고 판단 기준도 정해지지 않은 일")

### split_plan / write_specs (만듦, 2026-11-19)

1. 입력
   - 함수 인자: 명령서 md, split_tree 의 작업 트리(local_id 붙음), 참여 페르소나(`Participant(persona_id, name, description)`), 호출 기록기, claude -p 호출 함수
   - 정의서 하나의 입력 글: `# 명령서` / `# 작업 트리`(◀ 정의서 대상) / `# 대상 작업`(이름, 목적, 종류) / `# 참여 페르소나`(`- 1 기본 페르소나: 설명` 처럼 id 를 앞에)
2. 출력
   - `SpecsResult(drafts, warnings)`. drafts 는 맨 아래 작업마다의 `NodeDraft(local_id, title, kind, persona_ids, output_spec, path, prerequisites)`, 트리 순서
   - 바꾸는 규칙 (기존 make_node, resolve 와 같음)
     - 이름은 트리 이름. 정의서 이름이 다르면 경고
     - 트리에서 HITL 이면 kind hitl, persona_ids 없음. 아니면 정의서의 kind, 모르는 값이면 document
     - 참여 페르소나에 없는 id 는 빼고, 남는 것이 없으면 첫 참여 페르소나 + 경고
     - output_spec = `### 하는 일` (does, 비면 트리의 목적) / `### 산출물` (`- 형태: …` + 담을 것) / `### 그 외 설명` (notes, 비면 "(없음)")
     - 선행 작업: needs 의 source 가 명령서·저장소면 넣지 않는다. 작업 이름(또는 경로)이면 그 작업 아래 맨 아래 작업 전부의 local_id 와 what. 같은 이름이 여럿이면 가장 가까운 것, 정할 수 없으면 경고
   - 정의서마다 `calls/spec/<n>/`
3. 생긴 파일 트리
   ```
   src/task_planner/workflow/make_plan/split_plan/
   ├─ prompt_caller.py              claude -p 호출 함수의 모양 (split_tree 와 같이 씀)
   └─ write_specs/
      ├─ write_specs.py
      ├─ prompt_spec.md
      ├─ prompt_spec_output.py      name, does, needs, output, notes, persona_ids, kind
      ├─ prompt_spec_need.py        what, source
      ├─ prompt_spec_product.py     form, contents
      ├─ participant.py             참여 페르소나 (페르소나 포트를 만들면 그 model 로 바꿈)
      ├─ prerequisite.py            local_id, what
      ├─ node_draft.py
      └─ specs_result.py
   tests/workflow/make_plan/test_write_specs.py
   ```
4. 프롬프트 전문 (`prompt_spec.md`, 모델 opus). 원문에서 바꾼 곳: 산출물 줄의 `needs([{what, from}])` → `needs([{what, source}])`, `persona, work_type` → `persona_ids, kind`, 필드 설명의 needs·persona·work_type 세 줄
   ```markdown
## 목적
분해가 끝난 작업 트리에서 "◀ 정의서 대상" 작업 하나의 정의서를 씁니다.
정의서는 나중에 이 작업의 작업 지시를 만드는 재료입니다.
입력: 명령서, 작업 트리 전체, 대상 작업(이름, 목적, 종류), 참여 페르소나.

## 산출물
JSON 하나: name, does, needs([{what, source}]), output({form, contents}), notes, persona_ids, kind

## 칸의 뜻
- name: 트리의 작업 이름 그대로
- does: 이 작업의 목적과 본질적으로 하는 일
- needs: 필요한 정보(what)와 출처(source). 출처는 트리의 다른 작업 이름, "명령서", "저장소" 중 하나
- output: 형태(문서 / 표 / 결정 / 코드 변경 / 조사 노트)와 담을 것(러프하게 2~4줄). 코드면 저장소 경로와 주요 작업 내용
- notes: 핵심적으로 해야 할 일과 주의할 점
- persona_ids: 참여 페르소나 가운데 이 작업에 개입하는 페르소나의 id. 여럿이면 모두. HITL 이면 빈 배열
- kind: document / research / code / hitl
   ```
5. 코드 전문 (`write_specs/write_specs.py`)
   ```python
"""3-2 정의서. 맨 아래 작업마다 정의서를 쓰고(동시 4개), 노드 spec 모양의 저장 전 노드로 바꾼다.
정의서의 needs 가운데 출처가 다른 작업인 것은 그 작업의 local_id 로 바꿔 선행 작업으로 둔다.
규칙은 기존 generate.py 의 make_node, resolve 와 같다."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from task_planner.claude_utils.prompt.call_prompt import call_prompt
from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.model.plan.node_kind import NodeKind
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.prompt_caller import PromptCaller
from task_planner.workflow.make_plan.split_plan.request_md import demoted
from task_planner.workflow.make_plan.split_plan.task_tree.task_tree import TaskTree
from task_planner.workflow.make_plan.split_plan.task_tree.work_item import WorkItem
from task_planner.workflow.make_plan.split_plan.task_tree.work_kind import WorkKind
from task_planner.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft
from task_planner.workflow.make_plan.split_plan.write_specs.participant import Participant
from task_planner.workflow.make_plan.split_plan.write_specs.prerequisite import Prerequisite
from task_planner.workflow.make_plan.split_plan.write_specs.prompt_spec_output import SpecOutput
from task_planner.workflow.make_plan.split_plan.write_specs.specs_result import SpecsResult

PARALLEL = 4
NOT_A_TASK_SOURCES = ("명령서", "저장소")  # 선행 작업이 아닌 출처

SPEC = PromptSpec(
    name="spec",
    prompt_file=Path(__file__).parent / "prompt_spec.md",
    output_type=SpecOutput,
    model="opus",
)


def write_specs(
    request_md: str,
    tree: TaskTree,
    participants: tuple[Participant, ...],
    call_log: PromptCallLog,
    caller: PromptCaller = call_prompt,
) -> SpecsResult:
    """맨 아래 작업마다 정의서를 받아 저장 전 노드로 바꾼다. 결과는 트리 순서 (n1, n2 …)."""
    leaves = tree.leaves()
    specs = _write_all_specs(request_md, tree, leaves, participants, call_log, caller)
    warnings: list[str] = []
    drafts = tuple(
        _to_draft(tree, leaf, spec, participants, warnings) for leaf, spec in zip(leaves, specs, strict=True)
    )
    return SpecsResult(drafts=drafts, warnings=tuple(warnings))


def _write_all_specs(
    request_md: str,
    tree: TaskTree,
    leaves: tuple[WorkItem, ...],
    participants: tuple[Participant, ...],
    call_log: PromptCallLog,
    caller: PromptCaller,
) -> list[SpecOutput]:
    def write_one(leaf: WorkItem) -> SpecOutput:
        output, record = caller(SPEC, build_spec_input(request_md, tree, leaf, participants))
        call_log.save("spec", record)
        return output  # type: ignore[no-any-return]

    with ThreadPoolExecutor(PARALLEL) as pool:
        return list(pool.map(write_one, leaves))


def _to_draft(
    tree: TaskTree, leaf: WorkItem, spec: SpecOutput, participants: tuple[Participant, ...], warnings: list[str]
) -> NodeDraft:
    """정의서를 노드 spec 필드로 옮긴다. 이름은 트리 이름을 쓰고, 종류·담당은 규칙에 맞게 고친다."""
    assert leaf.local_id is not None
    if spec.name.strip() != leaf.name:
        warnings.append(f'{leaf.local_id}: 정의서 이름 "{spec.name}"이 트리 이름 "{leaf.name}"과 달라 트리 이름을 씀')
    kind = _node_kind(leaf, spec)
    return NodeDraft(
        local_id=leaf.local_id,
        title=leaf.name,
        kind=kind,
        persona_ids=_persona_ids(leaf, spec, kind, participants, warnings),
        output_spec=_output_spec(leaf, spec),
        path=tree.path_of(leaf.item_key),
        prerequisites=_prerequisites(tree, leaf, spec, warnings),
    )


def _node_kind(leaf: WorkItem, spec: SpecOutput) -> NodeKind:
    """트리에서 HITL 이면 hitl. 아니면 정의서의 kind, 모르는 값이면 document."""
    if leaf.kind is WorkKind.HITL:
        return NodeKind.HITL
    if spec.kind in (NodeKind.DOCUMENT, NodeKind.RESEARCH, NodeKind.CODE):
        return NodeKind(spec.kind)
    return NodeKind.DOCUMENT


def _persona_ids(
    leaf: WorkItem, spec: SpecOutput, kind: NodeKind, participants: tuple[Participant, ...], warnings: list[str]
) -> tuple[int, ...]:
    """확인 노드는 담당이 없다. 참여 페르소나에 없는 id 는 빼고, 남는 것이 없으면 첫 참여 페르소나로 둔다."""
    if kind is NodeKind.HITL:
        return ()
    participant_ids = [participant.persona_id for participant in participants]
    chosen = tuple(persona_id for persona_id in spec.persona_ids if persona_id in participant_ids)
    if chosen or not participant_ids:
        return chosen
    warnings.append(
        f"{leaf.local_id}({leaf.name}): 담당 {spec.persona_ids} 이 참여 페르소나에 없어 {participant_ids[0]} 로 둠"
    )
    return (participant_ids[0],)


def _output_spec(leaf: WorkItem, spec: SpecOutput) -> str:
    """정의서의 does, output, notes 를 노드의 output_spec md 로 합친다 (기존 make_node 와 같은 모양)."""
    return "\n".join(
        [
            "### 하는 일",
            spec.does.strip() or leaf.scope,
            "",
            "### 산출물",
            "- 형태: " + (spec.output.form.strip() or "(정하지 않음)"),
            spec.output.contents.strip(),
            "",
            "### 그 외 설명",
            spec.notes.strip() or "(없음)",
        ]
    )


def _prerequisites(tree: TaskTree, leaf: WorkItem, spec: SpecOutput, warnings: list[str]) -> tuple[Prerequisite, ...]:
    """needs 의 출처가 다른 작업이면 그 아래 맨 아래 작업들의 local_id 로 바꾼다. 명령서·저장소는 선행 작업이 아니다."""
    found: list[Prerequisite] = []
    for need in spec.needs:
        source = need.source.strip().removeprefix("[HITL] ").strip()
        if not source or source in NOT_A_TASK_SOURCES:
            continue
        target = _find_source(tree, leaf, source)
        if target is None:
            warnings.append(
                f'{leaf.local_id}({leaf.name}): 필요 정보 "{need.what}"의 출처 "{source}"를 트리에서 하나로 찾지 못함'
            )
            continue
        found += [
            Prerequisite(local_id=prior.local_id, what=need.what.strip())
            for prior in tree.leaves_under(target.item_key)
            if prior.local_id is not None and prior.item_key != leaf.item_key
        ]
    return tuple(found)


def _find_source(tree: TaskTree, leaf: WorkItem, source: str) -> WorkItem | None:
    """출처 이름(또는 " / " 로 이은 경로)이 가리키는 작업.
    같은 이름이 여럿이면 대상과 가장 가까운 것, 정할 수 없으면 None."""
    candidates = [item for item in tree.items if item.parent_key is not None]
    if " / " in source:
        hits = [item for item in candidates if tree.path_of(item.item_key).endswith(source)]
    else:
        hits = [item for item in candidates if item.name == source]
    if len(hits) <= 1:
        return hits[0] if hits else None
    closeness = {item.item_key: _common_depth(item.item_key, leaf.item_key) for item in hits}
    closest = max(closeness.values())
    nearest = [item for item in hits if closeness[item.item_key] == closest]
    return nearest[0] if len(nearest) == 1 else None


def _common_depth(first_key: str, second_key: str) -> int:
    """두 작업의 공통 상위 작업 깊이. "0.1.2" 와 "0.1.3" 이면 2."""
    depth = 0
    for first_part, second_part in zip(first_key.split("."), second_key.split("."), strict=False):
        if first_part != second_part:
            break
        depth += 1
    return depth


def build_spec_input(request_md: str, tree: TaskTree, leaf: WorkItem, participants: tuple[Participant, ...]) -> str:
    """정의서 하나의 입력: 명령서, 작업 트리 전체, 대상 작업, 참여 페르소나 (id 포함)."""
    persona_lines = [
        f"- {person.persona_id} {person.name}: {person.description or '(설명 없음)'}" for person in participants
    ]
    return "\n\n".join(
        [
            "# 명령서\n사용자가 맡긴 원래 일입니다.\n\n" + demoted(request_md),
            "# 작업 트리\n" + tree.render(marked_key=leaf.item_key, mark_text="◀ 정의서 대상").rstrip(),
            f"# 대상 작업\n- 이름: {leaf.name}\n- 목적: {leaf.scope}\n- 종류: {leaf.kind.value}",
            "# 참여 페르소나\n" + ("\n".join(persona_lines) or "(없음)"),
        ]
    )
   ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 63개 통과 (새 시험 2개: 정의서를 저장 전 노드로 바꾸는 규칙, 입력 글 모양)
7. 실제 실행 (밤만쥬 명령서, opus. 나누기 8번 26.9초 $0.195 → 정의서 6번 28.9초 $0.294)
   - 나누기 결과는 첫 실행과 달랐다 (n1 표준 밤만쥬 레시피 조사, n2 1인분 반죽·소 배합 산정, n3 에어프라이어 굽기 조건 설정, n4 버너 공정 조건 설정, n5 장보기 목록 작성, n6 단계별 레시피 작성)
   - 선행 작업: n2 ← n1, n4 / n3 ← n1, n2, n4 / n4 ← n1, n2, n3 / n5 ← n2, n3, n4, n1 / n6 ← n2, n3, n4, n1, n5
   - 발견 1: 선행 작업에 순환이 있다 (n2 ↔ n4, n3 ↔ n4). 정의서는 "서로 맞춰야 한다"는 뜻으로 서로를 출처로 적는다. 간선 정리(write_edges)와 간선 보충 코드가 다뤄야 한다
   - 발견 2: n3 의 notes 에 줄바꿈이 글자 `\n` 으로 들어왔다 (opus 출력). output_spec 에 그대로 들어간다
   - 경고 없음

### split_plan / 선행 관계의 뜻 (사용자, 2026-11-19)

선행 관계(간선)는 "뒤 작업이 실행될 때 앞 작업의 산출물을 입력으로 받는다"는 뜻이다. 사람이 하기 좋은 순서가 아니다.
- 가 (정의서): needs 의 뜻을 좁혔다. 출처가 다른 작업이면 그 산출물이 있어야 시작할 수 있는 경우만 적고, 서로 맞춰야 할 뿐이면 notes 에 적는다
- 다 (간선): 간선 프롬프트에 순환을 푸는 규칙을 넣고, 코드가 순환을 만드는 간선을 넣지 않는다. 입력의 "선행 작업"은 "받는 산출물"로 이름을 바꿨다
- 나 (나누기에서 산출물이 한 방향으로 흐르게 나누기)는 시험 결과를 보고 정한다

정의서 needs 규칙을 고친 뒤 같은 작업 트리로 정의서를 다시 썼다 (opus 6번, 31.3 초, $0.279):

| | n2 | n3 | n4 | n5 | n6 |
|---|---|---|---|---|---|
| 고치기 전 | n1, n4 | n1, n2, n4 | n1, n2, n3 | n1, n2, n3, n4 | n1~n5 |
| 고친 뒤 | n1 | n1, n2 | n1, n2 | n2, n3, n4 | n1, n2, n3, n4 |

서로를 적은 쌍이 없어졌다 (전: n2↔n4, n3↔n4). 서로 맞춰야 하는 내용은 notes 로 옮겨 갔다. 예: n2 notes "앙금을 그대로 쓰는지 졸이는지는 '버너 공정 조건 설정'과 맞춘다".

### split_plan / write_edges (만듦, 2026-11-19)

1. 입력
   - 함수 인자: 명령서 md, write_specs 의 저장 전 노드 전부, 호출 기록기, claude -p 호출 함수
   - 노드 전부를 한 입력에 넣고 claude -p 를 1번 부른다. 노드마다 `## <local_id>` / 경로 / 종류 / 받는 산출물(`n1(제목): 받을 것`) / 산출물(output_spec 의 산출물 절)
   - 노드가 2개 미만이면 부르지 않는다
2. 출력
   - `EdgesResult(edges, warnings)`. edges 는 `EdgeDraft(from_local_id, to_local_id)`
   - 코드 정리: 간선 프롬프트의 간선을 차례로 넣되 없는 작업·자기 자신·중복·순환을 만드는 간선은 넣지 않고 경고. 그다음 받는 산출물로 적혔는데 빠진 직접 간선을 같은 규칙으로 더한다 (노드는 바로 이어진 선행 노드의 결과만 읽으므로)
   - `calls/edges/1/`
3. 생긴 파일 트리
   ```
   split_plan/write_edges/
   ├─ write_edges.py
   ├─ prompt_edges.md
   ├─ prompt_edges_output.py     edges
   ├─ edge_draft.py              from_local_id, to_local_id
   └─ edges_result.py            edges, warnings
   tests/workflow/make_plan/test_write_edges.py
   ```
4. 프롬프트 전문 (`prompt_edges.md`, 모델 opus). 원문에서 바꾼 곳: 입력 줄(필요 정보 → 받는 산출물, id → local_id), 순서 1 의 "필요 정보를" → "받는 산출물을", 순서 2 와 순환 금지 줄을 더함, 마지막 줄 from/to → from_local_id/to_local_id
   ```markdown
## 목적
실행되는 작업(맨 아래 작업과 HITL) 사이에서 산출물이 넘어가는 순서를 간선으로 잇습니다.
입력: 명령서, 작업 목록(local_id, 경로, 받는 산출물(출처는 local_id), 산출물).

## 작업 내용과 순서
1. 받는 산출물을 따라 간선을 잇습니다. 서로 의존하지 않는 작업은 간선 없이 병렬로 둡니다.
2. 두 작업이 서로의 산출물을 받는다고 적었으면 한 방향만 고릅니다. 다른 작업이 기준으로 쓸 값을 정하는 쪽을 앞에 둡니다.

## 중요한 정보
- 간선은 실제로 산출물을 받아 써야 하는 곳에만 긋습니다. 의존하지 않는 노드는 병렬로 둡니다.
- 간선을 따라가다 처음 작업으로 다시 돌아오는 순환을 만들지 않습니다.

## 답하는 칸
JSON 하나로 답합니다.

edges: 간선 목록. 간선마다 from_local_id, to_local_id(작업의 local_id). to_local_id 의 작업은 from_local_id 의 작업이 끝난 뒤 그 산출물을 받아 시작합니다.
   ```
5. 코드 전문 (`write_edges/write_edges.py`)
   ```python
"""3-3 간선. 모든 저장 전 노드를 한 번에 보여 주고 간선을 받는다 (claude -p 1번).
받은 간선은 코드가 정리한다: 쓸 수 없는 간선을 버리고, 순환을 만드는 간선은 넣지 않고,
받는 산출물로 적혔는데 빠진 직접 간선을 더한다. 노드는 바로 이어진 선행 노드의 결과만 읽기 때문이다."""

from __future__ import annotations

from pathlib import Path

from task_planner.claude_utils.prompt.call_prompt import call_prompt
from task_planner.claude_utils.prompt.dto.prompt_spec import PromptSpec
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.prompt_caller import PromptCaller
from task_planner.workflow.make_plan.split_plan.request_md import demoted
from task_planner.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_planner.workflow.make_plan.split_plan.write_edges.edges_result import EdgesResult
from task_planner.workflow.make_plan.split_plan.write_edges.prompt_edges_output import EdgesOutput
from task_planner.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft

EDGES = PromptSpec(
    name="edges",
    prompt_file=Path(__file__).parent / "prompt_edges.md",
    output_type=EdgesOutput,
    model="opus",
)


def write_edges(
    request_md: str, drafts: tuple[NodeDraft, ...], call_log: PromptCallLog, caller: PromptCaller = call_prompt
) -> EdgesResult:
    """모든 노드를 보고 간선을 받은 뒤, 버릴 것을 버리고 순환 없이 넣고, 빠진 받는 산출물 간선을 더한다."""
    if len(drafts) < 2:
        return EdgesResult(edges=(), warnings=())
    proposed = _ask_edges(request_md, drafts, call_log, caller)
    warnings: list[str] = []
    local_ids = {draft.local_id for draft in drafts}
    edges: list[EdgeDraft] = []
    for edge in proposed:
        _add_if_valid(edges, edge, local_ids, warnings, origin="간선 프롬프트")
    for edge in _prerequisite_edges(drafts):
        if edge not in edges:
            _add_if_valid(edges, edge, local_ids, warnings, origin="받는 산출물")
    return EdgesResult(edges=tuple(edges), warnings=tuple(warnings))


def _ask_edges(
    request_md: str, drafts: tuple[NodeDraft, ...], call_log: PromptCallLog, caller: PromptCaller
) -> list[EdgeDraft]:
    output, record = caller(EDGES, build_edges_input(request_md, drafts))
    call_log.save("edges", record)
    return list(output.edges)


def _prerequisite_edges(drafts: tuple[NodeDraft, ...]) -> list[EdgeDraft]:
    """정의서에서 받는 산출물로 적힌 작업마다 직접 간선 하나."""
    return [
        EdgeDraft(from_local_id=prerequisite.local_id, to_local_id=draft.local_id)
        for draft in drafts
        for prerequisite in draft.prerequisites
    ]


def _add_if_valid(
    edges: list[EdgeDraft], edge: EdgeDraft, local_ids: set[str], warnings: list[str], origin: str
) -> None:
    """없는 작업, 자기 자신, 중복, 순환을 만드는 간선은 넣지 않고 경고한다. 나머지는 edges 에 더한다."""
    label = f"{origin}의 간선 {edge.from_local_id} → {edge.to_local_id}"
    if edge.from_local_id not in local_ids or edge.to_local_id not in local_ids:
        warnings.append(f"{label}: 작업 목록에 없는 local_id 라 버림")
    elif edge.from_local_id == edge.to_local_id:
        warnings.append(f"{label}: 자기 자신을 잇는 간선이라 버림")
    elif edge in edges:
        warnings.append(f"{label}: 이미 있는 간선이라 버림")
    elif _reaches(edges, start=edge.to_local_id, goal=edge.from_local_id):
        warnings.append(f"{label}: 넣으면 순환이 생겨 넣지 않음")
    else:
        edges.append(edge)


def _reaches(edges: list[EdgeDraft], start: str, goal: str) -> bool:
    """start 에서 간선을 따라가 goal 에 닿는지. 닿으면 goal → start 간선이 순환을 만든다."""
    seen: set[str] = set()
    waiting = [start]
    while waiting:
        current = waiting.pop()
        if current == goal:
            return True
        if current in seen:
            continue
        seen.add(current)
        waiting += [edge.to_local_id for edge in edges if edge.from_local_id == current]
    return False


def build_edges_input(request_md: str, drafts: tuple[NodeDraft, ...]) -> str:
    """간선 입력: 명령서와, 작업마다 local_id·경로·종류·받는 산출물·산출물."""
    titles = {draft.local_id: draft.title for draft in drafts}
    sections = [
        "# 명령서\n사용자가 맡긴 원래 일입니다.\n\n" + demoted(request_md),
        "# 작업 목록\n실행되는 작업입니다. 목차의 n 으로 시작하는 값이 작업의 local_id 입니다.",
    ]
    for draft in drafts:
        received = [
            f"  - {item.local_id}({titles.get(item.local_id, '?')}): {item.what}" for item in draft.prerequisites
        ]
        sections.append(
            "\n".join(
                [
                    f"## {draft.local_id}",
                    f"- 경로: {draft.path}",
                    f"- 종류: {draft.kind.value}",
                    "- 받는 산출물:",
                    "\n".join(received) or "  (없음)",
                    "- 산출물:",
                    _product_part(draft.output_spec),
                ]
            )
        )
    return "\n\n".join(sections)


def _product_part(output_spec: str) -> str:
    """output_spec 에서 '### 산출물' 절의 글만."""
    after = output_spec.split("### 산출물\n", 1)[-1]
    return after.split("\n\n### 그 외 설명", 1)[0].strip()
   ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 66개 통과 (새 시험 3개: 버리기·순환 막기·빠진 간선 더하기, 양방향이 오면 하나만, 노드 전부를 한 입력에)
7. 실제 실행 (위 고친 정의서, opus 1번, 입력 3,240 자, 4.5 초, $0.047)
   ```
   n1 표준 밤만쥬 레시피 조사 ─┬→ n2 1인분 반죽·소 배합 산정 ─┬→ n3 에어프라이어 굽기 조건 설정 ─┬→ n5 장보기 목록 작성
                              │                              └→ n4 버너 공정 조건 설정 ────────┤
                              ├→ n3, n4, n6                                                   └→ n6 단계별 레시피 작성
   ```
   간선 12개: n1→n2, n1→n3, n2→n3, n1→n4, n2→n4, n2→n5, n3→n5, n4→n5, n1→n6, n2→n6, n3→n6, n4→n6. 받는 산출물과 같고, 코드가 버리거나 더한 간선은 없었다. n3·n4 는 동시에, n5·n6 은 동시에 실행할 수 있다

### split_plan / save_graph (만듦, 2026-11-19)

정함 (사용자, 2026-11-19): split_plan 을 다시 수행하면 앞선 시도가 남긴 노드를 지우고 새로 저장한다. 계획이 작성 중일 때만 지우고, 아니면 멈춘다. 정의서에 글자로 들어온 `\n` 은 저장할 때 줄바꿈으로 바꾼다.

1. 입력: plan_id, 저장 전 노드 전부, 간선 전부, 계획 저장소 읽기·쓰기 포트
2. 출력
   - 계획 저장소에 노드(트리 순서)와 간선
   - `SavedGraph(node_ids, edge_count, removed_node_count)`. node_ids 는 local_id → 서버 id. split_plan 단계가 result.json 에 남긴다
   - 작성 중이 아닌 계획이면 `PlanNotDraftingError`
3. 생긴 파일 트리
   ```
   split_plan/save_graph/
   ├─ save_graph.py
   ├─ saved_graph.py
   └─ plan_not_drafting_error.py
   tests/workflow/make_plan/test_save_graph.py
   ```
4. 프롬프트: 없음
5. 코드 전문 (`save_graph/save_graph.py`)
   ```python
"""split_plan 의 마지막 기능. 저장 전 노드와 간선을 계획 저장소에 저장한다.
노드를 먼저 저장해 서버 id 를 받고, 그 id 로 간선을 바꿔 저장한다.
split_plan 을 다시 수행하면 앞선 시도가 남긴 노드를 지우고 새로 저장한다.
지우는 것은 작성 중인 계획에서만 한다 (사용자, 2026-11-19)."""

from __future__ import annotations

from task_planner.model.plan.plan_status import PlanStatus
from task_planner.port.plan_api.dto.new_node import NewNode
from task_planner.port.plan_api.plan_api_reader import PlanApiReader
from task_planner.port.plan_api.plan_api_writer import PlanApiWriter
from task_planner.workflow.make_plan.split_plan.save_graph.plan_not_drafting_error import PlanNotDraftingError
from task_planner.workflow.make_plan.split_plan.save_graph.saved_graph import SavedGraph
from task_planner.workflow.make_plan.split_plan.write_edges.edge_draft import EdgeDraft
from task_planner.workflow.make_plan.split_plan.write_specs.node_draft import NodeDraft


def save_graph(
    plan_id: int,
    drafts: tuple[NodeDraft, ...],
    edges: tuple[EdgeDraft, ...],
    reader: PlanApiReader,
    writer: PlanApiWriter,
) -> SavedGraph:
    """앞선 시도의 노드를 지우고, 노드를 저장해 서버 id 를 받고, 그 id 로 간선을 저장한다."""
    removed_node_count = _clear_previous_nodes(plan_id, reader, writer)
    node_ids = _save_nodes(plan_id, drafts, writer)
    _save_edges(plan_id, edges, node_ids, writer)
    return SavedGraph(node_ids=node_ids, edge_count=len(edges), removed_node_count=removed_node_count)


def _clear_previous_nodes(plan_id: int, reader: PlanApiReader, writer: PlanApiWriter) -> int:
    """작성 중인 계획이면 남아 있는 노드를 지운다 (닿은 간선도 함께 지워진다). 작성 중이 아니면 멈춘다."""
    plan = reader.get_plan(plan_id)
    if plan.status is not PlanStatus.DRAFTING:
        raise PlanNotDraftingError(
            f"계획 {plan_id} 는 작성 중이 아니라({plan.status.value}) 노드를 다시 만들지 않습니다"
        )
    for node in plan.nodes:
        writer.delete_node(plan_id, node.node_id)
    return len(plan.nodes)


def _save_nodes(plan_id: int, drafts: tuple[NodeDraft, ...], writer: PlanApiWriter) -> dict[str, int]:
    """트리 순서대로 저장하고 local_id → 서버 id 표를 돌려준다."""
    node_ids: dict[str, int] = {}
    for draft in drafts:
        new_node = NewNode(
            title=draft.title,
            kind=draft.kind,
            persona_ids=draft.persona_ids,
            output_spec=_real_line_breaks(draft.output_spec),
        )
        node_ids[draft.local_id] = writer.add_node(plan_id, new_node).node_id
    return node_ids


def _save_edges(plan_id: int, edges: tuple[EdgeDraft, ...], node_ids: dict[str, int], writer: PlanApiWriter) -> None:
    for edge in edges:
        writer.add_edge(plan_id, node_ids[edge.from_local_id], node_ids[edge.to_local_id])


def _real_line_breaks(text: str) -> str:
    """모델이 줄바꿈을 글자 '\\n' 으로 낸 것을 실제 줄바꿈으로 바꾼다 (사용자, 2026-11-19)."""
    return text.replace("\\n", "\n")
   ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 69개 통과 (새 시험 3개: 노드 다음 간선을 서버 id 로, 다시 수행하면 앞선 노드를 지움, 작성 중이 아니면 손대지 않음)
7. 실제 실행 (밤만쥬 저장 전 노드 6개·간선 12개를 시험용 mock 폴더에): node_ids n1→1 … n6→6, 간선 12개. `.mockData/plans/1.json` 에 계획(drafting), 노드 6개(todo), 간선 12개, `ids.json` 은 plan 1, node 6, edge 12

### register_plan (만들기 전 계획, 2026-11-19)

1. 입력
   - 앞 단계 결과: `context.read("write_request")` → `{"title": str, "request": str}` (선언의 `reads=("write_request",)`)
   - 포트: 페르소나 목록 (`persona_api_reader()`. mock 이면 `.mockData/personas.json`)
2. 출력
   - 계획 저장소: 계획 하나. 제목·명령서는 write_request 결과, persona_ids 는 첫 페르소나 하나, 상태 drafting, 노드·간선 없음
   - 작업 폴더: `.plan/<plan_id>/command.md` (명령서 사본)
   - 단계 결과: `register_plan_<uuid8>/result.json` → `{"by_item": {"-": {"plan_id": 1}}}`
3. 생길 파일 트리
   ```
   코드
   src/task_planner/workflow/make_plan/register_plan/
   ├─ __init__.py
   ├─ register_plan_task.py
   └─ no_persona_error.py           페르소나가 하나도 없을 때
   make_plan_flow.py                register_plan 을 더함 (reads=("write_request",))
   tests/workflow/test_make_plan.py 시험 더함

   실행하면 (작업 폴더)
   .task_planner/sessions/<세션 id>/runs/<실행 id>/register_plan_<uuid8>/result.json
   .plan/<plan_id>/command.md
   mock (claude-task-planner 저장소)
   .mockData/personas.json          없으면 처음 값으로 생김
   .mockData/plans/<plan_id>.json
   .mockData/ids.json
   ```
4. 프롬프트: 없음
5. 코드 (만들 모양)
   ```python
   @TASKS.register_as("make_plan.register_plan")
   class RegisterPlanTask(Task):
       request_type = CodeRequest
       output_kind = OutputKind.DATA

       def build_request(self, context: FlowContext) -> CodeRequest:
           return CodeRequest()

       def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
           # 명령서로 계획을 등록하고, 받은 id 로 이 작업 폴더에 계획 폴더를 만든다
           written = context.read("write_request")
           new_plan = NewPlan(title=written["title"], request=written["request"], persona_ids=_default_persona_ids())
           plan = plan_api_writer().create_plan(new_plan)
           DefaultPlanFolderWriter().create_plan(plan.plan_id, written["request"])
           return TaskOutput({"plan_id": plan.plan_id})


   def _default_persona_ids() -> tuple[int, ...]:
       """첫 판의 참여 페르소나: 페르소나 목록의 첫 페르소나 하나. 없으면 NoPersonaError."""
   ```
6. 시험 (만들 것)
   - 가짜 대화 기록과 가짜 claude 로 start → done 을 돌리면 interview → write_request → register_plan 까지 가고 finished
   - mock 계획: 제목·명령서가 write_request 결과와 같고, persona_ids [1], 상태 drafting
   - 작업 폴더: `.plan/<plan_id>/command.md` 내용이 명령서와 같음
   - 페르소나 목록이 비면 failed

### register_plan (만듦, 2026-11-19)

계획대로 만들었다. 위 "만들기 전 계획"의 1~3 과 같다.

5. 코드 전문 (`register_plan/register_plan_task.py`)
   ```python
"""register_plan: write_request 의 제목과 명령서로 계획을 등록하고, 받은 plan_id 로 이 작업 폴더에 계획 폴더를 만든다.
참여 페르소나는 첫 판에서 페르소나 목록의 첫 페르소나 하나다 (사용자, 2026-11-19). 고르기는 나중에 더한다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_planner.port.persona_api.persona_api_choice import persona_api_reader
from task_planner.port.plan_api.dto.new_plan import NewPlan
from task_planner.port.plan_api.plan_api_choice import plan_api_writer
from task_planner.workflow.make_plan.register_plan.no_persona_error import NoPersonaError


@TASKS.register_as("make_plan.register_plan")
class RegisterPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 명령서로 계획을 등록하고, 받은 id 로 이 작업 폴더에 계획 폴더를 만든다
        written = context.read("write_request")
        new_plan = NewPlan(title=written["title"], request=written["request"], persona_ids=_default_persona_ids())
        plan = plan_api_writer().create_plan(new_plan)
        DefaultPlanFolderWriter().create_plan(plan.plan_id, written["request"])
        return TaskOutput({"plan_id": plan.plan_id})


def _default_persona_ids() -> tuple[int, ...]:
    """첫 판의 참여 페르소나: 페르소나 목록의 첫 페르소나 하나. 없으면 NoPersonaError."""
    personas = persona_api_reader().list_personas()
    if not personas:
        raise NoPersonaError("페르소나 목록이 비어 있어 계획을 등록하지 못했습니다")
    return (personas[0].persona_id,)
   ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 84개 통과 (새 시험 2개: 첫 페르소나로 등록하고 계획 폴더를 만듦, 페르소나가 없으면 failed). make_plan 시험은 작업 폴더를 임시 폴더로 바꿔 돌린다 (`.plan/` 이 저장소에 생기지 않게)
7. 실제 실행 (CLI, 밤만쥬 인터뷰 대화 기록, write_request 는 실제 opus, 시험용 mock 폴더)
   ```
   작업 폴더
   ├─ .plan/1/command.md                                      명령서 사본
   └─ .task_planner/sessions/try2/runs/r_20261119_053615/
      ├─ interview_f3244c81/result.json
      ├─ write_request_ac9dbeff/result.json, calls/1/
      └─ register_plan_b6f35063/result.json                   {"plan_id": 1}
   mock 폴더
   ├─ personas.json                                           처음 값으로 생김
   ├─ ids.json
   └─ plans/1.json   {plan_id: 1, title: "가정집 재료와 에어프라이어로 밤만쥬 1인분 만들기", persona_ids: [1], status: drafting, nodes: [], edges: []}
   ```

### split_plan 단계 (만듦, 2026-11-19)

정함 (사용자, 2026-11-19): 지금까지 하나씩 만든 네 기능을 단계 하나로 묶어 흐름에 넣는다. 그러면서 바뀐 데이터(Persona model)와 구현체(plan_api, persona_api 고르기 함수)를 반영한다. 네 기능의 로직은 바꾸지 않는다. 지식 검색은 이번에도 "없음".

1. 입력
   - 앞 단계 결과: `context.read("register_plan")` → `{plan_id}` (선언의 `reads=("register_plan",)`)
   - 포트: `plan_api_reader().get_plan(plan_id)` (제목, 명령서, persona_ids. 요청문의 원본은 API), `persona_api_reader().list_personas()` (참여 페르소나)
2. 출력
   - 계획 저장소: 노드와 간선
   - 단계 결과: `{"node_ids": {"n1": 1, …}, "edge_count": int, "warnings": [str]}`
   - 호출 기록: `split_plan_<uuid8>/files/calls/split/<n>/`, `spec/<n>/`, `edges/1/` (engine 이 단계마다 만들어 주는 산출물 폴더)
3. 바뀐 파일
   ```
   src/task_planner/workflow/make_plan/
   ├─ make_plan_flow.py                  split_plan 을 더함
   └─ split_plan/
      ├─ split_plan_task.py              새로 만듦
      └─ write_specs/
         ├─ write_specs.py               Participant → Persona
         └─ participant.py               지움
   tests/workflow/test_make_plan.py      가짜 claude 를 네 종류 프롬프트에 답하게, 시험 1개
   tests/workflow/make_plan/test_write_specs.py   Persona 로
   ```
4. 프롬프트: 이 단계가 새로 더한 것은 없다. 네 기능의 프롬프트는 위 split_tree, write_specs, write_edges 기록과 같다
5. 코드 전문 (`split_plan/split_plan_task.py`)
   ```python
"""split_plan: register_plan 이 등록한 계획의 명령서로 노드와 간선을 만들어 계획 저장소에 저장한다.
안에서 네 기능을 차례로 부른다: split_tree(한 층씩 나누기) → write_specs(정의서) → write_edges(간선) → save_graph(저장).
나누기는 몇 번 부를지 실행 전에 모르므로 engine 단계 하나 안에서 우리 코드가 반복한다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.model.persona.persona import Persona
from task_planner.port.persona_api.persona_api_choice import persona_api_reader
from task_planner.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_planner.workflow.make_plan.split_plan.prompt_call_log import PromptCallLog
from task_planner.workflow.make_plan.split_plan.save_graph.save_graph import save_graph
from task_planner.workflow.make_plan.split_plan.split_tree.split_tree import split_tree
from task_planner.workflow.make_plan.split_plan.write_edges.write_edges import write_edges
from task_planner.workflow.make_plan.split_plan.write_specs.write_specs import write_specs


@TASKS.register_as("make_plan.split_plan")
class SplitPlanTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 계획의 명령서로 작업 트리 → 정의서 → 간선을 만들고, 계획 저장소에 노드와 간선을 저장한다.
        # 명령서는 계획 저장소에서 읽는다 (요청문의 원본은 API). 호출 기록은 이 단계의 산출물 폴더에 남긴다
        plan = plan_api_reader().get_plan(context.read("register_plan")["plan_id"])
        call_log = PromptCallLog(context.output_dir())
        split = split_tree(plan.title, plan.request, call_log)
        specs = write_specs(plan.request, split.tree, _participants(plan.persona_ids), call_log)
        edges = write_edges(plan.request, specs.drafts, call_log)
        saved = save_graph(plan.plan_id, specs.drafts, edges.edges, plan_api_reader(), plan_api_writer())
        return TaskOutput(
            {
                "node_ids": saved.node_ids,
                "edge_count": saved.edge_count,
                "warnings": [*split.warnings, *specs.warnings, *edges.warnings],
            }
        )


def _participants(persona_ids: tuple[int, ...]) -> tuple[Persona, ...]:
    """페르소나 목록 가운데 계획에 참여한 것만, 계획의 persona_ids 순서대로."""
    by_id = {persona.persona_id: persona for persona in persona_api_reader().list_personas()}
    return tuple(by_id[persona_id] for persona_id in persona_ids if persona_id in by_id)
   ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 85개 통과. 새 시험은 done 한 번에 write_request → register_plan → split_plan 까지 가고, mock 계획에 노드 2개·간선 1개, result.json 의 node_ids, calls 의 split 3·spec 2·edges 1 을 본다. 가짜 claude 는 입력 글의 머리(`# 지금까지의 작업 트리` / `# 대상 작업` / `# 작업 목록` / 그 밖)로 어떤 프롬프트인지 알아본다
7. 실제 실행 (CLI, 밤만쥬 인터뷰 대화 기록, 실제 opus, 시험용 mock 폴더)
   - done 한 번에 68 초. write_request 7.2 초 $0.045, split_plan 약 61 초 (나누기 7번, 정의서 5번, 간선 1번). 합계 $0.465
   - 노드 5개: 1 밤만쥬 1인분 배합 설계, 2 버너 손질 조건 설정, 3 에어프라이어 굽기 조건 설정, 4 단계별 레시피 작성, 5 장보기 목록 작성 (모두 document)
   - 간선 7개: 1→2, 1→3, 1→4, 2→4, 3→4, 4→5, 1→5. 순환 없음, 경고 없음
   ```
   runs/r_20261119_054039/
   ├─ interview_c2ae5b91/result.json
   ├─ write_request_3a4fdbe3/result.json, calls/1/
   ├─ register_plan_f239c11c/result.json
   └─ split_plan_a05d5347/
      ├─ result.json                       node_ids n1~n5, edge_count 7, warnings []
      └─ files/calls/split/1~7, spec/1~5, edges/1
   ```
   - 확인하지 못한 것: 단계를 다시 수행할 때 engine 이 단계 폴더의 이전 호출 기록을 지우는지

### prepare_show (만들기 전 계획, 2026-11-19)

1. 입력
   - 앞 단계 결과
     - `context.read("register_plan")` → `{"plan_id": int}`
     - `context.read("split_plan")` → `{"warnings": [str], ...}`
     - `context.read("interview")` → `{"transcript": str | None, ...}`
     - 선언의 `reads=("interview", "register_plan", "split_plan")`
   - 포트: `plan_api_reader().get_plan(plan_id)` (노드, 간선, 상태)
2. 출력
   - 계획 저장소: 상태 drafting → reviewing (`set_plan_status`). 이미 reviewing 이면 그대로. 그 밖의 상태면 `PlanNotShowableError` 로 실패
   - 작업 폴더: `.plan/<plan_id>/shown.json` → `{"shown_at": "2026-11-19T05:41:47Z", "transcript": "/Users/…/<세션 id>.jsonl"}`
   - 단계 결과: `{"summary": str}`. 보일 글 모양:
     ```text
     계획 1 "가정집 재료와 에어프라이어로 밤만쥬 1인분 만들기" 을 만들었습니다. 노드 5개, 간선 7개.

     | 노드 | 제목 | 종류 | 받는 산출물 |
     |---|---|---|---|
     | 1 | 밤만쥬 1인분 배합 설계 | document | 없음 |
     | 2 | 버너 손질 조건 설정 | document | 1 |
     | 4 | 단계별 레시피 작성 | document | 1, 2, 3 |
     …

     확인 노드(HITL): 없음
     경고: 없음
     ```
     - 확인 노드가 있으면 노드 id, 제목, 확인받을 것(output_spec 의 "### 하는 일" 첫 줄)을 줄마다
     - 경고가 있으면 split_plan 의 warnings 를 줄마다. 노드 상한에 닿았다는 경고면 그대로 보인다 (늘릴지는 묻지 않는다. 기존 보고의 "늘릴지 묻기"는 다시 생성이 판정 전이라 뺌)
     - 기존 계획 스킬 "5. 보고"(/Users/dankim/orca/workspaces/productivility/persona-enhancer-pg2/plugin/skills/plan/SKILL.md:74-85)에서 그래프 버전, 웹 편집기, 지식이 들어간 작업 수, 시간·비용은 뺀다 (버전·웹 편집기 없앰, 지식 검색 연결 안 함, 시간·비용은 engine 기록에 있음)
3. 생길 파일 트리
   ```
   코드
   src/task_planner/model/plan/shown_record.py                  새로: ShownRecord(shown_at, transcript)
   src/task_planner/port/local/plan_folder/
   ├─ plan_folder_reader.py               read_shown(plan_id) -> ShownRecord | None 를 더함
   ├─ plan_folder_writer.py               save_shown(plan_id, record) 를 더함
   ├─ default_plan_folder_reader.py       구현 더함
   ├─ default_plan_folder_writer.py       구현 더함
   ├─ shown_record_file_converter.py      새로: ShownRecord ↔ shown.json
   └─ plan_folder_location.py             shown_file(plan_id) 를 더함
   src/task_planner/workflow/make_plan/prepare_show/
   ├─ __init__.py
   ├─ prepare_show_task.py
   ├─ plan_summary.py                     보일 글 만들기 (build_summary)
   └─ plan_not_showable_error.py          검토 중으로 바꿀 수 없는 상태
   make_plan_flow.py                      prepare_show 를 더함
   tests/port/plan_folder/test_plan_folder.py   shown 저장·읽기 시험
   tests/workflow/make_plan/test_plan_summary.py 보일 글 시험
   tests/workflow/test_make_plan.py       흐름 시험 더함

   실행하면 (작업 폴더)
   .plan/<plan_id>/shown.json
   .task_planner/…/prepare_show_<uuid8>/result.json
   ```
4. 프롬프트: 없음
5. 코드 (만들 모양)
   ```python
   @TASKS.register_as("make_plan.prepare_show")
   class PrepareShowTask(Task):
       request_type = CodeRequest
       output_kind = OutputKind.DATA

       def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
           # 계획을 검토 중으로 바꾸고, 보여 준 기록을 남기고, 사용자에게 보일 글을 만든다
           plan_id = context.read("register_plan")["plan_id"]
           plan = _move_to_reviewing(plan_id)
           shown = ShownRecord(shown_at=utc_now(), transcript=context.read("interview")["transcript"])
           DefaultPlanFolderWriter().save_shown(plan_id, shown)
           return TaskOutput({"summary": build_summary(plan, context.read("split_plan")["warnings"])})


   def _move_to_reviewing(plan_id: int) -> Plan:
       """작성 중이면 검토 중으로 바꾼다. 이미 검토 중이면 그대로. 그 밖이면 PlanNotShowableError."""
   ```
6. 시험 (만들 것)
   - 포트: save_shown 뒤 read_shown 이 같은 값, 없으면 None
   - 보일 글: 노드 표의 받는 산출물, 확인 노드 줄, 경고 줄
   - 흐름: done 한 번에 prepare_show 까지 → mock 계획 상태 reviewing, `.plan/1/shown.json` 에 시각과 대화 기록 경로, result.json 의 summary
   - 이미 검토 중이면 그대로, 승인 상태면 failed

### prepare_show (만듦, 2026-11-19)

계획대로 만들었다 (계획 폴더 포트에 메서드 두 개를 더하는 것은 사용자 확인). 위 "만들기 전 계획"의 1~3 과 같다.

5. 코드 전문
   - `prepare_show/prepare_show_task.py`
     ```python
"""prepare_show: 계획을 검토 중으로 바꾸고, 보여 준 기록을 계획 폴더에 남기고, 사용자에게 보일 글을 만든다.
보여 준 기록(시각, 대화 기록 경로)은 B 의 지식 추출이 계획 id 로 찾아 읽는다 (사용자, 2026-11-19)."""

from __future__ import annotations

from typing import Any

from task_planner.common.clock import utc_now
from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_status import PlanStatus
from task_planner.model.plan.shown_record import ShownRecord
from task_planner.port.local.plan_folder.default_plan_folder_writer import DefaultPlanFolderWriter
from task_planner.port.plan_api.plan_api_choice import plan_api_reader, plan_api_writer
from task_planner.workflow.make_plan.prepare_show.plan_not_showable_error import PlanNotShowableError
from task_planner.workflow.make_plan.prepare_show.plan_summary import build_summary


@TASKS.register_as("make_plan.prepare_show")
class PrepareShowTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 계획을 검토 중으로 바꾸고, 보여 준 기록을 남기고, 사용자에게 보일 글을 만든다
        plan_id = context.read("register_plan")["plan_id"]
        plan = _move_to_reviewing(plan_id)
        shown = ShownRecord(shown_at=utc_now(), transcript=context.read("interview")["transcript"])
        DefaultPlanFolderWriter().save_shown(plan_id, shown)
        return TaskOutput({"summary": build_summary(plan, context.read("split_plan")["warnings"])})


def _move_to_reviewing(plan_id: int) -> Plan:
    """작성 중이면 검토 중으로 바꾼다. 이미 검토 중이면 그대로. 그 밖이면 PlanNotShowableError."""
    plan = plan_api_reader().get_plan(plan_id)
    if plan.status is PlanStatus.REVIEWING:
        return plan
    if not plan.status.can_move_to(PlanStatus.REVIEWING):
        raise PlanNotShowableError(f"계획 {plan_id} 는 {plan.status.value} 상태라 검토 중으로 바꿀 수 없습니다")
    return plan_api_writer().set_plan_status(plan_id, PlanStatus.REVIEWING)
     ```
   - `prepare_show/plan_summary.py`
     ```python
"""prepare_show 가 사용자에게 보일 글: 계획 한 줄, 노드 표, 확인 노드, 경고."""

from __future__ import annotations

from task_planner.model.plan.node_kind import NodeKind
from task_planner.model.plan.plan import Plan
from task_planner.model.plan.plan_node import PlanNode


def build_summary(plan: Plan, warnings: list[str]) -> str:
    """계획 머리 줄, 노드 표, 확인 노드 줄, 경고 줄을 빈 줄로 이은 글."""
    head = f'계획 {plan.plan_id} "{plan.title}" 을 만들었습니다. 노드 {len(plan.nodes)}개, 간선 {len(plan.edges)}개.'
    return "\n\n".join([head, _node_table(plan), _hitl_lines(plan), _warning_lines(warnings)])


def _node_table(plan: Plan) -> str:
    rows = ["| 노드 | 제목 | 종류 | 받는 산출물 |", "|---|---|---|---|"]
    for node in plan.nodes:
        received = ", ".join(str(node_id) for node_id in plan.prerequisites(node.node_id)) or "없음"
        rows.append(f"| {node.node_id} | {node.title} | {node.kind.value} | {received} |")
    return "\n".join(rows)


def _hitl_lines(plan: Plan) -> str:
    hitl_nodes = [node for node in plan.nodes if node.kind is NodeKind.HITL]
    if not hitl_nodes:
        return "확인 노드(HITL): 없음"
    lines = [f"- {node.node_id} {node.title}: {_what_to_confirm(node)}" for node in hitl_nodes]
    return "확인 노드(HITL):\n" + "\n".join(lines)


def _what_to_confirm(node: PlanNode) -> str:
    """확인받을 것: output_spec 의 '### 하는 일' 바로 아래 첫 줄."""
    after_heading = node.output_spec.split("### 하는 일\n", 1)[-1]
    return after_heading.strip().splitlines()[0] if after_heading.strip() else "(없음)"


def _warning_lines(warnings: list[str]) -> str:
    if not warnings:
        return "경고: 없음"
    return "경고:\n" + "\n".join(f"- {warning}" for warning in warnings)
     ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 90개 통과. 새 시험 5개: shown 저장·읽기(덮어쓰기), 보일 글(노드 표·확인 노드·경고), 작성 중→검토 중과 이미 검토 중, 승인 상태는 거절, 흐름(done 한 번에 prepare_show 까지 → reviewing, shown.json, summary). register_plan 흐름 시험은 상태를 보지 않게 고쳤다 (뒤 단계가 reviewing 으로 바꾸므로)
7. 실제 계획(위 split_plan 실제 실행의 밤만쥬 계획)으로 만든 보일 글
   ```text
   계획 1 "가정집 재료와 에어프라이어로 밤만쥬 1인분 만들기" 을 만들었습니다. 노드 5개, 간선 7개.

   | 노드 | 제목 | 종류 | 받는 산출물 |
   |---|---|---|---|
   | 1 | 밤만쥬 1인분 배합 설계 | document | 없음 |
   | 2 | 버너 손질 조건 설정 | document | 1 |
   | 3 | 에어프라이어 굽기 조건 설정 | document | 1 |
   | 4 | 단계별 레시피 작성 | document | 1, 2, 3 |
   | 5 | 장보기 목록 작성 | document | 4, 1 |

   확인 노드(HITL): 없음

   경고: 없음
   ```

### show_plan (만듦, 2026-11-19)

1. 입력: `context.read("prepare_show")["summary"]`, `context.read("register_plan")["plan_id"]` (선언의 `reads=("register_plan", "prepare_show")`)
2. 출력: 메인 세션에 show 지시. `payload.text` = 보일 글 + 빈 줄 + "고칠 곳이 있으면 대화로 말해 주세요.\n확정은 /plan-go <id>, 불허는 /plan-cancel <id>". 메인 세션이 보이고 next 를 부르면 흐름이 끝난다 (finished). 단계 결과는 `{}`
3. 생긴 파일: `workflow/make_plan/show_plan/show_plan_task.py`, `make_plan_flow.py` 에 한 줄
4. 프롬프트: 메인 세션에 넘기는 글은 위 2 의 글이다. 보이는 방법은 run 스킬의 show 처리("payload.text 의 내용을 사용자에게 답변으로 알리고 next 를 부릅니다")
5. 코드 전문
   - `show_plan/show_plan_task.py`
     ```python
"""show_plan: prepare_show 가 만든 글을 사용자에게 보이고, 고치는 방법과 확정·불허 명령을 계획 id 까지 넣어 안내한다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.show_request import ShowRequest

# 계획서(specs/plans/workflow-make_plan.md) show_plan 의 보일 글 그대로
GUIDE = """고칠 곳이 있으면 대화로 말해 주세요.
확정은 /plan-go {plan_id}, 불허는 /plan-cancel {plan_id}"""


@TASKS.register_as("make_plan.show_plan")
class ShowPlanTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        # 보일 글 아래에 다음 명령을 계획 id 까지 넣어 붙인다 (사용자, 2026-11-19)
        summary = context.read("prepare_show")["summary"]
        plan_id = context.read("register_plan")["plan_id"]
        return ShowRequest(f"{summary}\n\n{GUIDE.format(plan_id=plan_id)}")

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})
     ```
   - `make_plan_flow.py` (여섯 단계 모두)
     ```python
"""make_plan 워크플로 선언. 계획서: specs/plans/workflow-make_plan.md

interview → write_request → register_plan → split_plan → prepare_show → show_plan.
"""

from __future__ import annotations

from task_planner.engine.definition.flow_definition import FlowDefinition
from task_planner.engine.definition.ref import Ref
from task_planner.engine.definition.unit.builders import group, task
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.workflow.make_plan.interview import interview_task  # noqa: F401
from task_planner.workflow.make_plan.prepare_show import prepare_show_task  # noqa: F401
from task_planner.workflow.make_plan.register_plan import register_plan_task  # noqa: F401
from task_planner.workflow.make_plan.show_plan import show_plan_task  # noqa: F401
from task_planner.workflow.make_plan.split_plan import split_plan_task  # noqa: F401
from task_planner.workflow.make_plan.write_request import write_request_task  # noqa: F401

MAKE_PLAN_FLOW = FlowDefinition(
    name="make_plan",
    description="사용자를 인터뷰해 명령서를 정리하고 계획을 만들어 보인다",
    root=group("make_plan", ChildRun.IN_ORDER,
        task("interview", PerformedBy.MAIN_SESSION_TALK, Ref("make_plan.interview")),
        task("write_request", PerformedBy.CLAUDE_P, Ref("make_plan.write_request"), reads=("interview",)),
        task("register_plan", PerformedBy.CODE, Ref("make_plan.register_plan"), reads=("write_request",)),
        task("split_plan", PerformedBy.CODE, Ref("make_plan.split_plan"), reads=("register_plan",)),
        task("prepare_show", PerformedBy.CODE, Ref("make_plan.prepare_show"),
             reads=("interview", "register_plan", "split_plan")),
        task("show_plan", PerformedBy.MAIN_SESSION_SHOW, Ref("make_plan.show_plan"),
             reads=("register_plan", "prepare_show"))),
)  # fmt: skip
     ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 91개 통과. 새 시험: done 뒤 show 지시의 글이 보일 글로 시작하고 "/plan-go 1, 불허는 /plan-cancel 1" 로 끝나며, next 뒤 finished. 다른 흐름 시험은 done → show → next → finished 를 거치게 고침

### 끝까지 시험: Claude Code (2026-11-19)

방법: Claude Code 를 대화 없이(`claude -p`) 띄우고, 같은 세션 id 로 이어 부르며 Claude 가 사용자 역할로 답했다. 플러그인은 `--plugin-dir`, 허용 도구는 `task-planner` 명령·Skill·AskUserQuestion 만. 작업 폴더는 scratchpad 의 빈 폴더(tpm-try2), mock 은 저장소의 실제 `.mockData/`.

| 차례 | 사용자 말 | 일어난 일 |
|---|---|---|
| 1 | `/task-planner:run make_plan 파이썬으로 할 일 목록을 관리하는 작은 CLI 도구를 만들고 싶어` | `start make_plan` → talk 지시 → **Skill grilling 을 불렀다** → 질문 7개를 추천 답과 함께 한 번에 (grilling 의 라운드 방식) |
| 2 | "Q1 은 b 로 해줘. 나머지는 다 추천대로 예." | 목차로 정리해 보이고 "이 내용으로 정리할까요? (예 / 더 이야기)" |
| 3 | "예" | `done` → write_request → register_plan → split_plan → prepare_show 가 이어서 돌고 show 지시 (65 초) → `next` → finished |

결과
- 계획 1 "파이썬 할 일 목록 관리 CLI 도구(todo) 만들기", 상태 reviewing, 노드 6개, 간선 13개, 경고 없음
  ```
  | 1 | CLI 명령·데이터 형식 설계 | document | 없음 |
  | 2 | 패키지 골격 구성 | code | 없음 |
  | 3 | JSON 저장소 모듈 구현 | code | 1, 2 |
  | 4 | 명령 여섯 가지 구현 | code | 1, 2, 3 |
  | 5 | 명령별 pytest 테스트 작성 | code | 1, 2, 3, 4 |
  | 6 | README 작성 | document | 1, 2, 3, 4 |
  ```
- claude -p 비용 $0.585 (명령서 1, 나누기 7, 정의서 6, 간선 1). 메인 세션 비용은 따로
- 작업 폴더: `.plan/1/command.md`, `.plan/1/shown.json`(시각, 대화 기록 경로), `.task_planner/sessions/<세션 id>/runs/…` (단계 여섯 개 폴더, split_plan 의 calls/split 1~7, spec 1~6, edges 1)
- mock: `.mockData/personas.json`, `ids.json`, `plans/1.json`

발견
1. grilling 스킬을 실제로 불렀다 (목표 글 첫 줄을 고친 효과). 질문은 하나씩이 아니라 라운드로 여럿을 한 번에 묻는다 (grilling 스킬의 방식)
2. 대화 없이 띄운 세션에는 AskUserQuestion 이 없어, "정리할까요?"를 글로 물었다. 보통 Claude Code 에서는 선택 창이 뜬다
3. **show 지시의 글(계획 표)을 사용자에게 보이지 않고 바로 `next` 를 불렀다.** 마지막 말은 "위 계획 1은 확정이나 취소를 기다리고 있습니다"인데, 계획 표는 명령 결과(JSON)에만 있고 답변에 옮겨지지 않았다. run 스킬은 "payload.text 의 내용을 사용자에게 답변으로 알리고 next 를 부릅니다. 답변에 옮기지 않으면 사용자는 그 내용을 보지 못합니다"라고 적고 있다. 보통 Claude Code 에서도 같은지는 확인 전

