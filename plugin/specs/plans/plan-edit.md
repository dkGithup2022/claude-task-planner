# 계획 고치기 (A 5 단계 "대화로 고치기")

계획을 보인 뒤 사용자가 대화로 고칠 곳을 말하면 노드와 간선을 바꾸고, 바뀔 때마다 계획 저장소(서버)에 보낸다.
진행 방식: 계획 → 만들기 → 시험 → 단계 기록.

## 요청

- "뷰어가 서버에 있기 때문에 난 바뀔때마다 서버로 올려야 한다는 주의" (사용자, 2026-11-19)
- 대화 스킬은 짧게 쓴다. 피드백을 받고, 만족하면 /plan-go, 취소하면 /plan-cancel 을 안내하고, 고치는 일의 규칙과 예시 대화를 둔다 (사용자, 2026-11-19)
- "실제로 각 노드, 데이터 바꾸는 스킬을 별도로 만들어서 관리", "최소스펙으로 간결하게" (사용자, 2026-11-19)
- 머무르게 하는 방법은 스킬만 쓴다(가). make_plan 의 마지막 단계가 이 스킬을 부르게 한다. 그러면 적용 전 확인은 두지 않는다 (사용자, 2026-11-19)
- "최소 스펙으로 가자": 새 노드의 정의서를 claude -p 로 쓰지 않고, 데이터 스킬이 넘긴 값으로 만든다 (사용자, 2026-11-19)
- 그대로 쓰는 것: 2026-11-18 고치기 초안의 묶음 동작(split, merge, insert, remove, update, link, unlink)과 "앞뒤를 다시 잇는 일은 명령 안의 코드가 맡는다" (corbina/notes/2026-11-18-prompt-edit-plan-draft.md, 사용자 판정 "이 초안대로 간다")

## 옛 버전 확인: 고친 뒤 노드별 작업 지시를 다시 만들었나

- 고친 직후에는 만들지 않았다. 대화로 고치면 서버의 계획(노드 output_spec, 간선)만 바뀌었다 (persona-enhancer-pg2/plugin/client/plan/graph_ops.py).
- 노드별 작업 지시(`prompt.md`)는 확정이 끝날 때 모든 노드에 대해 한 번 만들었다. `/plan-go` 절차의 끝에서 `enhancer plan prepare` 로 노드 스펙 사본(`node_spec.md`)과 실행 기록을 만든 뒤, `enhancer plan prompts` 로 노드마다 claude -p(opus)를 불렀다. 노드 하나에 1분 안팎, $0.3~0.6 이 들었다 (persona-enhancer-pg2/plugin/skills/plan-go/procedure.md:50-51, plugin/client/plan/node_prompts.py).
- 이미 만든 작업 지시는 실행 중에 `--force` 로 노드 하나만 다시 만들 수 있었다 (plugin/skills/plan-run/SKILL.md:25).
- 지금 설계에서 작업 지시 만들기는 D(계획 실행) 2 단계다 (2026-11-18-flow-io.md D 절). 그래서 고치기는 계획 저장소만 바꾸면 되고, 작업 지시는 실행할 때 고친 정의서로 만든다.

## 대화에 어떻게 끼어드나

```
/task-planner:run make_plan
  └─ … ─▶ show_plan (마지막 단계)
            └─ 끝 지시: {text: 계획 표 + 안내, skill: "task-planner:plan-feedback 6"}
                  │  메인 세션: 글을 보이고 Skill 로 plan-feedback 6 을 부름 (흐름은 끝남)
                  ▼
plan-feedback (대화 스킬, 메인 세션 맥락에 남음)
  사용자: "화면 설계가 너무 커. 와이어프레임이랑 디자인 테마로 나눠 줘"
     │
     ├─ 고치는 말 ─▶ Skill: plan-edit 6 (사용자 말)
     │                 ├─ task-planner plan show 6          ─▶ 계획 JSON
     │                 ├─ 사용자 말 → 묶음 동작(ops)
     │                 └─ task-planner plan edit 6 <<ops    ─▶ 코드가
     │                        ├─ 메모리에서 동작 적용 + 앞뒤 다시 잇기 + 정의서 만들기
     │                        ├─ 문제 점검 → 새 문제면 아무것도 보내지 않고 거절
     │                        ├─ 바뀐 것마다 서버에 요청
     │                        └─ 바뀐 것 + 새 계획 표 출력
     │               ◀─ 바뀐 것과 새 계획 표를 보이고 "더 고칠 곳이 있으면 말해 주세요"
     ├─ 질문·잡담 ─▶ 그냥 답함
     └─ "이대로 할게" ─▶ "/plan-go 6 을 입력하면 확정합니다"
                  │
                  ▼
/plan-go 6 ─▶ 확정 흐름 (보여 준 시각부터의 대화 전체가 지식 추출 재료)
```

