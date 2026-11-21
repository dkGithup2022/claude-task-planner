# 계획: 지식 검색을 CLI 흐름에 연결 (나누기 판단, 작업 지시, 기존 지식 찾기)

## 0. 정한 것 (사용자, 2026-11-21)

- 검색어는 가중치 없이 글 하나 (`MemorySearchQuery.query: str`). 서버 API 는 바꾸지 않는다
- 검색은 `limit` 기본값 10 개를 받고, 쓰는 곳에서 잘라 쓴다
- 쓰는 곳마다 검색어를 만드는 함수 `build_search_word(...) -> str` 를 둔다

| 쓰는 곳 | 검색어 | 지식 종류 | 페르소나 | 넣는 지식 |
|---|---|---|---|---|
| 계획 만들기: 나누기 판단 | 작업 이름 + 하는 일 | plan | 계획의 참여 페르소나 | 검색 10 개 → 하이쿠가 관계있는 것만 최대 5 개 |
| 계획 실행: 작업 지시 만들기 | 노드 제목 + 산출물 스펙 (머리 줄 `###` 뺌) | knowledge, attitude (한 번씩) | 노드의 담당 페르소나 | 종류마다 앞 5 개 (생성기 프롬프트가 스스로 고른다) |
| 계획 확정: 기존 지식 찾기 | 후보의 작업 이름 + 내용 (지금 그대로) | plan 또는 knowledge | 계획의 참여 페르소나 | 10 개 (지금 그대로) |

- 지식은 본문 전체(덧붙임 포함)를 넣는다. 자르지 않는다
- 하이쿠 거르기: "실제 작업" 과 "컨텍스트" (최대 10 개) 를 받아 관계있는 컨텍스트의 id 를 중요한 순서로 최대 5 개. 없으면 빈 목록
- 하이쿠 호출이 실패하면 검색 순서대로 앞 5 개를 쓰고 경고를 남긴다
- 검색이 실패하면 (서버가 꺼짐 등) 검색 결과 자리에 "(검색 실패)" 를 넣고 경고를 남긴 뒤 계속한다
- 나누기 판단은 plan 종류만 찾는다. 검색과 거르기는 `_judge_layer` 의 `judge` 안에서 하고, `build_split_input` 에는 고른 지식만 넘긴다
- 확인 노드(HITL)는 담당 페르소나가 없어 찾지 않는다 (지금처럼 "(없음)")

## 1. 공통 로직의 자리

번들 규칙: 다른 워크플로 폴더의 코드를 import 하지 않는다 (tool-add-code-task 4 절). 층 규칙: port 는 claude_utils 를 쓰지 못하고, claude_utils 와 model 은 프로젝트 코드를 쓰지 못한다.
그래서 "검색 → 하이쿠 거르기" 를 통째로 한 곳에 둘 수 있는 층은 workflow 뿐인데, workflow 끼리는 서로 import 하지 않는다.

나눠서 둔다.

| 부분 | 자리 | 이유 |
|---|---|---|
| 검색 | `port/memory_api/` (이미 있음) | 바깥 API |
| 하이쿠 거르기 (프롬프트, 호출, id 정리) | `claude_utils/search_utils/` (새 폴더, 이름은 사용자 2026-11-21) | 검색 결과를 다루는 Claude 호출이고 지식·계획을 몰라도 된다. "실제 작업" 과 "컨텍스트(id, 제목, 본문)" 만 받는다 |
| 검색어 만들기, 연결 (검색 → 거르기 → 실패 처리 → 프롬프트 글) | 흐름마다 그 단계 폴더 | 흐름마다 재료가 다르다 |

흐름마다 반복되는 것은 연결 함수 하나 (10~20 줄) 뿐이다.

- claude_utils 에는 새 파일만 더한다 (처음부터 있는 파일은 고치지 않는다). claude_utils 를 더하는 번들 스킬은 따로 없어 tool-add-common 의 방식(새 파일만, 파일 하나에 한 가지 일)을 따른다

## 2. 단계

### 2-1. 하이쿠 거르기 (`claude_utils/search_utils/`, 새 폴더)

```
claude_utils/search_utils/
├─ context_item.py                          # ContextItem(context_id, title, body)
├─ prompt_relevant_context.md               # 프롬프트 (아래)
├─ prompt_relevant_context_output.py        # RelevantContextOutput(ids: list[int])
└─ pick_relevant_contexts.py                # RELEVANT_CONTEXT (PromptSpec, model="haiku"), pick_relevant_contexts, relevant_context_input, kept_ids
```

