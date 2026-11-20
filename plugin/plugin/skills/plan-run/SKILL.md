---
name: plan-run
description: 승인된 계획을 실행한다. 계획 id 를 인자로 받는다. id 가 없으면 이 작업 폴더의 계획 목록을 보인다
disable-model-invocation: true
argument-hint: <계획 id>
---
계획을 실행합니다. 순서, 상태, 데이터는 `task_plan_manager` 명령이 정합니다. 이 세션은 명령이 돌려준 지시 하나만 처리하고, 다른 판단이나 파일 쓰기를 하지 않습니다.

`task_plan_manager` 명령(start, next, done)은 모두 Bash 의 run_in_background 로, 제한 시간 4200000(70분)을 붙여 부릅니다. 노드 실행 때문에 한 번에 몇십 분이 걸릴 수 있습니다. 완료 알림이 오면 그 출력(지시 JSON)을 읽어 이어 갑니다. 기다리는 동안 다른 명령을 부르지 않습니다.
Stop 훅이 "task_plan_manager next 로 다음 지시를 받으세요" 라고 하면, 앞 명령이 이미 끝난 것입니다. next 를 부르기 전에 앞 명령의 출력을 읽어 그 지시부터 처리합니다.

1. `$ARGUMENTS` 에 계획 id(숫자)가 있는지 봅니다.
   - 있으면 `task_plan_manager start plan_run` 을 부릅니다. id 는 넘기지 않습니다 (대화 기록에 이 명령 줄이 남아 첫 단계가 읽습니다).
   - 없으면 `task_plan_manager start list_plans` 를 부릅니다 (이 작업 폴더의 계획 목록을 보이고 끝).
2. 결과 JSON 은 지시 하나입니다: `{"type", "node_uuid", "item_key", "payload"}`. `type` 대로 한 가지만 합니다. 내용은 `payload` 안에 있습니다.
   - `show`: `payload.text` 의 내용을 사용자에게 답변으로 알리고 `task_plan_manager next` 를 부릅니다. 명령의 결과(JSON)는 사용자에게 보이지 않으므로, 답변에 옮기지 않으면 사용자는 그 내용을 보지 못합니다.
   - `ask`: AskUserQuestion 으로 `payload.question` 과 `payload.choices` 를 그대로 묻습니다. 사용자의 답(고른 라벨 또는 직접 입력한 글)을 바꾸지 않고 `task_plan_manager done --answer "<답>"` 으로 넘깁니다.
   - `talk`: `payload.opening` 으로 대화를 시작해 `payload.goal` 을 향해 사용자와 이야기합니다. 충분하면 AskUserQuestion 으로 "정리할까요?" (예 / 더 이야기) 를 묻고, 예면 `task_plan_manager done` 을 부릅니다.
   - `spawn`: Agent 도구로 `payload.agent` 를 `payload.message` 그대로 띄웁니다. 백그라운드로 시작되면 완료 알림이 올 때까지 기다립니다. 서브에이전트가 끝난 뒤에 `task_plan_manager done` 을 부릅니다. 파일이 생긴 것만 보고 부르지 않습니다.
   - `finished`: `payload.text` 를 줄이거나 덧붙이지 않고 그대로 보이고 끝냅니다. 노드별 표가 들어 있습니다.
   - `wait`: 다른 명령이 단계를 실행 중입니다. `payload.text` 를 보이고 아무 명령도 부르지 않습니다. 앞 명령의 완료 알림이 오면 그 결과(지시)대로 이어 갑니다.
   - `failed`: `payload.text` 를 보이고 멈춥니다. 사용자가 다시 하자고 하면 `task_plan_manager next` 를 부릅니다.
3. `done` 의 결과도 다음 지시입니다. 2 를 반복합니다.
