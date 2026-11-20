# Plan: DELETE /api/personas/{persona_id}

## 요청 스펙

페르소나 지우기 (웹 4번 화면의 [삭제]). 그 페르소나를 쓰는 지식이나 계획이 있으면 막고 "지식 7개, 계획 10개가 이 페르소나를 씁니다" 처럼 알린다 (사용자, 2026-11-20: "a"). 출처: `corbina/notes/2026-11-20-ui.md` 4절. 정한 모양: 204. 없으면 404, 쓰는 곳이 있으면 409 PersonaInUseException (message 에 위 문구).

## Phase 1: 평가

### assess-api

미충족. [Usecase] PersonaDeleteUsecase.execute(identity) -> None. DELETE, 204.

### assess-usecase

부분 충족.
- [신규] PersonaDeleteUsecase: PersonaRepository.find_by_id 로 수를 읽고, 없으면 404, memory_count 나 plan_count 가 0 보다 크면 PersonaInUseException(409), 아니면 writer.delete. @transactional
- [신규] PersonaWriter.delete(identity): 선검증(404) → delete_by_id
- "쓰는 계획" 은 목록과 같은 기준이다: 참여 페르소나이거나 지우지 않은 노드의 담당
- infrastructure 신규: PersonaRepository.find_by_id (수 포함), delete_by_id

### assess-infra

부분 충족.
- find_by_id(identity) -> PersonaRead | None: PersonaJoinQuery 에 id 로 거른 SQL 을 더한다 (목록과 같은 SELECT)
- delete_by_id(identity) -> None: soft-delete. 지운 페르소나의 이름은 부분 유일 인덱스 밖이므로 다시 쓸 수 있다

### assess-model

충족. PersonaInUseException(persona_id, memory_count, plan_count).

## Phase 2: 구현 계획

1. add-infrastructure → 2. add-query (JoinQuery _BY_ID, EntityQuery) → 3. add-usecase → 4. add-api → 5. 시험: 안 쓰는 페르소나 204 후 목록에서 빠짐·이름 다시 쓰기, 지식·계획이 쓰면 409 와 문구, 없는 페르소나 404

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- PersonaRepository.find_by_id (PersonaJoinQuery.find_by_id_with_counts), delete_by_id
- PersonaWriter.delete, `usecase/persona_delete_usecase.py` (쓰는 곳 검사), Provider 갱신
- DELETE /{persona_id} (204)
- 검증: ruff, lint-imports, mypy(219 파일) 통과. 시험 3개 더해 모두 56개 통과 (안 쓰는 페르소나 지우기·이름 다시 쓰기, 지식 2·노드 담당 계획 1 → 409 와 문구, 없는 페르소나 404)
