# C: 병합할 지식을 비슷한 지식 10개 가운데 고르기

C(refine_each)의 고르기를 두 단계로 나눈다. 먼저 "병합하시겠습니까?"를 묻고, 병합이면 비슷한 지식 10개 가운데 대상을 세 개씩 넘겨 보며 고른다.
진행 방식: 계획 → 만들기 → 시험 → 별도 에이전트 리뷰 → 단계 기록. 상태: 만듦 (사용자, 2026-11-19: "커밋하고 단계 수행". 9 절 확인할 것은 적은 대로 진행).

## 요청

- "각 생성된 요소로 이제 검색을 수행 하는데, 검색을 해서 유사도 유사한 것 (검색 로직은 이제 나중에 선택할 것임, 우선은 검색이라는게 있다~ 정도의 mock 으로) 10 개중 선택하기. 병합 하시겠습니까? 이렇게 나오게 하는게 어떨까?" (사용자, 2026-11-19)
- 10개 가운데 고르는 방식: "다음 3개 보기 로 넘겨 보기" (사용자, 2026-11-19)
- "기존 구조를 어떻게 추가하거나 수정해야 할지, 소스는 어떻게 최소 스펙으로 관리할지" (사용자, 2026-11-19)

## 1. 입력과 받는 방식

- 그대로: `/plan-go <id>`, `/plan-cancel <id>`. 바뀌는 것은 C 안의 질문뿐이다.
- 기존 지식 찾기(`find_existing`)는 그대로 10개를 찾는다. 같은 종류만 찾는 것도 그대로다. 종류를 넘어 병합하는 일은 사용자가 따로 생각하기로 했다 (2026-11-19).

## 2. 출력 (보이는 모습)

병합할지 묻기 (`choose_action`)
```text
지식 후보 1/2: [도메인] 테이블 설계
기존 서비스가 FK 를 걸지 않으면 새 테이블에도 FK 를 걸지 않는다.
근거: "fk 걸지 마, 우리 서비스는 안 걸어"

비슷한 지식 10개
 1. #2 테이블 설계 — 배열은 별도 테이블로 둔다. FK 는 기존 서비스가 걸고 있을 때만 건다.
 2. #1 테이블 설계 — 최소 스펙부터, 꼭 필요한 스펙만 나열한다. 기존 구조에 테이블을 추가한다면…
 ...
10. #9 API 설계 — …

병합하시겠습니까?
선택지: 병합 / 새 지식으로 저장 / 넣지 않기
```
- 비슷한 지식이 없으면 목록 대신 "비슷한 지식이 없습니다." 를 쓰고, 선택지는 `새 지식으로 저장 / 넣지 않기` 둘이다.

병합할 지식 고르기 (`choose_target_1` ~ `choose_target_3`, 병합을 골랐을 때만)
```text
어느 지식에 병합할까요? (1~3 / 10)
선택지: #2 테이블 설계 / #1 테이블 설계 / #5 테이블 설계 / 다음 3개 보기

어느 지식에 병합할까요? (4~6 / 10)
선택지: #7 … / #3 … / #8 … / 다음 3개 보기

어느 지식에 병합할까요? (7~10 / 10)
선택지: #4 … / #6 … / #9 … / #10 …
```
- 선택 창에는 선택지가 2~4개 들어간다. 그래서 한 쪽에 셋과 "다음 3개 보기"를 두고, 남은 것이 넷 이하가 되면 마지막 쪽에 다 보인다. 10개면 3 / 3 / 4 로 세 쪽이다.
- 비슷한 지식이 하나뿐이면 선택지가 하나가 되어 선택 창을 띄울 수 없다. 이때는 `#2 테이블 설계 / 새 지식으로 저장` 으로 묻는다.
- 본문은 첫 질문의 목록에서 보이므로, 고르기 선택지에는 id 와 작업 이름만 쓴다.

## 3. 데이터