## 1. 평가 (dk-claude-tool-bundle tool-planner 절차)

### 나누기
- 포트: 계획 읽기(노드, 간선, 상태), 노드 추가·고치기·지우기, 간선 추가·지우기 (계획 저장소 API)
- 공통 기능: 없음
- tool-planner 범위 밖 (직접 만듦): 고치기 기능 코드(`workflow/plan_edit/`), 명령(`entry/cli.py` 의 plan show·edit), engine 의 끝 지시 `skill`, 플러그인 스킬 셋(plan-feedback, plan-edit, run 한 줄). 흐름(FlowDefinition)이 아니라 tool-workflow-planner 로도 넘기지 않는다

### tool-assess-port

**판정**: 충족

| 접근 | 판정 | 포트 | 메서드 |
|---|---|---|---|
| 계획 읽기 | 충족 | plan_api | PlanApiReader.get_plan(plan_id) -> Plan |
| 노드 추가 | 충족 | plan_api | PlanApiWriter.add_node(plan_id, NewNode) -> PlanNode |
| 노드 고치기 | 충족 | plan_api | PlanApiWriter.update_node(plan_id, node_id, NodeChange) -> PlanNode |
| 노드 지우기 | 충족 | plan_api | PlanApiWriter.delete_node(plan_id, node_id) (닿은 간선도 지움) |
| 간선 추가 | 충족 | plan_api | PlanApiWriter.add_edge(plan_id, from_node_id, to_node_id) -> PlanEdge |
| 간선 지우기 | 충족 | plan_api | PlanApiWriter.delete_edge(plan_id, edge_id) |

**model 층 요청**: 없음. 묶음 동작(op)은 도메인 데이터가 아니라 명령의 입력 스펙이라 `workflow/plan_edit/` 에 둔다.

**사용자 확인 필요**: 없음

### tool-assess-model

**판정**: 충족. Plan(노드, 간선, persona_ids, status), `Plan.prerequisites`, `Plan.problems`, PlanStatus, NodeKind 로 충분하다. 뒤 노드 찾기는 간선에서 계산한다.

## 1. 입력과 받는 방식

- 대화 스킬 `plan-feedback <id>`: make_plan 의 끝 지시가 부른다. 사용자가 직접 불러도 된다.
- 데이터 스킬 `plan-edit <id> <사용자 말>`: plan-feedback 이 부른다.
- `task-planner plan show <id>`: 인자만 받는다.
- `task-planner plan edit <id>`: 표준 입력으로 JSON 하나를 받는다 (heredoc. 허용 도구가 `Bash(task-planner:*)` 뿐이라 파일을 쓰지 않음).

```json
{"ops": [
  {"op": "split", "node_id": 14, "order": "serial", "into": [
    {"title": "와이어프레임 설계", "scope": "화면별 배치와 이동 흐름을 정한다."},
    {"title": "디자인 테마 설계", "scope": "색, 글꼴, 간격을 정한다.", "note": "기존 서비스 색을 그대로 쓴다."}
  ]}
]}
```

| op | 넘길 것 | 코드가 하는 일 |
|---|---|---|
| split | node_id, order(serial / parallel), into: [{title, scope, output?, note?}] | 원래 노드를 지우고 새 노드를 만든다. 차례로: 앞 노드들 → 첫 → … → 끝 → 뒤 노드들. 동시에: 앞 노드들 → 새 노드 각각 → 뒤 노드들. 종류와 담당은 원래 노드를 따른다 |
| merge | node_ids, title, scope, output?, note? | 합칠 노드들을 지우고 새 노드 하나를 만든다. 그 노드들의 앞 노드를 모두 앞에, 뒤 노드를 모두 뒤에 잇는다. 합쳐진 노드끼리의 간선은 없앤다. 종류는 첫 노드, 담당은 모두 합친다 |
| insert | after?, before?, title, scope, kind, output?, note? | after → 새 노드 → before 로 잇고, after → before 간선은 지운다. 담당은 hitl 이면 비우고, 아니면 계획의 첫 페르소나 |
| remove | node_id | 노드를 지우고 앞 노드 각각 → 뒤 노드 각각을 바로 잇는다 |
| update | node_id, 바꿀 것만: title, scope, kind, persona_ids, output, add_note | scope 는 "하는 일" 절을, output 은 "산출물" 절을 바꾼다. add_note 는 "그 외 설명" 끝에 한 줄을 더한다 |
| link / unlink | from, to | 간선 하나를 더하거나 지운다 |