```python
MAX_RELEVANT = 5


def pick_relevant_contexts(
    task_md: str, items: Sequence[ContextItem], caller: PromptCaller = call_prompt
) -> tuple[tuple[int, ...], PromptCallRecord]:
    """items 가운데 실제 작업과 관계있는 것의 id 를 하이쿠가 고른 중요한 순서로 최대 5 개, 그리고 호출 기록.

    items 에 없는 id 와 겹친 id 는 버린다. 호출이 실패하면 PromptCallError (부르는 쪽이 정한다).
    """
```

- `PromptCaller` 는 지금 `workflow/make_plan/split_plan/prompt_caller.py` 에 있어 claude_utils 가 쓸 수 없다. claude_utils 안에 같은 모양의 타입을 둔다 (`Callable[[PromptSpec, str], tuple[Any, PromptCallRecord]]`)
- 입력 글

```
# 실제 작업
<task_md>

# 컨텍스트
## id 5: 문서 작성 계획
<본문 전체>

## id 7: 서비스 설계 문서 작성
<본문 전체>
```

- 프롬프트 (`prompt_relevant_context.md`)

```
당신은 아래의 "실제 작업"과 "컨텍스트"를 받아서, 실제 작업과 관계있는 컨텍스트의 id 를 반환한다.

관계있는 컨텍스트
- 실제 작업과 같은 분야의 지식. 예: 실제 작업이 UI/UX 화면 설계면 UI/UX 작업에 대한 지식
- 비슷한 계획을 어떻게 나눴는지에 대한 이전 내용

관계없는 컨텍스트
- 다른 분야만 다루는 지식. 예: 실제 작업이 UI/UX 화면 설계인데 DB 테이블 설계만 다루는 지식

컨텍스트는 최대 10 개 들어온다. 관계있는 것을 최대 5 개, 중요한 순서대로 반환한다.
관계있는 것이 없으면 빈 목록을 반환한다. 5 개를 채우려고 관계없는 것을 넣지 않는다.
```

- 시험: 입력 글 모양, 없는 id·겹친 id 버리기, 5 개 넘으면 자르기, 빈 목록 (가짜 caller)

### 2-2. 계획 만들기: 나누기 판단 (`workflow/make_plan/split_plan/`)

- `split_plan_task.py`: `split_tree(plan.title, plan.request, plan.persona_ids, call_log)`
- `split_tree/split_tree.py`
  - as-is: `split_tree(title, request_md, call_log, caller=call_prompt)`, `_judge_layer(tree, frontier, request_md, call_log, caller)`, `build_split_input(tree, work_item, request_md)`
  - to-be: `split_tree(title, request_md, persona_ids, call_log, caller=call_prompt)`, `_judge_layer(tree, frontier, request_md, persona_ids, call_log, caller)`, `build_split_input(tree, work_item, request_md, knowledge_md)`
  - `judge` 안에서 `relevant_plan_knowledge(...)` 로 지식을 찾고 거른 뒤, 그 글을 `build_split_input` 에 넘긴다. 경고는 판단 결과와 함께 돌려 `SplitResult.warnings` 에 모은다
  - as-is: `"# 검색 결과\n없음 (지식 검색은 아직 연결하지 않았습니다)"`
  - to-be: `"# 검색 결과\n" + knowledge_md` (고른 지식이 없으면 "없음", 검색이 실패하면 "(검색 실패)")
- `split_tree/search_word.py` (새): `build_search_word(work_item) -> str` = `f"{work_item.name} {work_item.scope}"`
- `split_tree/relevant_plan_knowledge.py` (새): 검색(plan, 10 개) → `pick_relevant_contexts` (실제 작업: 계획 제목, 작업 이름, 하는 일) → 호출 기록 `call_log.save("relevant_context", record)` → 고른 지식의 원문 글. 검색 실패, 하이쿠 실패는 0 절에 정한 대로
- 고른 지식의 글: 지식마다 `## <작업 이름> (지식 <id>)` 와 본문 전체
- `split_tree/prompt_split.md:11`
  - as-is: `- 검색 결과: 이 작업으로 검색한 이전 plan과 지식 기록 (각각 상위 10개). 입력 맨 아래에 옵니다. 없으면 "없음"`
  - to-be: `- 검색 결과: 이 작업으로 검색한, 작업을 나누는 방식의 지식 (상위 5개). 입력 맨 아래에 옵니다. 없으면 "없음"`
- 시험 `tests/workflow/make_plan/test_split_tree.py`
  - 세 곳(38·55·66 행)의 `split_tree` 호출에 페르소나 인자를 더한다
  - 가짜 caller 가 `spec.name` 을 보고 나누기 결과와 거르기 결과를 따로 돌려준다
  - 더하는 시험: 고른 지식이 나누기 입력에 들어간다, 검색 실패면 "(검색 실패)" 와 경고, 하이쿠 실패면 검색 앞 5 개와 경고