단계 결과 (result.json, 항목 번호별)
```jsonc
// choose_action
{"answer": "병합"}                                   // 병합 | 새 지식으로 저장 | 넣지 않기
// choose_target_1 (다음을 골랐을 때)
{"answer": "다음 3개 보기", "memory_id": null}
// choose_target_2 (지식을 골랐을 때)
{"answer": "#7 API 설계", "memory_id": 7}
```
- 고르지 않은 쪽은 건너뜀(SKIPPED)으로 남고 결과가 없다.
- 저장 데이터와 API 는 바뀌지 않는다. 병합은 지금의 덧붙이기(POST /memories/{id}/append)다.

## 4. 흐름도

as-is
```
refine_each            [FOR_EACH_ITEM: extract_knowledge.candidates]
├─ find_existing       [CODE]
├─ choose_action       [MAIN_SESSION_ASK]   새로 / 덧붙이기: 기존 두 개 / 넣지 않기
└─ keep_each           [IN_ORDER] [run_if: confirm_plan.keeps_candidate]
   ├─ write_knowledge    [CLAUDE_P]
   ├─ review_knowledge   [MAIN_SESSION_TALK]
   ├─ finalize_knowledge [CLAUDE_P]
   └─ save_knowledge     [CODE]
```

to-be
```
refine_each            [FOR_EACH_ITEM: extract_knowledge.candidates]
├─ find_existing       [CODE]
├─ choose_action       [MAIN_SESSION_ASK]   병합 / 새로 / 넣지 않기 (질문 글에 비슷한 지식 10개)
├─ choose_target       [IN_ORDER] [run_if: answer_is(choose_action, "병합")]
│  ├─ choose_target_1  [MAIN_SESSION_ASK]   1~3
│  ├─ choose_target_2  [MAIN_SESSION_ASK]   4~6   [run_if: answer_is(choose_target_1, "다음 3개 보기")]
│  └─ choose_target_3  [MAIN_SESSION_ASK]   7~10  [run_if: answer_is(choose_target_2, "다음 3개 보기")]
└─ keep_each           [IN_ORDER] [run_if: confirm_plan.keeps_candidate]   (그대로)
   ├─ write_knowledge    [CLAUDE_P]          병합 대상을 읽는 곳만 바뀜
   ├─ review_knowledge   [MAIN_SESSION_TALK] 병합 대상을 읽는 곳만 바뀜
   ├─ finalize_knowledge [CLAUDE_P]          (그대로)
   └─ save_knowledge     [CODE]              병합 대상을 읽는 곳만 바뀜
```

engine 은 바꾸지 않는다.
- 세 쪽은 단계 셋으로 선언한다. 같은 클래스 하나를 쪽 번호만 바꿔 등록 키 인자로 넘긴다. `record_decision` 이 결정 값을 받는 것과 같은 방식이다.
- 다음 쪽을 열지는 engine 의 기본 조건 `answer_is` 로 정한다. 앞 쪽을 건너뛰었으면 거짓이라, 앞에서 고른 뒤에는 뒤 쪽이 모두 건너뛰어진다.
- 따져 본 다른 안이 있다. engine 의 "답을 받지 않음"(`ReplyRejectedError`)에 새 질문을 실어, 같은 단계에서 쪽을 바꾸는 안이다. 단계가 하나로 끝나지만 engine 사본을 또 고쳐야 해서 택하지 않았다.

## 5. 파일 트리

```
src/task_planner/workflow/confirm_plan/
├─ confirm_plan_flows.py                         choose_target 묶음을 더함, keep_each 단계의 reads 에 고르기 단계들
└─ refine_each/
   ├─ choose_action/
   │  ├─ choose_action_task.py                   질문 글: 비슷한 지식 10개 목록 (한 줄씩)
   │  └─ action_choices.py                       선택지: 병합 / 새로 / 넣지 않기. 덧붙이기 선택지와 id 읽기는 뺌
   └─ choose_target/                             새로
      ├─ __init__.py
      ├─ choose_target_task.py                   쪽 하나의 질문과 답 읽기
      ├─ target_pages.py                         10개를 쪽으로 나누기 (3 / 3 / 4)
      └─ merge_target.py                         병합 대상 id 읽기 (뒤 단계 셋이 같이 씀), 고르기 단계 이름 목록
   └─ keep_each/
      ├─ write_knowledge/write_knowledge_task.py     append_target_id(…) → merge_target_id(context)
      ├─ review_knowledge/review_knowledge_task.py   같음
      └─ save_knowledge/save_knowledge_task.py       같음
tests/workflow/confirm_plan/test_refine_each.py  시험을 고치고 더함
```

