# Plan: GET /api/personas

## 요청 스펙

페르소나 목록. CLI 는 계획 만들기에서 담당을 고를 때 읽고, 웹 4번 화면은 페르소나마다 지식 수와 계획 수를 함께 보인다. 출처: `corbina/notes/2026-11-20-api.md` 2절, `2026-11-20-ui.md` 4절.

응답 `{"personas": [{"persona_id": 1, "name": "dankim-persona", "description": "...", "memory_count": 7, "plan_count": 10}]}`

CLI 기준 코드: `persona_api_converter.py` `to_personas` 가 personas 의 persona_id, name, description 만 읽는다. 더한 두 수는 읽지 않으므로 깨지지 않는다. 다른 점: 없음.

## Phase 1: 평가

### assess-api

미충족. [Reader] PersonaReader.get_all() -> list[PersonaRead]. 응답 PersonaListResponse(personas: list[PersonaResponse]). persona_id 순. 200.

### assess-usecase

미충족. PersonaReader 가 없다.
- infrastructure 신규: PersonaRepository.find_all() -> list[PersonaRead] (지식 수·계획 수 포함)

### assess-infra

미충족. PersonaRepository 가 없다.
- [신규] PersonaRepository (Pattern Bar): find_all
- 수 세기는 다른 aggregate(지식, 계획, 노드)에 걸치므로 PersonaJoinQuery 에 SQL 로 쓴다
  - memory_count: 지우지 않은 지식 가운데 memory_personas 에 이 페르소나가 있는 것
  - plan_count: 지우지 않은 계획 가운데 참여 페르소나(plan_personas)에 있거나, 지우지 않은 노드의 담당(plan_node_personas)에 있는 것. 지우기를 막을 때 노드 담당만 쓰는 계획도 "쓰는 계획" 이기 때문이다

Entity 와 테이블
- personas: id, name(VARCHAR 255), description(Text), 공통 4컬럼
- 이름 중복을 막는다 (사용자, 2026-11-20). 지운 페르소나의 이름은 다시 쓸 수 있게, 지우지 않은 행에만 유일 조건을 건다 (부분 유일 인덱스 `uq_personas_name_active`)

### assess-model

충족. Persona, PersonaRead(memory_count, plan_count) 가 있다.

## Phase 2: 구현 계획

1. add-infrastructure: PersonaRepository.find_all
2. add-entity-specs: PersonaEntity, migration `persona`
3. add-query: PersonaJoinQuery (+ 행 dataclass PersonaWithCountsRow), DefaultPersonaRepository. JoinQuery 메서드는 시험으로 SQL 을 확인한다
4. add-usecase: PersonaReader, DefaultPersonaReader, PersonaProvider
5. add-api: persona_router GET, PersonaResponse, PersonaListResponse
6. 시험: 지식·계획·노드 담당으로 센 수, 지운 지식·계획·노드는 세지 않음, 지운 페르소나 빠짐, id 순

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: `infrastructure/persona/persona_repository.py` (find_all)
- add-entity-specs: PersonaEntity (personas, 부분 유일 인덱스 `uq_personas_name_active`), migration `persona`. `alembic check` 통과
- add-query: PersonaJoinQuery·PersonaWithCountsRow (SQL, 지식·계획·노드 담당을 센다), PersonaEntityQuery, DefaultPersonaRepository
- add-usecase: `service/persona/` PersonaReader, DefaultPersonaReader, `app/providers/persona_provider.py`
- add-api: `api/persona/persona_router.py` GET, PersonaResponse, PersonaListResponse, ROUTERS 에 persona_router
- 검증: ruff, lint-imports, mypy(209 파일) 통과
- 시험: `test_persona_api.py` 2개 (JoinQuery SQL: 지식 수·참여/노드 담당 계획 수, 지운 지식·노드·페르소나 제외, id 순 / 빈 목록). 모두 48개 통과
