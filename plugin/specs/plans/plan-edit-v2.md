# 계획 고치기 v2: 간선을 LLM 으로 다시 정하기, 새 노드의 정의서

노드를 나누거나 넣는 등 계획의 구조가 바뀌면, 바뀐 노드와 그 앞뒤 노드 사이의 간선을 LLM(claude -p)이 정의서를 읽고 다시 정한다. 계획을 처음 만들 때의 간선 정리도 같은 프롬프트를 쓴다. 대화로 새로 만드는 노드는 make_plan 과 같은 칸의 정의서를 대략 적게 한다.
진행 방식: dk-claude-tool-bundle 절차 (tool-planner 평가 → 계획 확인 → 제작) → 시험 → 별도 에이전트 리뷰 → 단계 기록. 상태: 프롬프트·스킬 글 검수 받음 (예시 1 의 34 → 43 은 뺌, 사용자 2026-11-19), 평가 확인 받음 (출력 칸은 from_id / to_id, 사용자 2026-11-19).

## 요청과 정한 것 (사용자, 2026-11-19)

- "1. plan-edit 이후에 간선 정리 2. split 이후 간선 정리 3. split 된 노드의 정의서 스펙"
- "split 단계에서 우리 정의서를 대략적으로 적을 수 있게 해야 겠는데"
- "규칙으로는 안되겠다. llm 으로 … 이전 단계의 결과가 필요한 노드가 후행하면 의미를 보고 이어 버리는 것으로"
- "plan edit, 이랑 계획 과정에서 노드 나뉘는 과정 두 과정 모두, 노드의 배치/스플릿의 변화가 생기면 변화 대상들 + 앞뒤 노드를 인자로 가져와서 edge 정보를 다시 배치하는 llm 콜"
- 인자: 나뉘거나 바뀐 노드(나뉜 경우 나뉜 전체), 이전의 관계, 바뀐 것의 선행·후행 노드(한 단계만). 출력: 간선 정보, 이걸로 간선을 바꾼다. 프롬프트는 하나로 두고 내용은 새로 쓴다
- 프롬프트 입력은 노드의 정의서까지 JSON 으로 묶는다
- 부르는 곳: 나누기, 합치기, 넣기, 빼기. 고치기(제목, 하는 일 등)와 잇기·끊기에는 부르지 않는다
- 명령서(계획을 만들 때 인터뷰를 정리한 문서)는 간선 프롬프트에 넣지 않는다
- 모델은 opus 그대로. claude -p 가 실패하면 고치지 않고 거절한다

## 평가 (dk-claude-tool-bundle tool-planner 절차)

"바꿀 때 dk-claude-tool-bundle 의 플래너 통해서 바꿔야함" (사용자, 2026-11-19)

### 나누기
- 포트: 계획 읽기, 노드 추가·고치기·지우기, 간선 추가·지우기 (계획 저장소 API)
- model: 노드 정의서(output_spec md)를 절(하는 일, 산출물 형태·담을 것, 그 외 설명)로 읽고 쓰는 일. 간선 다시 정하기의 입력 만들기, 계획 고치기의 정의서 만들기·바꾸기, make_plan 의 정의서 쓰기가 같이 쓴다
- 공통 기능: 없음. 정의서 모양은 도메인 지식이라 common 이 아니다
- tool-planner 범위 밖 (직접 만듦, 이전 plan-edit 과 같음): 간선 다시 정하기(`workflow/relink_edges/`), make_plan 의 간선 정리(`write_edges`), 계획 고치기(`workflow/plan_edit/`), plan-edit 스킬 글. 흐름 선언(FlowDefinition)은 바뀌지 않아 tool-workflow-planner 로 넘기지 않는다. claude -p 를 부르는 파일은 tool-add-prompt-task 의 모양(`prompt_{이름}.md`, `prompt_{이름}_output.py`, `PromptSpec` 상수)을 따르고, 시험은 tool-workflow-planner 6 절처럼 가짜 claude(`TASK_PLANNER_CLAUDE_BIN`)로 한다

### tool-assess-port

**판정**: 충족

| 접근 | 판정 | 포트 | 메서드 |
|---|---|---|---|
| 계획 읽기 | 충족 | plan_api | PlanApiReader.get_plan(plan_id) -> Plan |
| 노드 추가 | 충족 | plan_api | PlanApiWriter.add_node(plan_id, NewNode) -> PlanNode |
| 노드 고치기 | 충족 | plan_api | PlanApiWriter.update_node(plan_id, node_id, NodeChange) -> PlanNode |
| 노드 지우기 | 충족 | plan_api | PlanApiWriter.delete_node(plan_id, node_id) |
| 간선 추가 | 충족 | plan_api | PlanApiWriter.add_edge(plan_id, from_node_id, to_node_id) -> PlanEdge |
| 간선 지우기 | 충족 | plan_api | PlanApiWriter.delete_edge(plan_id, edge_id) |

