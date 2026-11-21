# engine: 마지막 보이기 글을 끝 지시에 싣기

흐름의 마지막 단계가 보이기(show)이면, 그 글을 따로 보내지 않고 끝(finished) 지시의 글로 보낸다.
진행 방식: 계획 → 만들기 → 시험 → 단계 기록.

## 요청

- e2e test3 의 불허 흐름에서 생긴 일이다. 알림 단계가 "…을 불허했습니다. 이 계획은 끝났습니다. 저장한 지식 0개"를 보이기 지시로 냈다. 그런데 메인 세션은 그 뒤에 온 끝 지시의 "끝났습니다."만 받아 "절차가 모두 끝났습니다"라고 답했다.
- "가. 끝 지시에 알림 문구를 싣기" 로 반영 (사용자, 2026-11-19).

## 1. 입력과 받는 방식

- 지금과 같다: `next`, `done`. 바뀌는 것은 engine 이 돌려주는 지시뿐이다.

## 2. 출력과 내보내는 방식

지금은 지시가 두 번 나간다.
```json
{"type": "show", "node_uuid": "8da0b35a-...", "item_key": "-", "payload": {"text": "계획 6 \"…\" 을 불허했습니다. 이 계획은 끝났습니다. 저장한 지식 0개 (새로 0, 덧붙이기 0)."}}
{"type": "finished", "node_uuid": "bcaea094-...", "item_key": null, "payload": {"text": "끝났습니다."}}
```
바꾸면 지시가 한 번만 나간다.
```json
{"type": "finished", "node_uuid": "bcaea094-...", "item_key": null, "payload": {"text": "계획 6 \"…\" 을 불허했습니다. 이 계획은 끝났습니다. 저장한 지식 0개 (새로 0, 덧붙이기 0)."}}
```
- 마지막 단계가 보이기가 아니면 지금처럼 "끝났습니다." 를 보낸다.
- 해당하는 흐름은 plan_go 와 plan_cancel(알림), make_plan(계획 보이기), list_plans(목록 보이기), demo 다.

## 3. 데이터

- 바뀌지 않는다. 보이기 단계는 지금처럼 완료로 기록되고(history, result.json), 실행 상태는 finished 가 된다.

## 4. 파일 트리

```
src/task_planner/engine/
├─ runner/unit/default_unit_runner.py   보이기를 완료한 뒤 다음 차례가 없으면 끝 지시로 바꿔 돌려줌
└─ runner/flow/default_flow_runner.py   단계 실행기가 끝 지시를 돌려주면 그 글로 실행을 끝냄
tests/                                   마지막 show → finished 를 기대하던 시험을 고침
```
흐름 코드와 스킬은 바꾸지 않는다. run 스킬은 이미 "`finished`: `payload.text` 를 보이고 끝냅니다" 이다.

## 5. 프롬프트

없음.

## 6. 코드 요지

- 단계 실행기: 보이기 단계를 완료한 뒤 `_find_next` 로 다음 차례를 본다. 없으면 `Instruction.finished(루트 uuid, 보이기 글)` 을 돌려준다.
- 흐름 실행기 `_advance`: 단계 실행기가 끝 지시를 돌려주면, 지금 None 일 때 하는 끝 처리(상태 finished, 활성 실행 지우기)를 하고 그 지시를 돌려준다.

## 진행 기록

- 2026-11-19 만듦. engine 두 곳(단계 실행기, 흐름 실행기). 흐름 코드와 스킬은 그대로. 마지막 show 뒤 next → finished 를 기대하던 시험 12개를 "finished 에 글이 실림"으로 고침. 검증 통과 (pytest 125개, ruff, lint-imports, mypy)

## 단계 기록

1. 입력: 그대로.
2. 출력: 흐름의 마지막 단계가 보이기면, 지시가 show 와 finished 두 번이 아니라 그 글을 실은 finished 한 번으로 나간다. 마지막이 보이기가 아니면 "끝났습니다." 그대로.
3. 파일: `default_unit_runner.py` (`_finish_with_last_show`), `default_flow_runner.py` (`_advance`), `unit_runner.py` 설명, 시험 7개 파일.
4. 별도 에이전트 리뷰: 보이기 뒤의 다음 차례를 찾다가 오류(실행 조건, 반복 항목 계산)가 나면, 이미 끝난 보이기가 실패로 바뀌고 다시 나감 → 찾기 전에 완료한 노드를 비워, 실패가 지금처럼 루트 노드에 남게 고침. 그 밖의 경로(반복 안의 마지막 보이기, 건너뛴 단계만 남은 경우, 답 넘기기 경로, 종료 훅, 스킬 셋)는 지적 없음.
5. 남은 것: 실제 Claude Code 에서 불허 흐름을 다시 돌려 알림 글이 보이는지 확인 (e2e).
