# 워크플로: list_plans

`/plan-go`, `/plan-cancel`, `/plan-run` 을 계획 id 없이 불렀을 때, 이 작업 폴더의 계획 목록(id, 제목, 상태)을 보이고 끝낸다 (사용자, 2026-11-19. workflow-confirm_plan.md 의 정할 것 2 번).
진행 방식은 make_plan 과 같다: 단계마다 계획 → 만들기 → 시험 → 단계 기록.

## 요청

"id 없이 부르면 고르는 분기를 두지 않고, 이 저장소의 계획 목록(id, 제목, 상태)을 보이고 'id 를 넣어 다시 불러 주세요'로 끝낸다" (사용자, 2026-11-19)
"`/plan-go` 명령 글이 흐름을 시작하기 전에 id 를 확인하고, 없으면 list_plans 흐름을 시작한다" (사용자, 2026-11-19)

## 흐름도                                  상태: 확답 (사용자, 2026-11-19)

```
list_plans
├─ collect_plans    [CODE]
└─ show_plans       [MAIN_SESSION_SHOW]
```

## 단계별 상세                             상태: 2 / 2 확답

### collect_plans
- 종류: CODE
- 결과 종류: DATA
- 입력: 없음
- 출력: → { plans: list[{plan_id: int, title: str, status: str}] }
- 상세
  - 하는 일: 이 작업 폴더의 `.plan/` 아래 폴더 이름으로 계획 id 를 얻고, 계획마다 계획 저장소에서 제목과 상태를 읽는다
  - 쓸 model·port: `DefaultPlanFolderReader().list_plan_ids()`, `plan_api_reader().get_plan(plan_id)`
  - 폴더는 있는데 계획 저장소에 없으면(mock 을 지운 경우 등) 제목 "(계획 저장소에 없음)", 상태 빈 글로 넣는다. 목록 보이기가 실패하지 않게 한다
- 다시 수행: 읽기만 하므로 안전
- 상태: 확답 (사용자, 2026-11-19)

### show_plans
- 종류: MAIN_SESSION_SHOW
- 결과 종류: DATA
- 입력: ← collect_plans.plans
- 출력: 없음
- 상세
  - 보일 글 (계획이 있을 때):
    ```text
    명령 뒤에 계획 id 를 넣어 다시 불러 주세요. 예: /plan-go 7

    | id | 제목 | 상태 |
    |---|---|---|
    | 7 | 검색 기능 설계 | 검토 중 |
    | 9 | 로그인 개편 | 승인 |
    ```
  - 보일 글 (계획이 없을 때): "이 작업 폴더에 계획이 없습니다. /task-planner:run make_plan 으로 계획을 만들어 주세요."
  - 상태는 한국어로 보인다: drafting 작성 중, reviewing 검토 중, approved 승인, rejected 불허, running 실행 중, done 끝남
- 상태: 확답 (사용자, 2026-11-19)

## 같이 쓰는 코드
- 없음

## 진행 기록

- list_plans: collect_plans_task.py, show_plans_task.py, plan_status_label.py, list_plans_flow.py, registry.py 한 줄, 시험 3개. 검증 통과 (pytest 94개)

## 단계 기록

### list_plans (만들기 전 계획, 2026-11-19)

1. 입력
   - 사용자: `/plan-go`(또는 `/plan-cancel`, `/plan-run`)를 id 없이 부름 → 그 명령의 스킬 글이 `task-planner start list_plans` 를 부른다 (명령 스킬은 다음 일)
   - collect_plans: 앞 단계 결과 없음. 작업 폴더의 `.plan/` 폴더 이름, 계획 저장소 (`plan_api_reader()`)
   - show_plans: `context.read("collect_plans")["plans"]` (선언의 `reads=("collect_plans",)`)
2. 출력
   - collect_plans 단계 결과: `{"plans": [{"plan_id": 7, "title": "검색 기능 설계", "status": "reviewing"}, ...]}` (id 작은 순)
   - show_plans: 메인 세션에 show 지시 → 메인 세션이 보이고 next → finished