## 6. 프롬프트

없음. 바뀌는 것은 질문 글과 선택지다 (2 절).

## 7. 코드 요지

`target_pages.py`
```python
PAGE_SIZE = 3  # 한 쪽에 보일 지식 수. 넷째 자리는 "다음 3개 보기"
NEXT_PAGE = "다음 3개 보기"


def page_of(existing: list[dict], page: int) -> list[dict]:
    """page 쪽(1부터)에 보일 지식. 남은 것이 넷 이하면 그 쪽에 다 보인다."""
    start = (page - 1) * PAGE_SIZE
    rest = existing[start:]
    return rest if len(rest) <= PAGE_SIZE + 1 else rest[:PAGE_SIZE]


def has_next(existing: list[dict], page: int) -> bool:
    return len(existing) - (page - 1) * PAGE_SIZE > PAGE_SIZE + 1
```

`choose_target_task.py`
```python
@TASKS.register_as("confirm_plan.choose_target")
class ChooseTargetTask(Task):
    """병합할 지식을 쪽 하나에서 고른다. 다음 쪽이 있으면 넷째 선택지가 "다음 3개 보기"다."""
    request_type = QuestionRequest
    output_kind = OutputKind.DATA

    def __init__(self, page: int) -> None:
        self.page = page

    def build_request(self, context): ...      # 질문 "어느 지식에 병합할까요? (4~6 / 10)", 선택지 _choices(...)
    def build_output(self, context, result):   # 선택지 밖이면 ReplyRejectedError, 아니면 {"answer", "memory_id"}
```
- 선택지 이름은 `#<id> <작업 이름>`. 답에서 id 를 읽는다.
- 한 쪽에 지식이 하나뿐이고 다음 쪽이 없으면 `새 지식으로 저장` 을 더한다. 이 답의 `memory_id` 는 null 이고, 뒤 단계는 새로 저장으로 다룬다.

`merge_target.py`
```python
TARGET_PAGES = ("choose_target_1", "choose_target_2", "choose_target_3")


def merge_target_id(context: FlowContext) -> int | None:
    """고른 병합 대상의 id. 병합이 아니거나 새로 저장을 골랐으면 None."""
    for node_name in TARGET_PAGES:
        try:
            memory_id = context.read(node_name)["memory_id"]
        except OutputMissingError:  # 건너뛴 쪽
            continue
        if memory_id is not None:
            return int(memory_id)
    return None
```
- 뒤 단계 셋(write, review, save)은 지금 `append_target_id(context.read("choose_action")["answer"])` 를 부르는 줄만 `merge_target_id(context)` 로 바꾼다. 선언의 reads 에는 `*TARGET_PAGES` 를 넣는다.
- `keeps_candidate`(넣지 않기가 아니면 계속)는 그대로 둔다.

선언 (`confirm_plan_flows.py` 의 `_refine_each`)
```python
choose_target = group("choose_target", ChildRun.IN_ORDER,
    task("choose_target_1", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_target", {"page": 1}),
         reads=("find_existing",)),
    task("choose_target_2", PerformedBy.MAIN_SESSION_ASK, Ref("confirm_plan.choose_target", {"page": 2}),
         reads=("find_existing", "choose_target_1"),
         run_if=Ref("answer_is", {"node_name": "choose_target_1", "value": NEXT_PAGE})),
    task("choose_target_3", ...  page 3, choose_target_2 를 보고),
    run_if=Ref("answer_is", {"node_name": "choose_action", "value": MERGE}), reads=("choose_action",))  # fmt: skip
```

## 8. 시험