**model 층 요청**
- 대상: plan (기존 도메인에 새 클래스)
- 클래스: NodeSpec (plan/node_spec.py)
- 필드: does: str, output_form: str, output_contents: str, notes: str
- 동작: NodeSpec.from_md(md: str) -> NodeSpec, to_md() -> str
- 쓰는 곳: relink_edges 의 입력 만들기, plan_edit 의 새 노드 정의서·고치기, (선택) make_plan write_specs 의 정의서 md
- 이유: 정의서 md 를 절로 나누는 코드가 지금 plan_edit 안(`node_spec.py` `split_sections`)에만 있다. 간선 다시 정하기도 같은 것을 써야 해서, 기능 폴더끼리 서로 가져다 쓰지 않게 model 에 둔다

**사용자 확인 필요**: 없음

### tool-assess-model

**판정**: 미충족 (새 클래스)

- [신규] model/plan/node_spec.py — NodeSpec
  - 필드: does: str (하는 일), output_form: str (산출물 형태. 없으면 ""), output_contents: str (산출물에 담을 것), notes: str (그 외 설명. 없으면 "")
  - 동작: from_md(md) -> NodeSpec (`### 이름` 머리로 절을 나누고, 산출물 첫 줄 `- 형태: ` 를 형태로), to_md() -> str (make_plan 과 같은 모양. 형태가 없으면 "(정하지 않음)", 설명이 없으면 "(없음)")
  - PlanNode 는 바꾸지 않는다 (`output_spec: str` 그대로). 저장 모양도 그대로
- 영향: plan_edit/node_spec.py 의 split_sections·new_spec·change_spec 을 NodeSpec 으로 바꾼다. specs/models.md 에 NodeSpec 절을 더한다

**사용자 확인 필요**: 없음

### 구현 순서
1. add-model: model/plan/node_spec.py (NodeSpec), 시험, specs/models.md
2. (직접) workflow/relink_edges/: relink_node, relink_request, relink_input(NodeSpec 사용), prompt_relink_edges.md(1.4 절 전문), prompt_relink_edges_output.py, relink_edges.py, 시험
3. (직접) make_plan write_edges 를 relink_edges 로 바꾸고, prompt_edges.md·build_edges_input·prompt_edges_output.py 지움, 시험 고침
4. (직접) plan_edit: op 칸(새 노드, order 뺌, scope → does), edit_graph(잇기 규칙 빼고 범위 모으기), edit_plan(relink 부르기, 이음·끊음), 시험 고침
5. (직접) plan-edit 스킬 글 5 절 to-be
6. 최종 검증: ruff, lint-imports, mypy, pytest. 별도 에이전트 리뷰. e2e

### 정할 것 (평가에서 나온 것)
- 출력 칸 `from` 은 파이썬 예약어라 출력 데이터 클래스의 필드 이름으로 쓸 수 없다 (출력 JSON 스키마를 데이터 클래스 필드 이름으로 만든다). 두 안:
  - 가. 프롬프트는 그대로 두고 출력 모양을 `edges: list[dict[str, int]]` 로 받는다. tool-add-prompt-task 가 허용하는 타입이지만, 간선 하나의 칸(from, to)이 스키마에 고정되지 않는다
  - 나. 프롬프트의 출력 칸을 `from_id`, `to_id` 로 바꾼다 (예시 넷과 출력 절). 스키마가 칸을 고정한다
  - 정함: 나 (사용자, 2026-11-19). 입력의 previous_edges, user_edges 는 `from`, `to` 그대로 둔다

## 0. 지금 생기는 일 (e2e4, 계획 8)

- 나누기: "39 화면 구현"을 41, 42, 43 으로 나누자, 39 로 들어오던 35, 34, 37 이 모두 첫 조각 41 로 갔다. API 를 부르는 43 이 API 구현(37)을 받지 못했다. 코드 규칙이 "들어오는 간선은 첫 조각, 나가는 간선은 마지막 조각"이기 때문이다 (`edit_graph.py` `_split`). 조각의 종류도 원래 노드(code)를 따라 와이어프레임이 code 가 됐다.
- 넣기: 36 과 37 사이에 45 를 넣자 36 → 37 이 지워졌다. API 구현은 테이블 설계도 직접 받아야 한다. 코드 규칙이 "after → 새 노드 → before, after → before 는 지움"이기 때문이다 (`_insert`).
- 고친 뒤 바뀐 간선이 결과(`changes`)에 나오지 않아, 사용자가 계획 표를 보고 찾았다.
- 나누기로 생긴 노드의 정의서가 세 줄 정도로 얇다. 처음 만든 노드는 산출물 아래 담을 것 4줄, 그 외 설명 5줄이 있다.

## 1. 간선 다시 정하기 (`workflow/relink_edges/`)

두 곳(make_plan, plan edit)이 같이 쓰는 기능 하나. claude -p 를 한 번 부르고, 받은 간선을 코드가 거른다.

### 1.1 입력 (프롬프트에 넘기는 JSON)