### 2-3. 계획 실행: 작업 지시 만들기 (`workflow/plan_run/prompts/write_prompts/`)

- `search_word.py` (새): `build_search_word(node) -> str` = 제목 + 산출물 스펙에서 `#` 로 시작하는 줄을 뺀 것
- `node_knowledge.py` (새): 노드의 담당 페르소나로 knowledge, attitude 를 한 번씩 찾아 종류마다 앞 5 개의 글. 확인 노드이거나 담당이 없으면 "(없음)". 검색이 실패하면 "(검색 실패)"
- `write_node_prompts.py` 의 `_make_one` 이 `node_knowledge` 를 불러 `node_prompt_input` 에 넘긴다
- `node_prompt_input.py`
  - as-is: `node_prompt_input(command_md, plan, node, personas)`, 끝 절 `NO_KNOWLEDGE` ("(없음)")
  - to-be: `node_prompt_input(command_md, plan, node, personas, knowledge_md)`, 끝 절에 `knowledge_md`. `NO_KNOWLEDGE` 상수와 주석("지식 검색이 mock 인 동안")은 지운다
- 경고: 검색 실패를 만든 것(`made`) 항목에 `"warning"` 으로 남긴다
- 시험: 검색어 (머리 줄 뺌), 확인 노드는 찾지 않음, 두 종류를 찾아 입력에 들어감, 검색 실패

### 2-4. 계획 확정: 기존 지식 찾기 (`workflow/confirm_plan/refine_each/find_existing/`)

- `search_word.py` (새): `build_search_word(candidate) -> str` = `f"{candidate['theme']} {candidate['content']}"`
- `find_existing_task.py`: as-is `query=f"{candidate['theme']} {candidate['content']}"` → to-be `query=build_search_word(candidate)`. 동작 같음

### 2-5. 도식 (corbina/notes, git 밖)

- `2026-11-18-flow-diagrams.md` 170 행 (차례도): "읽음: 지식 검색 (작업 이름과 범위)" 다음에 "하이쿠로 거르기 (관계있는 것만 최대 5 개)" 를 더한다
- 같은 파일 253 행 (흐름도): `K4{{"지식 검색: 연결 안 함 (입력에 없음)"}}` → 지식 검색(10 개) → 하이쿠 거르기(최대 5 개) → 나눌지 판단
- 213 행 "나누기 안의 지식 검색은 연결하지 않았다" 는 연결했다로 고친다
- `python3 build_re_code.py`

## 3. 검증

- `uv run ruff check . && uv run ruff format --check . && uv run lint-imports && uv run mypy && uv run pytest -q`
- 서버로 한 번: `TASK_PLAN_MANAGER_API=server` 로 작은 계획 하나를 만들어, 나누기 판단의 호출 기록(`calls/`)에서 거르기 입력·출력과 나누기 입력의 검색 결과 절을 확인한다
- 별도 에이전트 리뷰

## 4. 진행 기록

### 2-1 하이쿠 거르기 (2026-11-21)
- 새 파일: `claude_utils/search_utils/__init__.py`, `context_item.py`, `prompt_relevant_context.md` (계획의 문구 그대로), `prompt_relevant_context_output.py`, `pick_relevant_contexts.py`
- `PromptCaller` 는 `pick_relevant_contexts.py` 안에 같은 모양으로 둠 (폴더 트리에 파일을 더하지 않으려고)
- 시험 `tests/claude_utils/test_pick_relevant_contexts.py` 4 개: 입력 글 모양과 모델 haiku, 없는 id·겹친 id 버리기, 5 개로 자르기, 빈 목록

### 2-2 나누기 판단 (2026-11-21)
- 새 파일: `split_tree/search_word.py`, `split_tree/relevant_plan_knowledge.py`
- 고친 파일: `split_tree/split_tree.py` (페르소나를 받아 `judge` 안에서 찾고 거름, 경고를 `SplitResult.warnings` 에 모음. 계획 제목은 트리의 맨 위 작업 이름), `split_plan_task.py`, `split_tree/prompt_split.md:11` (계획의 to-be 문구)
- `relevant_plan_knowledge` 는 (검색 결과 절의 글, 경고) 를 돌려준다. 검색 결과가 비면 하이쿠를 부르지 않고 "없음"
- 시험 `tests/workflow/make_plan/test_split_tree.py`: 기존 3 개는 페르소나 인자만 더함 (기대값 그대로). 가짜 caller 가 `spec.name` 으로 거르기 호출을 따로 답함. 더한 시험 3 개: 고른 지식이 들어감, 검색 실패, 하이쿠 실패
- `tests/workflow/test_make_plan.py` 의 가짜 claude 에 거르기 호출의 답(`{"ids": []}`)을 더함. 없으면 하이쿠 실패 경고가 생겨 기존 기대값(`warnings: []`)과 달라진다. 기대값은 그대로