가짜 claude 로 CLI 를 끝까지 돈다 (`test_refine_each.py`). mock 지식은 10개를 둔다.
1. 병합 → 첫 쪽에서 #2 → #2 에 덧붙여짐. 2·3 쪽은 건너뜀
2. 병합 → 다음 → 다음 → 셋째 쪽에서 #10 → #10 에 덧붙여짐. 셋째 쪽 선택지는 4개이고 "다음"이 없음
3. 새 지식으로 저장 → 고르기 단계 셋 모두 건너뜀, 새 지식 하나
4. 넣지 않기 → 고르기와 keep_each 모두 건너뜀
5. 비슷한 지식이 없음 → 선택지 둘(새로 / 넣지 않기), 질문 글에 "비슷한 지식이 없습니다."
6. 비슷한 지식이 하나 → 고르기 선택지가 `#1 … / 새 지식으로 저장`. 새로 저장을 고르면 새 지식
7. 쪽 나누기 함수: 10 → 3/3/4, 5 → 3/2, 4 → 4, 1 → 1

실제 Claude Code(e2e)에서 `/plan-go` 를 한 번 돌려, 선택 창이 쪽마다 나오는지 본다.

## 9. 확인할 것

1. 첫 질문 목록의 본문 길이: 한 줄에 80자까지 (지금은 두 개를 200자까지 보인다)
2. 비슷한 지식이 하나뿐일 때 `새 지식으로 저장` 을 더하는 것 (2 절)
3. 마지막 쪽에서 되돌아가기("처음 3개 보기")는 두지 않는다. 고르지 않으려면 선택 창의 직접 입력으로 다른 말을 쓰면 같은 질문이 다시 나온다
4. 종류를 넘는 병합은 이번 범위 밖 (1 절)

## 진행 기록

- 2026-11-19 만듦. 계획과 다른 점: engine 이 한 흐름에서 같은 등록 키를 두 번 쓰지 못하게 해서(`check_definition.py`), 고르기 클래스 하나를 `confirm_plan.choose_target_1`~`_3` 세 키로 등록했다. 쪽 번호는 지금처럼 등록 키 인자로 넘긴다.
- 확인 대화의 첫 말은 "(#2 에 덧붙이기)" 그대로 두었다. "병합"으로 맞출지는 사용자 판단 (문구 바꿈).
- 시험: test_refine_each.py 12개 (병합·새로·넣지 않기, 세 쪽 넘겨 마지막 쪽에서 고르기, 첫 쪽에서 고르면 뒤 쪽 건너뜀, 비슷한 지식 없음, 하나뿐, 쪽 나누기 4가지). 전체 pytest 146개, ruff, mypy, lint-imports 통과

## 단계 기록

1. 입력: 그대로 (`/plan-go`, `/plan-cancel`). 기존 지식 찾기도 같은 종류 10개 그대로.
2. 출력: 후보마다 "병합하시겠습니까?" (병합 / 새로 / 넣지 않기, 질문 글에 비슷한 지식 10개). 병합이면 쪽마다 대상 고르기 (3 / 3 / 4, "다음 3개 보기").
3. 파일: `choose_target/` 새로 (choose_target_task, target_pages, merge_target). choose_action 두 파일, 흐름 선언, 본문 쓰기·확인 대화·저장 단계의 한 줄씩, find_existing 의 상한 자르기, 시험.
4. 별도 에이전트 리뷰: (1) 검색 결과가 10개를 넘으면 셋째 쪽에도 "다음"이 붙고, 고르면 넷째 쪽이 없어 병합이 새로 저장으로 바뀜 → 찾기 결과를 상한으로 자르고, 상한과 쪽 수가 맞는지 보는 시험을 둠. 쓰지 않는 PAGE_COUNT 를 뺌. (2) 이 변경 전에 시작해 멈춘 plan_go 실행은 이어 가면 실패함 (실행 상태에 옛 단계 목록이 남음) → 코드는 그대로, 반영 전에 진행 중인 실행을 끝내거나 취소. (3) 병합 대상을 읽는 단계의 reads 에 쓰지 않는 choose_action 이 들어감 → 뺌.
5. 남은 것: 실제 Claude Code 에서 쪽 넘기기 확인 (e2e), 확인 대화 첫 말의 "덧붙이기"를 "병합"으로 맞출지 (사용자 판단).

## C 마무리 조건

이 단위를 만들고 시험·리뷰·e2e 한 번을 통과하면 C 는 끝낸다. 남는 것은 서버 검색(검색 로직 선택)과 종류를 넘는 병합이고, 둘 다 사용자가 따로 정한다.
