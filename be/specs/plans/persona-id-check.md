# Plan: 페르소나 id 검사 (지식·계획·노드)

## 요청 스펙

두 번째 리뷰의 위험 2 에 대한 사용자 결정 (2026-11-20, "Check, 400"): 지식 만들기·고치기, 계획 만들기, 노드 만들기·고치기에서 persona_ids 에 없는(또는 지운) 페르소나가 있으면 400 으로 거절한다. 페르소나 목록의 수와 지우기의 "쓰는 곳" 검사가 늘 맞게 된다.

리뷰의 위험 1 에 대한 사용자 결정: 지식 PATCH 는 보낸 필드만 고친다. 바뀌지 않은 페르소나·근거 목록은 자식 행을 지우고 다시 넣지 않는다.

기존 동작을 바꾼다 (as-is → to-be)
- as-is: persona_ids 를 받은 그대로 저장한다
- to-be: 지우지 않은 페르소나가 아닌 id 가 하나라도 있으면 400 UnknownPersonaException, 메시지 "페르소나 3, 9 가 없습니다". 고치기에서 persona_ids 를 보내지 않으면 검사하지 않는다
- CLI 영향: CLI 는 서버에서 읽은 페르소나 가운데 고르므로 막히지 않는다. 확인 노드는 빈 목록이라 검사할 것이 없다

## Phase 1: 평가

### assess-api

충족. 요청·응답 모양은 그대로, 오류 하나가 는다.

### assess-usecase

부분 충족. 다섯 Usecase(MemoryCreate, MemoryUpdate, PlanCreate, PlanNodeCreate, PlanNodeUpdate)가 Writer 를 부르기 전에 PersonaRepository.find_missing_ids 로 본다. 다른 도메인의 Repository 주입이다 (허용).

### assess-infra

부분 충족.
- [신규] PersonaRepository.find_missing_ids(persona_ids: list[int]) -> list[int]: 지우지 않은 페르소나에 없는 id. 받은 순서, 겹치지 않게
- DefaultMemoryRepository.save: 수정 때 페르소나·근거 목록이 지금 값과 다를 때만 자식 행을 바꾼다

### assess-model

부분 충족. [신규] UnknownPersonaException (`exception/persona/unknown_persona_exception.py`, InvalidInputException 상속, 400).

## Phase 2: 구현 계획

1. add-model: UnknownPersonaException
2. add-infrastructure·add-query: find_missing_ids (PersonaEntityQuery.find_active_ids_in), DefaultMemoryRepository.save 고침
3. add-usecase: 다섯 Usecase 에 검사 (공통 함수 `service/persona/persona_check.py` require_personas)
4. 시험: 루트 conftest 의 truncate_all 이 id 도 처음으로 돌린다 (RESTART IDENTITY). `personas` 픽스처가 1 dankim-persona, 2 be-developer 를 만든다. 계획·지식 시험이 이것을 쓴다. 새 시험: 다섯 곳의 400, 지운 페르소나 400, PATCH 에서 안 보낸 목록의 자식 행 id 가 그대로

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-model: `exception/persona/unknown_persona_exception.py`
- add-infrastructure·add-query: PersonaRepository.find_missing_ids, PersonaEntityQuery.find_active_ids_in. DefaultMemoryRepository.save 는 페르소나·근거 목록이 바뀔 때만 자식 행을 바꾼다
- add-usecase: `service/persona/persona_check.py` require_personas. MemoryCreate, MemoryUpdate, PlanCreate, PlanNodeCreate, PlanNodeUpdate Usecase 에 PersonaRepository 주입과 검사
- 시험 기반: 루트 conftest 의 truncate_all 을 `RESTART IDENTITY` 로 (시험마다 id 가 1 부터), `personas` 픽스처 (1 dankim-persona, 2 be-developer). test_plan_api, test_memory_api 가 autouse 로 쓴다
- 검증: ruff, lint-imports, mypy(223 파일) 통과
- 시험: 3개 더해 모두 61개 통과 (계획·노드 만들기·노드 고치기 400 과 오류 모양, persona_ids 없이 상태만 바꾸면 통과, 지식 만들기·지운 페르소나·고치기 400, 안 바꾼 목록의 자식 행 id 가 그대로)