- scope: 이 노드가 하는 일 한두 줄. output: 산출물 한 줄(형태와 담을 것). note: 그 외 설명에 넣을 한 줄. 사용자가 말한 조건은 note 나 add_note 에 넣는다.
- 새 노드의 정의서는 make_plan 과 같은 형식으로 만든다: `### 하는 일` scope / `### 산출물` `- 형태: ` output (없으면 "(정하지 않음)") / `### 그 외 설명` note (없으면 "(없음)").

## 2. 출력과 내보내는 방식

**plan show**
```json
{
  "plan_id": 6, "title": "…", "status": "reviewing", "persona_ids": [1],
  "nodes": [
    {"node_id": 17, "title": "글 구성 설계", "kind": "document", "persona_ids": [1], "output_spec": "### 하는 일\n…"},
    ...
  ],
  "edges": [{"from": 17, "to": 18}, ...]
}
```

**plan edit** 성공
```json
{
  "ok": true,
  "changes": ["14 화면 설계를 나눔 → 31 와이어프레임 설계, 32 디자인 테마 설계", "간선 12→31, 31→32, 32→15 추가", "..."],
  "summary": "계획 6 \"…\" 을 고쳤습니다. 노드 11개, 간선 24개.\n\n| 노드 | 제목 | 종류 | 받는 산출물 |\n…",
  "problems": []
}
```
거절 (서버에 아무것도 보내지 않음)
```json
{"ok": false, "reason": "순환: 23 블로그 원고 작성 → 27 원고와 실습 검증 → 23 블로그 원고 작성"}
```
- 이런 경우에 거절한다: 계획이 검토 중이 아님, 없는 노드, 고치기 전에 없던 문제(순환, 끊긴 간선 끝, 담당 없음)가 생김.
- 보내다가 서버 요청이 실패하면 `ok: false` 와 그때까지 반영한 `changes`, 그리고 오류를 돌려준다. 되돌리지 않는다.

## 3. 데이터

- 계획 저장소(서버 또는 `.mockData/plans/<id>.json`): 바뀐 것마다 바로 반영된다. 순서는 노드 추가 → 노드 고치기 → 간선 지우기 → 간선 추가 → 노드 지우기다.
- 로컬 계획 폴더 `.plan/<id>/` 는 바꾸지 않는다. `shown.json` 의 보여 준 시각도 그대로 둔다. 그래야 확정할 때 처음 보인 뒤의 고치기 대화가 모두 지식 추출에 들어간다.
- engine: 끝 지시의 내용(ShowRequest)에 `skill`(없으면 null)을 더한다.

## 4. 파일 트리

```
plugin/skills/
├─ plan-feedback/SKILL.md                      새로: 대화 스킬 (5절)
├─ plan-edit/SKILL.md                          새로: 데이터 스킬 (5절)
└─ run/SKILL.md                                finished 에 skill 이 있으면 부른다 (한 줄)
src/task_planner/
├─ engine/request/show_request.py              skill: str | None = None
├─ engine/instruction/instruction_converter.py  skill 이 있으면 payload 에 넣음
├─ engine/runner/unit/default_unit_runner.py   마지막 보이기를 끝 지시로 바꿀 때 skill 도 옮김
├─ entry/cli.py                                plan show, plan edit 하위 명령
└─ workflow/
   ├─ plan_edit/                               새로 (흐름이 아닌 기능 폴더. 명령이 부름)
   │  ├─ op/                    묶음 동작 데이터, 동작마다 한 파일, JSON 읽기
   │  ├─ edit_graph.py          op 를 메모리의 노드·간선에 적용 (앞뒤 다시 잇기, 정의서 만들기)
   │  ├─ send_edit.py           고치기 전과 후를 비교해 PlanApiWriter 로 보냄, 바뀐 것 글
   │  ├─ plan_view.py           plan show 의 JSON
   │  └─ plan_edit_refused_error.py
   └─ make_plan/
   ├─ show_plan/show_plan_task.py      끝 지시에 skill "task-planner:plan-feedback <id>"
   └─ prepare_show/plan_summary.py     머리 줄 "만들었습니다 / 고쳤습니다" 를 고름
tests/workflow/plan_edit/              새로: op 마다 다시 잇기, 거절, 보내는 순서, show JSON
```

