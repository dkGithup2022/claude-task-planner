# engine: 실행 중인 단계 표시

명령(`start`, `next`, `done`)이 단계를 실행하는 동안 같은 실행에 다른 명령이 들어오면, 같은 단계를 또 실행하지 않고 기다리게 한다.
진행 방식: 계획 → 만들기 → 시험 → 단계 기록.

## 요청

- e2e test3 에서 같은 단계가 두 번 돌았다. 처음에는 계획이 둘(4, 5) 생겼고, 두 번째에는 make_plan 실행이 실패로 남았다.
- 원인은 세 가지가 겹친 것이다.
  - Claude Code 는 2분이 넘는 Bash 명령을 백그라운드로 넘긴다.
  - 그 사이 종료 훅이 "기다리는 지시 없음"을 "next 차례"로 읽고 종료를 막는다.
  - 그래서 메인 세션이 `next` 를 또 부른다.
- "가로 해서" (프로세스 번호를 함께 저장하고, 그 프로세스가 없으면 다시 실행) "이대로 하자" (사용자, 2026-11-19)

## 1. 입력과 받는 방식

- 명령은 지금과 같다: `task_plan_manager start <흐름> | next | done [--answer]`, 그리고 종료 훅(Stop).
- 새로 읽는 것: state.json 의 `executing`.

## 2. 출력과 내보내는 방식

- 실행 중에 두 번째 명령이 들어오면 지시 `wait` 를 출력한다.
  ```json
  {
    "type": "wait",
    "node_uuid": "502e976a-...",
    "item_key": null,
    "payload": {"text": "split_plan 을 실행 중입니다 (2026-11-19T09:12:38Z 시작). 앞 명령의 완료 알림을 기다리세요."}
  }
  ```
- 종료 훅: 실행 중인 단계가 있고 그 프로세스가 살아 있으면 막지 않는다(`{}`).

## 3. 데이터

state.json 에 `executing` 을 더한다. 단계를 실행하는 동안만 채운다.
```json
{
  "run_id": "r_20261119_091058",
  "status": "running",
  "waiting_instruction": null,
  "executing": {"node_uuid": "502e976a-...", "item_key": null, "pid": 77458, "started_at": "2026-11-19T09:12:38Z"},
  ...
}
```
- 단계가 완료, 지시 대기, 실패로 끝나면 null 로 바꾼다. 예전 state.json 에 이 값이 없으면 null 로 본다.
- 프로세스가 사라져 다시 실행할 때는 history.jsonl 에 한 줄을 남긴다. 그 줄의 note 는 "앞 실행(pid 77458)이 끝나지 않고 사라져 다시 실행" 이다.

노드 상태(NodeStatus)에 두지 않는 이유가 있다. 반복 단계는 노드 하나를 모든 항목이 같이 쓰고, 항목별 진행은 `done_items` 로 따진다. 그래서 실행 하나에 필드 하나로 둔다. 한 실행에서 engine 이 동시에 실행하는 단계는 늘 하나다.

## 4. 파일 트리

```
src/task_plan_manager/engine/
├─ model/run_state/executing_step.py        새로: ExecutingStep, is_alive()
├─ model/run_state/flow_run_state.py        executing 필드
├─ port/run_state/run_state_file_converter.py  executing 읽고 쓰기
├─ instruction/instruction_type.py          WAIT
├─ instruction/instruction.py               Instruction.wait(), WAIT 의 내용은 ShowRequest
├─ runner/unit/default_unit_runner.py       실행 직전 표시, 완료·대기·실패에서 지움
├─ runner/flow/default_flow_runner.py       next·done 맨 앞에서 실행 중인 단계 확인
└─ hook/stop_hook.py                        실행 중이면 막지 않음
plugin/skills/run/SKILL.md                  wait 처리, Bash 제한 시간 10분
tests/engine/test_executing_step.py         새로: 시험 4개
```

## 5. 프롬프트

없음. run 스킬에 두 줄을 더한다.
- `wait`: `payload.text` 를 보이고 아무 명령도 부르지 않습니다. 앞 명령의 완료 알림이 오면 그 결과(지시)대로 이어 갑니다.
- (첫머리) `task_plan_manager` 명령은 Bash 제한 시간 600000(10분)으로 부릅니다.

## 6. 코드 요지

- 단계 실행기: `perform` 직전에 `executing` 을 채워 저장한다. `_complete`, `_wait`, `_fail` 은 저장하기 전에 `executing = None` 으로 바꾼다.
- 흐름 실행기: `next_instruction` 과 `submit_reply` 의 맨 앞에서 `executing` 을 본다.
  - 살아 있으면 `wait` 지시를 돌려준다.
  - 사라졌으면 지우고 history 에 남긴다. 그 단계는 아직 완료되지 않았으므로 그대로 다시 실행된다.
- 종료 훅: 실행 중이고 살아 있으면 None.

## 남는 한계 (이번 범위 밖)

- 단계가 계획 저장소에 반영한 직후, 완료로 기록되기 전에 죽으면 다시 실행할 때 같은 일을 또 한다. 그 단계가 스스로 막아야 한다.
- 죽은 프로세스의 번호를 다른 프로세스가 받으면 살아 있다고 볼 수 있다.

## 진행 기록

- 2026-11-19 만듦. 시험 5개(실행 중이면 wait, 사라진 실행은 다시, 단계마다 표시 지움, 예전 state.json 읽기, 실행 중 취소 막기). 검증 통과 (pytest 125개, ruff, lint-imports, mypy)

## 단계 기록

1. 입력: 명령과 종료 훅은 그대로. state.json 의 `executing` 을 새로 읽는다.
2. 출력: 실행 중에 들어온 명령은 `wait` 지시. 종료 훅은 실행 중이면 막지 않는다.
3. 파일: `executing_step.py` 새로. 실행 상태, 변환기, 지시 종류, 단계 실행기, 흐름 실행기, 종료 훅, cli, 스킬 셋(run, plan-go, plan-cancel)을 바꿈.
4. 별도 에이전트 리뷰: (1) 실행 중에 `cancel` 을 부르면, 실행 중이던 명령이 끝나며 취소를 덮어씀 → `cancel` 도 실행 중 단계를 먼저 보게 고침. (2) 재부팅 뒤 프로세스 번호가 재사용되면 계속 기다림 → 드물어서 `shortcut:` 주석으로 남김.
5. 남은 것: 실제 Claude Code 에서 2분 넘는 단계로 확인하는 시험(e2e)은 아직 안 함.