```jsonc
{
  "change": "39 \"댓글 화면 구현\" 을 41, 42, 43 으로 나눔",   // 바꾼 내용. 동작이 여럿이면 줄마다 하나
  "original_nodes": [ /* 지워지거나 바뀌기 전의 노드. 없으면 [] */ ],
  "changed_nodes":  [ /* 이번에 생기거나 바뀐 노드. 나눈 경우 나뉜 노드 전부 */ ],
  "neighbor_nodes": [ /* 바뀌기 전 원래 노드의 선행·후행 노드 (한 단계만) */ ],
  "previous_edges": [{"from": 35, "to": 39}, ...],             // 바뀌기 전, 위 노드들 사이의 간선
  "user_edges": {"link": [], "unlink": []}                     // 같은 고치기에서 사용자가 직접 말한 잇기·끊기
}
```
노드 하나: `{"id", "title", "kind", "does", "output": {"form", "contents"}, "notes"}`. 저장된 정의서 md(`### 하는 일`, `### 산출물`(`- 형태:` 줄과 담을 것), `### 그 외 설명`)를 코드가 절로 나눠 채운다.

### 1.2 출력

```json
{"edges": [{"from_id": 35, "to_id": 41}, {"from_id": 41, "to_id": 42}]}
```
changed_nodes 와 neighbor_nodes 사이의 간선 전부.

### 1.3 받은 뒤 코드가 하는 일

1. 거른다 (지금 `write_edges.py` 의 거르기를 옮김): 입력에 없는 노드, 자기 자신, 중복, 넣으면 순환이 생기는 간선은 버리고 경고로 남긴다.
2. `user_edges.unlink` 의 간선이 오면 버리고, `user_edges.link` 의 간선이 빠졌으면 더한다.
3. 결과를 돌려준다. 간선을 어디에 반영할지는 부른 쪽이 정한다 (2·3 절).

### 1.4 프롬프트 전문 (`prompt_relink_edges.md`, 새로)

````markdown
## 목적
계획의 일부 노드가 생기거나 바뀌었습니다. 바뀐 노드와 그 앞뒤 노드 사이의 간선을 다시 정합니다.
간선 A → B 는 B 가 A 의 산출물을 받아야 시작할 수 있다는 뜻입니다.

## 배경
계획을 실행하는 단위 하나를 노드(node), 노드 사이의 선후행 관계를 간선(edge)으로 나타냅니다.
노드마다 제목, 종류(document / research / code / hitl), 정의서(하는 일, 산출물, 그 외 설명)가 있습니다. hitl 은 사용자가 확인하는 노드입니다.
앞 단계에서 큰 작업을 여러 노드로 분해하거나, 노드를 넣고 빼고 합쳤습니다. 이 프롬프트는 그 뒤의 선후행 관계를 다시 올바르게 정합니다.
아래 판단 기준에 맞는 간선 배열을 돌려줍니다.

## 입력
JSON 하나입니다.
- change: 무엇을 바꿨는지 한 줄
- original_nodes: 이번에 지워지거나 바뀌기 전의 노드. 없으면 []
- changed_nodes: 이번에 생기거나 바뀐 노드. 나눈 경우 나뉜 노드 전부
- neighbor_nodes: 바뀌기 전에 원래 노드의 선행·후행이던 노드 (한 단계만)
- previous_edges: 바뀌기 전, 위 노드들 사이의 간선
- user_edges: 사용자가 직접 잇거나(link) 끊으라고(unlink) 한 간선
- fixed_edges: 그대로 남는 간선. 판단할 때 참고만 하고 다시 정하지 않습니다. 없으면 []

노드 하나의 모양: id, title, kind, does(하는 일), output(산출물의 form 과 contents), notes(그 외 설명)

처음 계획을 만들 때는 모든 노드가 changed_nodes 이고, original_nodes 와 neighbor_nodes 는 비어 있습니다.

## 판단 기준
계획을 수행할 때, 다음 노드를 수행하는 데 이전 노드의 결과가 필요하면 잇습니다.
- 뒤 노드가 앞 노드의 산출물을 실제로 받아 써야 할 때만 잇습니다. 노드의 does 와 output 을 보고 판단합니다.
- 원래 노드로 들어오던 간선은, 분해된 노드 가운데 그 산출물을 받아 써야 하는 노드로 옮깁니다. 원래 노드에서 나가던 간선은 그 산출물을 만드는 노드에서 잇습니다.
- 바뀌지 않은 앞뒤 노드끼리의 간선도 다시 봅니다. 사이에 노드가 들어왔어도, 뒤 노드가 앞 노드의 산출물을 직접 써야 하면 남깁니다.
- 사용자가 정한 간선은 그대로 둡니다. link 는 남기고, unlink 는 다시 잇지 않습니다.
- 간선을 따라가다 처음 노드로 돌아오는 순환을 만들지 않습니다.

예시를 참고합니다.

## 예시 1: 나누기