## 5. 스킬 전문

### plan-feedback

````markdown
---
name: plan-feedback
description: 검토 중인 계획에 대한 피드백을 받아 고친다. 계획을 보인 뒤부터 /plan-go 또는 /plan-cancel 까지 쓴다
argument-hint: <계획 id>
---
- 계획 <id> 의 노드와 계획에 대한 피드백을 받습니다.
- 만족하면 `/plan-go <id>`, 취소하려면 `/plan-cancel <id>` 를 입력하게 안내합니다.
- 이 단계는 확정 전에, 대화로 기존 계획과 노드를 바꾸거나 노드에 지시할 내용을 더하는 단계입니다.

고치는 일은 아래 다섯 가지입니다.
- 나누기: 노드 하나가 너무 크면 여럿으로 나눕니다.
- 합치기: 노드 여럿을 하나로 모읍니다.
- 넣기·빼기: 노드를 더하거나 뺍니다.
- 고치기: 노드의 이름, 하는 일, 종류, 담당, 지시할 내용을 바꿉니다.
- 순서: 어느 노드의 산출물을 어느 노드가 받아 쓰는지 바꿉니다.

계획을 고치는 말이 오면 Skill 로 `plan-edit <id>` 를 부르고, 사용자 말을 그대로 넘깁니다.
plan-edit 이 돌려준 바뀐 것과 새 계획 표를 그대로 보이고, 더 고칠 것이 있는지 묻습니다.
고치는 말이 아니면(질문, 잡담) 그냥 답합니다. 지식으로 저장하거나 Claude 메모리에 적지 않습니다. 지식은 /plan-go 때 이 대화에서 뽑습니다.

예시 대화 1 (나누기)
```
Claude: 현재 계획에서 바꿀 것이 있다면 말해 주세요.
사용자: 화면 설계 작업이 너무 커. 와이어프레임이랑 디자인 테마로 나눠 줘. 디자인 테마는 기존 서비스 색을 그대로 쓰는 게 중요해.
```
대응
```
plan-edit 6 에 사용자 말을 넘김
→ 화면 설계를 와이어프레임, 디자인 테마로 나누고 앞뒤를 다시 이음. 디자인 테마의 지시에 "기존 서비스 색을 그대로 씀"을 넣음
→ 바뀐 것과 새 계획 표를 보이고 "더 고칠 곳이 있으면 말해 주세요"
```

예시 대화 2 (추가)
```
사용자: 배포하기 전에 스테이징에서 내가 직접 한 번 확인하는 단계를 넣어 줘.
```
대응
```
plan-edit 6 에 사용자 말을 넘김
→ 구현과 배포 사이에 확인 노드(hitl) "스테이징 확인"을 넣음
→ 바뀐 것과 새 계획 표를 보임
```

예시 대화 3 (제거)
```
사용자: README 작성은 빼 줘. 이번엔 필요 없어.
```
대응
```
plan-edit 6 에 사용자 말을 넘김
→ README 작성을 빼고, 그 노드를 거쳐 가던 앞뒤를 바로 이음
→ 바뀐 것과 새 계획 표를 보임
```

예시 대화 4 (고치기)
```
사용자: API 구현 작업에는 응답을 항상 {data, error} 로 감싸라고 넣어 줘.
```
대응
```
plan-edit 6 에 사용자 말을 넘김
→ API 구현의 지시에 응답 형식을 더함. 다른 노드와 간선은 그대로
→ 바뀐 것과 새 계획 표를 보임
```

예시 대화 5 (확정)
```
사용자: 좋아 이대로 할게.
```
대응
```
고치지 않음. "/plan-go 6 을 입력하면 확정합니다" 라고 안내
```
````

### plan-edit

````markdown
---
name: plan-edit
description: 계획의 노드와 간선을 사용자 말대로 바꿔 계획 저장소에 보낸다. plan-feedback 이 부른다
argument-hint: <계획 id> <사용자 말>
---
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

   - scope 는 이 노드가 하는 일 한두 줄, output 은 산출물 한 줄입니다. 사용자가 말한 조건은 note 나 add_note 에 넣습니다.
   - 앞뒤 간선은 넘기지 않습니다. 명령이 다시 잇습니다.
