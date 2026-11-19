---
name: plan-edit
description: 계획의 노드와 간선을 사용자 말대로 바꿔 계획 저장소에 보낸다. plan-feedback 이 부른다
argument-hint: <계획 id> <사용자 말>
---
`$ARGUMENTS` 의 첫 단어가 계획 id, 나머지가 사용자 말입니다.

`task_plan_manager` 명령은 Bash 제한 시간 600000(10분)으로 부릅니다.

1. `task_plan_manager plan show <id>` 로 지금 계획(노드, 간선)을 읽습니다.
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
       task_plan_manager plan edit <id> <<'EOF'
       {"ops": [...]}
       EOF
4. 결과의 `changes` 와 `summary`(새 계획 표)를 그대로 돌려줍니다. `ok: false` 면 이유를 그대로 돌려줍니다.