입력
```json
{
  "change": "39 \"댓글 화면 구현\" 을 41, 42, 43 으로 나눔",
  "original_nodes": [
    {"id": 39, "title": "댓글 화면 구현", "kind": "code",
     "does": "공지 상세 화면에 댓글 목록, 작성, 수정, 삭제 화면을 만들고 댓글 API 와 연결한다.",
     "output": {"form": "코드 변경", "contents": "공지 상세 화면의 댓글 영역 컴포넌트와 API 호출 코드"},
     "notes": "로그인하지 않은 사용자에게는 입력창 대신 로그인 안내를 보인다."}
  ],
  "changed_nodes": [
    {"id": 41, "title": "댓글 영역 와이어프레임", "kind": "document",
     "does": "댓글 목록, 입력창, 수정·삭제 버튼의 배치와 로그인·본인 여부에 따른 표시를 와이어프레임으로 잡는다.",
     "output": {"form": "문서", "contents": "댓글 영역 와이어프레임과 상태별 표시 규칙"},
     "notes": "기존 공지 상세 화면의 배치를 따른다."},
    {"id": 42, "title": "댓글 UI 컴포넌트 구현", "kind": "code",
     "does": "와이어프레임대로 댓글 목록과 입력 컴포넌트를 만든다. 데이터는 아직 가짜 값으로 채운다.",
     "output": {"form": "코드 변경", "contents": "댓글 목록·입력·수정 컴포넌트"},
     "notes": ""},
    {"id": 43, "title": "댓글 UI와 API 연결", "kind": "code",
     "does": "컴포넌트에서 댓글 API 를 불러 목록, 작성, 수정, 삭제가 실제로 동작하게 한다.",
     "output": {"form": "코드 변경", "contents": "API 호출 코드와 오류 처리"},
     "notes": "로그인하지 않은 사용자에게는 입력창 대신 로그인 안내를 보인다."}
  ],
  "neighbor_nodes": [
    {"id": 35, "title": "프론트 공지 상세 화면 구조 파악", "kind": "research",
     "does": "공지 상세 화면의 컴포넌트 구조와 상태 관리 방식을 조사한다.",
     "output": {"form": "조사 노트", "contents": "화면 구조와 댓글 영역을 붙일 위치"},
     "notes": ""},
    {"id": 34, "title": "인증·권한 처리 방식 파악", "kind": "research",
     "does": "로그인 여부, 본인 여부, 관리자 여부를 서버와 화면에서 어떻게 확인하는지 조사한다.",
     "output": {"form": "조사 노트", "contents": "권한 확인 방법과 쓸 함수"},
     "notes": ""},
    {"id": 37, "title": "댓글 백엔드 API 구현", "kind": "code",
     "does": "댓글 목록, 작성, 수정, 삭제 API 를 만든다.",
     "output": {"form": "코드 변경", "contents": "댓글 API 네 개와 응답 형식"},
     "notes": "응답은 항상 {data, error} 모양으로 감싼다."}
  ],
  "previous_edges": [
    {"from": 35, "to": 39},
    {"from": 34, "to": 39},
    {"from": 37, "to": 39},
    {"from": 34, "to": 37}
  ],
  "fixed_edges": [],
  "user_edges": {"link": [], "unlink": []}
}
```

출력
```json
{"edges": [
  {"from_id": 35, "to_id": 41},
  {"from_id": 34, "to_id": 41},
  {"from_id": 41, "to_id": 42},
  {"from_id": 42, "to_id": 43},
  {"from_id": 37, "to_id": 43},
  {"from_id": 34, "to_id": 37}
]}
```
- 와이어프레임(41)은 화면 구조(35)와 권한별 표시(34)를 받아 씁니다.
- API 를 부르는 일은 43 이 하므로 37 → 39 를 37 → 43 으로 옮깁니다.
- 34 → 37 은 바뀌지 않은 앞뒤 노드끼리의 간선이고, API 구현에 권한 확인이 필요하므로 남깁니다.

## 예시 2: 넣기

입력
```json
{
  "change": "36 과 37 사이에 45 \"API 명세 정하기\" 를 넣음",
  "original_nodes": [],
  "changed_nodes": [
    {"id": 45, "title": "API 명세 정하기", "kind": "document",
     "does": "테이블 설계를 보고 댓글 API 네 개의 요청·응답 예시를 정한다.",
     "output": {"form": "문서", "contents": "API 별 요청·응답 예시"},
     "notes": "응답은 항상 {data, error} 모양으로 감싼다."}
  ],
  "neighbor_nodes": [
    {"id": 36, "title": "댓글 테이블 설계", "kind": "code",
     "does": "댓글 테이블을 설계하고 마이그레이션을 만든다.",
     "output": {"form": "코드 변경", "contents": "댓글 테이블 마이그레이션과 컬럼 설명"},
     "notes": "외래 키는 걸지 않는다."},
    {"id": 37, "title": "댓글 백엔드 API 구현", "kind": "code",
     "does": "댓글 목록, 작성, 수정, 삭제 API 를 만든다.",
     "output": {"form": "코드 변경", "contents": "댓글 API 네 개"},
     "notes": ""},
    {"id": 38, "title": "댓글 API 테스트 작성", "kind": "code",
     "does": "댓글 API 네 개의 요청과 응답을 확인하는 테스트를 쓴다.",
     "output": {"form": "코드 변경", "contents": "API 별 테스트"},
     "notes": ""}
  ],
  "previous_edges": [
    {"from": 36, "to": 37}
  ],
  "fixed_edges": [
    {"from": 36, "to": 38},
    {"from": 37, "to": 38}
  ],
  "user_edges": {"link": [], "unlink": []}
}
```