### 2-3 작업 지시 만들기 (2026-11-21)
- 새 파일: `write_prompts/search_word.py`, `write_prompts/node_knowledge.py`
- 고친 파일: `node_prompt_input.py` (knowledge_md 인자, `NO_KNOWLEDGE` 지움), `write_node_prompts.py` (`_make_one` 이 `node_knowledge` 를 부르고 경고를 돌려줌, 만든 것 항목에 검색이 실패했을 때만 `warning`), `workflow/plan_run/README.md` 51 행 (출력 모양에 warning)
- 지식 글: 지식마다 `## <작업 이름> (<작업 지식|태도>, 지식 <id>)` 와 본문 전체
- 시험 `tests/workflow/plan_run/test_node_knowledge.py` 5 개: 검색어(머리 줄 뺌), 두 종류와 종류마다 앞 5 개, 확인 노드는 찾지 않음, 없으면 "(없음)", 검색 실패

### 2-4 기존 지식 찾기 (2026-11-21)
- 새 파일 `find_existing/search_word.py`, `find_existing_task.py` 의 검색어 한 줄. 동작 같음

### 2-5 도식 (2026-11-21)
- `corbina/notes/2026-11-18-flow-diagrams.md`: 차례도에 "하이쿠로 거르기", "고른 지식 id" 두 줄, 바뀐 점의 "연결하지 않았다" 를 연결했다로, 흐름도 `K4` 를 지식 검색 → 하이쿠 거르기 → 나눌지 판단으로. `re_code.html` 다시 만듦

### 3 검증 (2026-11-21)
- ruff check 통과, lint-imports 4 kept, mypy 514 파일 문제 없음, pytest 294 passed
- ruff format --check: `specs/plans/workflow-plan_run.md` 하나만 걸림. 이 문서 안의 파이썬 코드 블록 정렬이고, 이번에 고치지 않은 파일이다 (저장소를 합친 커밋 2df4580 부터 그대로)
- 서버로 한 번 (개발 서버, 벡터 꺼짐, 맨 위 작업만 판단하도록 깊이 상한 1): 거르기 입력에 지식 7, 6, 5, 3 이 들어가고 하이쿠(9.09 초, $0.0007)가 `{"ids": [7, 6, 5]}` 를 돌려줌. 나누기 입력의 검색 결과 절에 지식 7, 6, 5 의 원문이 들어가고, 나누기(opus, 12.28 초, $0.094)가 지식 7 과 5 를 근거로 적음
- 검색 실패 (닫힌 포트): 검색 결과 절이 "(검색 실패)", 경고 "서비스 설계 문서 작성: 지식 검색 실패 (POST http://localhost:8099/api/memories/search 에 연결하지 못함: …)", 나누기는 그대로 불림
- 별도 에이전트 리뷰: 아직


### 리뷰 반영 (사용자 2026-11-21)
- 서버가 연결을 받은 뒤 응답 없이 끊으면 (서버 재시작 등) `RemoteDisconnected`, `ConnectionResetError` 가 `request_json` 밖으로 그대로 나와 "(검색 실패)" 로 넘어가지 않고 단계가 멈췄다. `common/http/http_json.py` 에 `except (http.client.HTTPException, OSError)` 절을 맨 뒤에 더해 `HttpJsonError` ("의 응답을 받지 못함") 로 바꾼다. 왜 있는지 주석을 둔다. 시험 `tests/common/test_http_json.py` (고치기 전 코드에서는 `ConnectionResetError` 로 실패함을 확인)
- 검색 결과가 비면 하이쿠를 부르지 않는 분기의 시험 `test_should_not_call_picking_when_search_finds_nothing` (그 분기를 지우면 실패함을 확인)
- `workflow/plan_run/README.md:53` 의 생성기 입력 설명을 "담당 페르소나로 검색한 작업 지식과 태도 각 5 개" 로
- 검증: ruff check, lint-imports (4 kept), mypy 통과, pytest 296 passed. `ruff format --check` 는 이번에 손대지 않은 `specs/plans/workflow-plan_run.md` 하나만 걸림 (저장소를 합친 커밋부터 그대로)
