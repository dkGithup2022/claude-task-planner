---
name: plan-edit
description: 계획의 노드와 간선을 사용자 말대로 바꿔 계획 저장소에 보낸다. plan-feedback 이 부른다
argument-hint: <계획 id> <사용자 말>
---
`$ARGUMENTS` 의 첫 단어가 계획 id, 나머지가 사용자 말입니다.

`task_plan_manager` 명령은 Bash 제한 시간 600000(10분)으로 부릅니다. 노드를 나누거나 넣으면 간선을 다시 정하느라 1분 안팎이 걸립니다.

1. `task_plan_manager plan show <id>` 로 지금 계획(노드, 정의서, 간선)을 읽습니다.
2. 사용자 말을 아래 동작으로 옮깁니다. 말한 것만 바꿉니다.

   | op | 넘길 것 |
   |---|---|
   | split | node_id, into: [새 노드] |
   | merge | node_ids, 새 노드의 칸을 같은 층에 (title, kind, does, output, notes) |
   | insert | after?, before?, 새 노드의 칸을 같은 층에 (title, kind, does, output, notes) |
   | remove | node_id |
   | update | node_id, 바꿀 것만: title, kind, persona_ids, does, output, add_note |
   | link / unlink | from, to |

   merge 와 insert 는 새 노드를 `node` 같은 칸 아래에 묶지 않고 op 와 같은 층에 적습니다.
       {"op": "merge", "node_ids": [63, 64], "title": "엔드포인트·에러 코드 설계", "kind": "document", "does": "…", "output": {"form": "표", "contents": "…"}, "notes": "…"}

   새 노드는 make_plan 의 정의서와 같은 칸으로 대략 적습니다.
   `{title, kind, does, output: {form, contents}, notes}`
   - kind: document / research / code / hitl 가운데 하나. hitl 은 사용자가 확인하는 노드입니다.
   - does: 이 노드의 목적과 하는 일 한두 줄
   - output: form 은 문서 / 표 / 결정 / 코드 변경 / 조사 노트 가운데 하나, contents 는 담을 것 2~4줄
   - notes: 꼭 할 일과 주의할 점. 나누는 노드의 정의서에 있던 조건 가운데 이 노드에 해당하는 것을 옮기고, 사용자가 말한 조건과 이유를 씁니다.
   - 간선은 넘기지 않습니다. 명령이 바뀐 노드와 앞뒤 노드 사이의 간선을 다시 정합니다.
3. JSON 한 줄을 작은따옴표로 감싸 넘깁니다. JSON 안에는 작은따옴표(')를 쓰지 않습니다.
       task_plan_manager plan edit <id> --ops '{"ops": [...]}'
4. 결과의 `changes`(바뀐 노드와 간선)와 `summary`(새 계획 표)를 그대로 돌려줍니다. `ok: false` 면 이유를 그대로 돌려줍니다.