출력
```json
{"edges": [
  {"from_id": 36, "to_id": 45},
  {"from_id": 45, "to_id": 37},
  {"from_id": 45, "to_id": 38},
  {"from_id": 36, "to_id": 37}
]}
```
- 명세(45)는 테이블 설계를 보고 정하므로 36 을 받습니다.
- API 구현(37)과 테스트(38)는 명세의 요청·응답 예시를 기준으로 쓰므로 45 를 받습니다.
- API 구현(37)은 명세와 함께 테이블 컬럼도 직접 써야 하므로 36 → 37 을 남깁니다.
- 36 → 38, 37 → 38 은 fixed_edges 라 답하지 않습니다. 그대로 남습니다.

## 출력
JSON 하나로 답합니다.
```json
{"edges": [{"from_id": 35, "to_id": 41}, {"from_id": 41, "to_id": 42}]}
```
- edges: changed_nodes 와 neighbor_nodes 사이의 간선 가운데 fixed_edges 를 뺀 전부. 지워진 original_nodes 는 쓰지 않습니다
- from_id, to_id: 노드 id(숫자). to_id 노드는 from_id 노드가 끝난 뒤 그 산출물을 받아 시작합니다
- 입력한 노드와 그 밖의 노드 사이의 간선은 쓰지 않습니다. 그 간선은 그대로 남습니다
````

## 2. plan edit 에서 부르기 (`workflow/plan_edit/`)

### 2.1 언제

고치기 명령 한 번에 나누기·합치기·넣기·빼기가 하나라도 있으면 한 번 부른다. 동작이 여럿이면 바뀐 노드와 앞뒤 노드를 모두 합쳐 넘기고, change 는 줄마다 하나씩 쓴다. 고치기와 잇기·끊기만 있으면 부르지 않는다.

### 2.2 동작마다 모으는 것

| 동작 | original_nodes | changed_nodes | neighbor_nodes |
|---|---|---|---|
| 나누기 | 나눈 노드 | 조각 전부 | 나눈 노드의 앞, 뒤 |
| 합치기 | 합친 노드들 | 합친 새 노드 | 합친 노드들의 앞, 뒤 (합친 노드끼리 제외) |
| 넣기 | 없음 | 새 노드 | 사용자가 말한 자리 (after, before) |
| 빼기 | 뺀 노드 | 없음 | 뺀 노드의 앞, 뒤 |

- previous_edges: 고치기 전 계획에서, original·neighbor 노드 사이의 간선
- user_edges: 같은 고치기 명령 안의 잇기·끊기
- 새 노드의 id 는 지금처럼 음수 임시 id 를 그대로 넘긴다. 보낼 때 진짜 id 로 바뀐다

### 2.3 순서 (`edit_plan.py` `_prepare`)

```
as-is: 읽기 → apply_all(노드 바꾸기 + 코드 규칙으로 잇기) → 새 문제 검사 → 보내기
to-be: 읽기 → apply_all(노드만 바꾸고 위 표를 모음) → relink_edges → 범위 안 간선 바꾸기 → 새 문제 검사 → 보내기
```
- 범위 안 간선 바꾸기: 양 끝이 모두 changed·neighbor 노드인 간선을 지우고, 받은 간선을 넣는다. 지워진 노드에 붙은 간선은 지금처럼 지운다. 범위 밖 노드와 이어진 간선은 그대로 둔다.
- claude -p 가 실패하면 `PlanEditRefusedError` 로 거절한다. 아무것도 보내지 않는다.

### 2.4 바뀐 간선을 결과에 보이기

`changes` 끝에 고치기 전과 후의 간선을 비교한 두 줄을 더한다. 모든 고치기 명령에 공통이다.
```
- 나눔: 39 댓글 화면 구현 → 41 댓글 영역 와이어프레임, 42 댓글 UI 컴포넌트 구현, 43 댓글 UI와 API 연결
- 이음: 35 → 41, 34 → 41, 41 → 42, 42 → 43, 37 → 43, 34 → 43
- 끊음: 35 → 39, 34 → 39, 37 → 39
```

### 2.5 지우는 코드 규칙

`_split`, `_merge`, `_insert`, `_remove` 안의 간선 잇기(`_connect`, after → before 지우기)를 뺀다. 나누기의 `order`(serial / parallel)와 `split_order.py` 도 뺀다. 간선은 LLM 이 정한다.

## 3. make_plan 에서 부르기 (`workflow/make_plan/split_plan/write_edges/`)

`write_edges` 가 `relink_edges` 를 부르게 바꾼다. split_plan 의 순서(나누기 → 정의서 → 간선 → 저장)는 그대로다.
- changed_nodes: 저장 전 노드 전부. original_nodes, neighbor_nodes 는 [].
- previous_edges: 정의서의 받을 것(`prerequisites`)으로 만든 간선. 지금 간선 프롬프트에 "받는 산출물"로 넘기던 정보다.
- id: 저장 전 노드의 `local_id`("n1" 같은 글자)를 1, 2, 3… 으로 바꿔 넘기고, 받은 간선을 다시 `local_id` 로 되돌린다.
- 지금 하던 "받는 산출물인데 빠진 간선 더하기"는 뺀다. previous_edges 로 넘기고 LLM 이 판단한다.
- 지우는 것: `prompt_edges.md`, `build_edges_input`, `prompt_edges_output.py`.