3. 생길 파일 트리
   ```
   코드
   src/task_planner/workflow/list_plans/
   ├─ __init__.py
   ├─ list_plans_flow.py
   ├─ collect_plans/
   │  ├─ __init__.py
   │  └─ collect_plans_task.py
   └─ show_plans/
      ├─ __init__.py
      ├─ show_plans_task.py
      └─ plan_status_label.py          상태 → 한국어 (작성 중, 검토 중 …)
   src/task_planner/workflow/registry.py   FLOWS 에 "list_plans" 한 줄
   tests/workflow/test_list_plans.py

   실행하면 (작업 폴더)
   .task_planner/sessions/<세션 id>/runs/<실행 id>/
   ├─ collect_plans_<uuid8>/result.json
   └─ show_plans_<uuid8>/result.json
   ```
4. 프롬프트: 메인 세션에 넘기는 글은 위 "보일 글"이다. 보이는 방법은 run 스킬의 show 처리
5. 코드 (만들 모양)
   ```python
   @TASKS.register_as("list_plans.collect_plans")
   class CollectPlansTask(Task):
       request_type = CodeRequest
       output_kind = OutputKind.DATA

       def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
           # 작업 폴더의 계획 id 마다 계획 저장소에서 제목과 상태를 읽는다
           plan_ids = DefaultPlanFolderReader().list_plan_ids()
           return TaskOutput({"plans": [_plan_row(plan_id) for plan_id in plan_ids]})


   def _plan_row(plan_id: int) -> dict[str, Any]:
       """계획 하나의 id, 제목, 상태. 계획 저장소에 없으면 제목만 '(계획 저장소에 없음)'."""


   @TASKS.register_as("list_plans.show_plans")
   class ShowPlansTask(Task):
       request_type = ShowRequest
       output_kind = OutputKind.DATA

       def build_request(self, context: FlowContext) -> ShowRequest:
           # 계획이 있으면 다시 부르는 방법과 목록 표, 없으면 계획을 만드는 방법을 보인다
           return ShowRequest(build_plan_list_text(context.read("collect_plans")["plans"]))
   ```
6. 시험 (만들 것)
   - 계획 두 개(mock 계획 저장소 + 작업 폴더의 `.plan/<id>/`)를 만들어 두고 `start list_plans` → show 지시의 글에 두 계획의 id, 제목, 한국어 상태가 있음 → next → finished
   - 계획이 없으면 "이 작업 폴더에 계획이 없습니다" 글
   - 폴더는 있는데 계획 저장소에 없으면 "(계획 저장소에 없음)" 줄

### list_plans (만듦, 2026-11-19)

계획대로 만들었다. 위 "만들기 전 계획"의 1~3 과 같다.