3. 넘깁니다.
       task-planner plan edit <id> <<'EOF'
       {"ops": [...]}
       EOF
4. 결과의 `changes` 와 `summary`(새 계획 표)를 그대로 돌려줍니다. `ok: false` 면 이유를 그대로 돌려줍니다.
````

### run 스킬에 더하는 한 줄

- 지금: "`finished`: `payload.text` 를 보이고 끝냅니다."
- 바꾸면: "`finished`: `payload.text` 를 보이고 끝냅니다. `payload.skill` 이 있으면 이어서 Skill 도구로 그 스킬을 부릅니다."

## 6. 코드 요지

- `plan edit`:
  1. 계획을 읽는다. 검토 중이 아니면 거절한다.
  2. 노드와 간선을 메모리에 복사하고 op 를 차례로 적용한다. 새 노드는 음수 임시 id 를 받는다. 앞뒤 다시 잇기와 정의서 만들기도 여기서 한다.
  3. 바뀐 모습으로 `Plan.problems()` 를 돌려, 고치기 전에 없던 문제가 생겼으면 거절한다.
  4. 전과 후를 비교해 보낸다: 노드 추가(임시 id → 진짜 id), 노드 고치기, 간선 지우기, 간선 추가, 노드 지우기.
  5. 다시 읽어 `build_summary(plan, [], "고쳤습니다")` 와 `problems` 를 출력한다.
- 정의서 md 는 `write_specs.py` 의 `_output_spec` 과 같은 형식으로 만든다. 같은 함수를 함께 쓰도록 옮긴다.

## 진행 기록

- 2026-11-19 단위 1 engine: 끝 지시에 skill 싣기 (ShowRequest.skill, 변환기는 skill 이 있을 때만 싣기, 마지막 보이기 → 끝 지시가 skill 도 옮김, run 스킬 한 줄). 시험 1개
- 2026-11-19 단위 2 workflow/plan_edit/: op/ (동작 7개, NewPart, SplitOrder, JSON 읽기), edit_graph.py, node_spec.py, send_edit.py, edit_plan.py. 시험 9개 (나누기 차례로·동시에, 합치기, 넣기, 빼기, 고치기, 순환 거절, 상태·동작 거절, show)
  - 계획과 다른 점: 정의서 md 만들기를 write_specs 와 같은 함수로 합치지 않고 plan_edit/node_spec.py 에 같은 형식으로 두었다 (make_plan 코드를 건드리지 않음)
  - 바뀐 것 글은 조사가 이름에 붙지 않게 "나눔: 14 화면 설계 → …" 모양으로 함
- 2026-11-19 단위 3 entry/cli.py: plan show, plan edit (표준 입력 JSON). 시험 1개
- 2026-11-19 단위 4 make_plan show_plan 이 skill "task-planner:plan-feedback <id>" 를 실음, 계획 표 머리 줄 동사 인자, 스킬 plan-feedback·plan-edit. make_plan 시험에 skill 확인 추가
- 별도 에이전트 리뷰 (단위 1~4 함께):
  - (1) 새 문제를 문제 글 그대로 비교해서, 원래 있던 문제가 간선 id 나 노드 제목이 바뀌면 새 문제로 잡혀 거절됨 → 원래 간선은 원래 id 를 쓰고, 제목을 지운 계획끼리 비교하게 고침. 시험 추가
  - (2) merge 에 같은 id 가 두 번 오면 명령이 오류로 멈춤 → 겹친 id 는 한 번만 씀
  - (3) 확인 노드를 작업 노드로 바꿀 때 담당이 비어 거절됨 → 담당을 주지 않았으면 계획의 첫 페르소나. 시험 추가
- 검증: pytest 138개, ruff, ruff format, lint-imports, mypy 통과
- 2026-11-19 e2e(edit1, 계획 7)에서 찾아 고침 (사용자 승인):
  - heredoc 을 붙인 명령은 허용 규칙 `Bash(task-planner:*)` 에 맞지 않아 거부됨 → `plan edit <id> --ops '<JSON>'` 인자를 받고, 스킬은 이 인자를 씀. 표준 입력도 그대로 받음
  - 스킬이 kind 에 `doc` 을 넣음 → plan-edit 스킬에 kind 값 목록(document / research / code / hitl)
  - 메인 세션이 끝 지시의 계획 표를 보이지 않고 바로 plan-feedback 을 부름 → run 스킬: skill 이 있으면 먼저 글을 그대로 적은 뒤 스킬을 부름

## 단계 기록