## 4. 새 노드의 정의서 (plan edit)

나누기의 조각, 넣는 노드, 합친 노드를 make_plan 정의서와 같은 칸으로 받는다. plan-edit 스킬(메인 세션)이 계획 전체와 원래 정의서를 읽고 대략 적는다.

| 칸 | 지금 | 바꾸면 |
|---|---|---|
| 종류 | 나누기: 원래 노드를 따름 | 새 노드마다 kind |
| 하는 일 | scope 한두 줄 | does 한두 줄 |
| 산출물 | output 한 줄 | output {form, contents}. contents 는 담을 것 2~4줄 |
| 그 외 설명 | note 한 줄 | notes. 나누는 노드의 조건 가운데 해당하는 것을 옮기고, 사용자가 말한 조건과 이유를 씀 |

- 정의서 md 는 make_plan 과 같은 모양으로 만든다 (`node_spec.py` `new_spec`).
  ```
  ### 하는 일
  {does}

  ### 산출물
  - 형태: {output.form}
  {output.contents}

  ### 그 외 설명
  {notes}
  ```
- 고치기(update)의 `scope` 도 `does` 로 이름을 맞춘다.

## 5. 스킬 글 (plan-edit, 전문)

as-is (`plugin/skills/plan-edit/SKILL.md`)
````markdown
---
name: plan-edit
description: 계획의 노드와 간선을 사용자 말대로 바꿔 계획 저장소에 보낸다. plan-feedback 이 부른다
argument-hint: <계획 id> <사용자 말>
---
`$ARGUMENTS` 의 첫 단어가 계획 id, 나머지가 사용자 말입니다.

`task-planner` 명령은 Bash 제한 시간 600000(10분)으로 부릅니다.

1. `task-planner plan show <id>` 로 지금 계획(노드, 간선)을 읽습니다.
2. 사용자 말을 아래 동작으로 옮깁니다. 말한 것만 바꿉니다.

   | op | 넘길 것 |
   |---|---|
   | split | node_id, into: [{title, scope, output?, note?}], order: serial / parallel |
   | merge | node_ids, title, scope, output?, note? |
   | insert | after?, before?, title, scope, kind, output?, note? |
   | remove | node_id |
   | update | node_id, 바꿀 것만: title, scope, kind, persona_ids, output, add_note |
   | link / unlink | from, to |

   - kind 는 document / research / code / hitl 가운데 하나입니다. hitl 은 사용자가 확인하는 노드입니다.
   - scope 는 이 노드가 하는 일 한두 줄, output 은 산출물 한 줄입니다. 사용자가 말한 조건은 note 나 add_note 에 넣습니다.
   - 앞뒤 간선은 넘기지 않습니다. 명령이 다시 잇습니다.