5. 코드 전문
   - `collect_plans/collect_plans_task.py`
     ```python
"""collect_plans: 이 작업 폴더의 계획 id(.plan/ 폴더 이름)마다 계획 저장소에서 제목과 상태를 읽는다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.code_request import CodeRequest
from task_planner.port.local.plan_folder.default_plan_folder_reader import DefaultPlanFolderReader
from task_planner.port.plan_api.plan_api_choice import plan_api_reader
from task_planner.port.plan_api.plan_not_found_error import PlanNotFoundError

MISSING_TITLE = "(계획 저장소에 없음)"


@TASKS.register_as("list_plans.collect_plans")
class CollectPlansTask(Task):
    request_type = CodeRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> CodeRequest:
        return CodeRequest()

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        # 작업 폴더의 계획 id 마다 계획 저장소에서 제목과 상태를 읽는다 (id 작은 순)
        plan_ids = DefaultPlanFolderReader().list_plan_ids()
        return TaskOutput({"plans": [_plan_row(plan_id) for plan_id in plan_ids]})


def _plan_row(plan_id: int) -> dict[str, Any]:
    """계획 하나의 id, 제목, 상태. 계획 저장소에 없으면 제목만 '(계획 저장소에 없음)', 상태는 빈 글."""
    try:
        plan = plan_api_reader().get_plan(plan_id)
    except PlanNotFoundError:
        return {"plan_id": plan_id, "title": MISSING_TITLE, "status": ""}
    return {"plan_id": plan_id, "title": plan.title, "status": plan.status.value}
     ```
   - `show_plans/show_plans_task.py`
     ```python
"""show_plans: collect_plans 의 목록을 보이고, 명령 뒤에 계획 id 를 넣어 다시 부르라고 안내한다."""

from __future__ import annotations

from typing import Any

from task_planner.engine.definition.context.flow_context import FlowContext
from task_planner.engine.definition.task.output_kind import OutputKind
from task_planner.engine.definition.task.task import Task
from task_planner.engine.definition.task.task_output import TaskOutput
from task_planner.engine.registry.registries import TASKS
from task_planner.engine.request.show_request import ShowRequest
from task_planner.workflow.list_plans.show_plans.plan_status_label import status_label

# 계획서(specs/plans/workflow-list_plans.md) show_plans 의 보일 글 그대로
GUIDE = "명령 뒤에 계획 id 를 넣어 다시 불러 주세요. 예: /plan-go 7"
NO_PLANS = "이 작업 폴더에 계획이 없습니다. /task-planner:run make_plan 으로 계획을 만들어 주세요."


@TASKS.register_as("list_plans.show_plans")
class ShowPlansTask(Task):
    request_type = ShowRequest
    output_kind = OutputKind.DATA

    def build_request(self, context: FlowContext) -> ShowRequest:
        # 계획이 있으면 다시 부르는 방법과 목록 표, 없으면 계획을 만드는 방법을 보인다
        return ShowRequest(build_plan_list_text(context.read("collect_plans")["plans"]))

    def build_output(self, context: FlowContext, result: Any) -> TaskOutput:
        return TaskOutput({})


def build_plan_list_text(plans: list[dict[str, Any]]) -> str:
    if not plans:
        return NO_PLANS
    rows = ["| id | 제목 | 상태 |", "|---|---|---|"]
    rows += [f"| {plan['plan_id']} | {plan['title']} | {status_label(plan['status'])} |" for plan in plans]
    return GUIDE + "\n\n" + "\n".join(rows)
     ```
   - `list_plans_flow.py`
     ```python
"""list_plans 워크플로 선언. 계획서: specs/plans/workflow-list_plans.md

/plan-go, /plan-cancel, /plan-run 을 계획 id 없이 불렀을 때 이 작업 폴더의 계획 목록을 보이고 끝낸다.
"""

from __future__ import annotations

from task_planner.engine.definition.flow_definition import FlowDefinition
from task_planner.engine.definition.ref import Ref
from task_planner.engine.definition.unit.builders import group, task
from task_planner.engine.performer.performed_by import PerformedBy
from task_planner.engine.runner.child_run.child_run import ChildRun
from task_planner.workflow.list_plans.collect_plans import collect_plans_task  # noqa: F401
from task_planner.workflow.list_plans.show_plans import show_plans_task  # noqa: F401

LIST_PLANS_FLOW = FlowDefinition(
    name="list_plans",
    description="이 작업 폴더의 계획 목록(id, 제목, 상태)을 보이고, id 를 넣어 다시 부르라고 안내한다",
    root=group("list_plans", ChildRun.IN_ORDER,
        task("collect_plans", PerformedBy.CODE, Ref("list_plans.collect_plans")),
        task("show_plans", PerformedBy.MAIN_SESSION_SHOW, Ref("list_plans.show_plans"), reads=("collect_plans",))),
)  # fmt: skip
     ```
6. 검증: ruff, import 검사 계약 4개, mypy, pytest 94개 통과. 새 시험 3개: 계획 두 개의 목록과 한국어 상태 → next → finished, 계획이 없을 때 글, 폴더만 있고 계획 저장소에 없을 때 "(계획 저장소에 없음)"
7. 실제 실행 (CLI, Claude Code 끝까지 시험의 작업 폴더 tpm-try2, 실제 `.mockData`)
   ```text
   명령 뒤에 계획 id 를 넣어 다시 불러 주세요. 예: /plan-go 7

   | id | 제목 | 상태 |
   |---|---|---|
   | 1 | 파이썬 할 일 목록 관리 CLI 도구(todo) 만들기 | 검토 중 |
   ```
   next → finished. 실행 폴더에 collect_plans_…, show_plans_… 가 생김