3. JSON 한 줄을 작은따옴표로 감싸 넘깁니다. JSON 안에는 작은따옴표(')를 쓰지 않습니다.
       task-planner plan edit <id> --ops '{"ops": [...]}'
4. 결과의 `changes` 와 `summary`(새 계획 표)를 그대로 돌려줍니다. `ok: false` 면 이유를 그대로 돌려줍니다.
````

to-be
````markdown
---
name: plan-edit
description: 계획의 노드와 간선을 사용자 말대로 바꿔 계획 저장소에 보낸다. plan-feedback 이 부른다
argument-hint: <계획 id> <사용자 말>
---
`$ARGUMENTS` 의 첫 단어가 계획 id, 나머지가 사용자 말입니다.

`task-planner` 명령은 Bash 제한 시간 600000(10분)으로 부릅니다. 노드를 나누거나 넣으면 간선을 다시 정하느라 1분 안팎이 걸립니다.

1. `task-planner plan show <id>` 로 지금 계획(노드, 정의서, 간선)을 읽습니다.
2. 사용자 말을 아래 동작으로 옮깁니다. 말한 것만 바꿉니다.

   | op | 넘길 것 |
   |---|---|
   | split | node_id, into: [새 노드] |
   | merge | node_ids, 새 노드 |
   | insert | after?, before?, 새 노드 |
   | remove | node_id |
   | update | node_id, 바꿀 것만: title, kind, persona_ids, does, output, add_note |
   | link / unlink | from, to |

   새 노드는 make_plan 의 정의서와 같은 칸으로 대략 적습니다.
   `{title, kind, does, output: {form, contents}, notes}`
   - kind: document / research / code / hitl 가운데 하나. hitl 은 사용자가 확인하는 노드입니다.
   - does: 이 노드의 목적과 하는 일 한두 줄
   - output: form 은 문서 / 표 / 결정 / 코드 변경 / 조사 노트 가운데 하나, contents 는 담을 것 2~4줄
   - notes: 꼭 할 일과 주의할 점. 나누는 노드의 정의서에 있던 조건 가운데 이 노드에 해당하는 것을 옮기고, 사용자가 말한 조건과 이유를 씁니다.
   - 간선은 넘기지 않습니다. 명령이 바뀐 노드와 앞뒤 노드 사이의 간선을 다시 정합니다.
3. JSON 한 줄을 작은따옴표로 감싸 넘깁니다. JSON 안에는 작은따옴표(')를 쓰지 않습니다.
       task-planner plan edit <id> --ops '{"ops": [...]}'
4. 결과의 `changes`(바뀐 노드와 간선)와 `summary`(새 계획 표)를 그대로 돌려줍니다. `ok: false` 면 이유를 그대로 돌려줍니다.
````

바뀐 곳: 첫머리 시간 안내 한 문장, 1 의 "정의서", 2 의 표(order 뺌, scope → does, 새 노드), "새 노드" 칸 설명, 간선 안내 한 줄, 4 의 changes 설명. plan-feedback 스킬은 바꾸지 않는다.

## 6. 파일 트리

```
src/task_planner/workflow/
├─ relink_edges/                         새로
│  ├─ __init__.py
│  ├─ relink_edges.py                    입력 JSON 만들기, claude -p 부르기, 거르기 (거르기는 write_edges 에서 옮김)
│  ├─ relink_input.py                    노드 → 입력 노드 모양 (정의서 md 를 does / output / notes 로)
│  ├─ prompt_relink_edges.md             1.4 절 전문
│  └─ prompt_relink_edges_output.py      {"edges": [{"from", "to"}]}
├─ plan_edit/
│  ├─ edit_graph.py                      간선 잇기 규칙을 빼고, 동작마다 original·changed·neighbor 를 모음
│  ├─ edit_plan.py                       relink_edges 를 부르고 범위 안 간선을 바꿈, changes 에 이음·끊음
│  ├─ node_spec.py                       new_spec: 산출물 형태 아래 담을 것. split_sections 는 relink_input 이 같이 씀
│  └─ op/                                new_part(title, kind, does, output{form, contents}, notes), split_op(order 뺌),
│                                        split_order.py 지움, update_op(scope → does), edit_op_reader(새 칸 읽기)
└─ make_plan/split_plan/write_edges/
   ├─ write_edges.py                     relink_edges 를 부름 (local_id ↔ 숫자 id)
   ├─ prompt_edges.md                    지움
   └─ prompt_edges_output.py             지움
plugin/skills/plan-edit/SKILL.md         5 절 to-be
tests/workflow/relink_edges/test_relink_edges.py   새로
tests/workflow/plan_edit/test_edit_plan.py         가짜 claude 로 고침
tests/workflow/make_plan/…                         간선 가짜 출력을 새 모양으로
```
`relink_edges` 는 workflow 아래 두 기능이 같이 쓰는 폴더다. claude_utils(claude -p 부르기)를 쓰므로 workflow 층에 둔다.

## 7. 시험

가짜 claude(입력 머리로 프롬프트를 알아보고 정해진 답을 냄)로 돌린다.
- relink_edges: 입력 JSON 모양(정의서가 절로 나뉨), 거르기(없는 노드, 자기 자신, 중복, 순환), unlink 간선을 버리고 link 간선을 더함
- plan edit 나누기: 계획 8 과 같은 모양에서 받은 간선대로 바뀌고, 범위 밖 간선은 그대로. changes 에 이음·끊음
- plan edit 넣기: 36 → 37 이 남는 답을 주면 남음
- plan edit 고치기만: claude -p 를 부르지 않음
- plan edit 에서 claude -p 실패: 거절, 아무것도 보내지 않음
- plan edit 새 노드 정의서: make_plan 모양 (형태 아래 담을 것)
- make_plan: local_id ↔ 숫자 id 가 맞게 되돌아오고, 받는 산출물이 previous_edges 로 들어감
- e2e: 계획 8 과 같은 나누기·넣기를 대화로 해서, 사용자가 간선을 손으로 다시 잇지 않아도 되는지 본다

## 8. 정할 것

- 검수 받음 (사용자, 2026-11-19): 1.4 절 프롬프트 전문(예시 1 의 34 → 43 은 뺌), 5 절 스킬 글 to-be 전문

## 이번 범위 밖

- 고친 뒤 남은 다른 노드의 정의서가 새 구조와 어긋나는 것 (지운 노드 이름이 남음, 역할이 겹치는 노드). e2e4 문제 5
- 계획 표를 보인 뒤 들어간 조건을 모른다고 한 것. e2e4 문제 6 (plan-feedback 스킬)

## 진행 기록

- 1. add-model: `model/plan/node_spec.py` (NodeSpec: from_md, to_md, 세 절 밖의 절은 extra_md 로 지킴), 시험 3개, specs/models.md 에 NodeSpec 절. 검증 통과
- 2. relink_edges: relink_node, relink_request, relink_input(NodeSpec 으로 절 나눔), prompt_relink_edges.md(계획서 1.4 절 그대로), prompt_relink_edges_output.py + prompt_relink_edges_edge.py(출력 칸 from_id, to_id), relink_edges.py(거르기). 버린 간선은 글이 아니라 (간선, 까닭)으로 돌려주고 부른 쪽이 글을 만든다 (make_plan 은 n1 같은 local_id, 고치기는 노드 id 라서). 시험 3개
- 3. make_plan write_edges: relink_edges 를 부름. local_id ↔ 1, 2, 3…, 받는 산출물 → previous_edges. 명령서 인자를 뺌(split_plan_task 한 줄). prompt_edges.md, prompt_edges_output.py 지움. "받는 산출물인데 빠진 간선 더하기"는 뺌 (계획대로). 시험 3개로 다시 씀, make_plan 흐름 시험의 가짜 claude 를 새 입력에 맞춤
- 4. plan_edit: op(NewPart: title, does, kind?, output{form, contents}?, notes?; NodeOutput 새로; split 의 order·split_order.py 지움; insert 의 kind 는 새 노드 칸으로, 없으면 거절; update 의 scope → does, output 은 {form, contents} 또는 형태 글), node_spec(NodeSpec 으로 만들고 바꿈), edit_graph(간선 잇기 규칙을 빼고 원래·바뀐·앞뒤 노드와 이전 간선을 모음, 잇기·끊기는 user_edges 로), edit_plan(relink 부르기, 실패하면 거절, 이음·끊음 줄). 시험 다시 씀 (가짜 caller)
  - 계획과 다른 점: 잇기·끊기만 있는 고치기는 지금처럼 바로 반영하고, "이음 / 끊음" 줄은 비교 줄 하나로 합쳤다 (동작마다 적던 줄은 뺌). 앞뒤가 없는 노드를 빼면 다시 정할 노드가 없어 부르지 않는다
  - 시험이 실제 claude 를 부르지 않게 tests/conftest.py 에 기본값 `TASK_PLANNER_CLAUDE_BIN=false` 를 더함
- 5. plan-edit 스킬 글: 계획서 5 절 to-be 그대로
- 6. 최종 검증: pytest 154개, ruff, ruff format, mypy, lint-imports 통과
- 별도 에이전트 리뷰 반영:
  1. 한 고치기에 구조 동작이 둘 이상이면, 서로 다른 동작의 범위 노드 사이 간선이 이전 간선에서 빠진 채 지워졌다 → 이전 간선에 지금 범위 노드끼리의 간선을 더함. 시험 추가 (빼기 + 다른 곳 넣기)
  2. 범위 밖 노드를 거치는 순환은 거르기를 통과해 고치기 전체가 거절됐다 → 범위 밖 노드에 닿은 간선(`outside_edges`, 프롬프트에는 넣지 않음)도 순환 검사에 씀. 시험 추가
  3. 넣을 자리 없이 넣으면 이을 짝이 없는데 opus 를 불렀다 → 바뀐 노드와 앞뒤 노드가 합쳐 둘 미만이면 부르지 않음. 시험 추가
  4. 정의서의 머리 앞 글이나 같은 이름의 절이 덮어써졌다 → 이어 붙임. 시험 추가
  - 검증: pytest 158개, ruff, mypy, lint-imports 통과
- 나눈 노드의 정의서를 claude -p 로 쓰는 안(2026-11-18 고치기 초안 3 절)은 지금 넣지 않는다. 메인 세션이 하는 일 1~2줄로 대략 적고, 필요하면 나중에 넣는다 (사용자, 2026-11-19)
- 1 번(동작 둘 이상일 때 이전 간선이 빠짐)은 보류로 돌려 코드에서 뺐다. 백로그에 적음 (사용자, 2026-11-19: "1번은 보류하고, 백로그에 기록만")
- 범위 밖 노드를 거치는 순환 거르기는 그대로 둔다 (사용자, 2026-11-19: LLM 이 볼 수 없는 길이라 어쩔 수 없음)
- plan-feedback 스킬에 한 줄: "만약 insert 요청이 왔는데, 추가할 노드의 선행, 후행 노드를 특정할 수 없다면, 확실히 물어보세요." (사용자 문장 그대로). 코드로 자리 없는 넣기를 거절하는 것은 하지 않음, plan-edit 표의 insert 줄은 그대로 (사용자, 2026-11-19)
- e2e5 (계획 9, 885e9f9): 나누기는 손으로 다시 잇지 않아도 맞음. 넣기는 자리 두 노드만 넘겨 새 명세 노드가 한 곳에만 이어짐 → 아래 다 안
- 넣기의 범위 넓히기 (다 안, 사용자 2026-11-19): 앞뒤 노드로 자리(after, before)와 그 둘에 바로 붙은 노드를 넘긴다. 다시 정하는 간선은 새 노드에 닿는 간선과 자리 두 노드 사이 간선(previous_edges)뿐이고, 앞뒤 노드끼리의 나머지 간선은 fixed_edges 로 넘겨 그대로 둔다. 프롬프트: 입력 목록에 fixed_edges 한 줄, 출력 줄을 "fixed_edges 를 뺀 전부"로, 예시 1 에 "fixed_edges": [], 예시 2 를 38 API 테스트를 더한 판으로 (1.4 절 전문에 반영). 코드: relink_request 에 fixed_edges, relink_input 에 칸, _filter 가 fixed_edges 를 먼저 넣음, edit_graph._insert. 시험 1 개 추가. pytest 158 개 통과
