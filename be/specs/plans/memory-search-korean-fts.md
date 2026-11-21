# Plan: 지식 검색을 한국어 형태소 기반 전문 검색으로 (POST /api/memories/search 아래)

## 요청 스펙
/Users/dankim/orca/workspaces/productivility/task-plan-server/be 에서 지식 검색을 한국어 형태소 기반 전문 검색으로 바꾼다. API 경로와 요청·응답 모양은 그대로다 (POST /api/memories/search, POST /api/memories, PATCH /api/memories/{memory_id}). 정한 것(사용자, 2026-11-21, corbina/notes/2026-11-21-search-design.md 4절): memories 테이블에 search_tokens(tsvector, 'simple', 작업 이름 낱말 무게 A·본문 낱말 무게 B, GIN 인덱스) 열을 더한다. 마이그레이션에서 vector, pg_trgm 확장도 켠다(DB 이미지는 pgvector/pgvector:pg16 로 이미 바꿨다). 낱말은 kiwipiepy 로 만든다: infrastructure/memory/text_tokenizer.py 의 TextTokenizer.tokens(text) 인터페이스, persistence/memory/kiwi_text_tokenizer.py 의 kiwi 구현(명사·영문·동사·형용사 어간만, 한 번만 띄움). model/memory/memory_search_terms.py 에 MemorySearchTerms(theme, body) 값만 둔다. service/memory/search_terms/ 에 낱말 만드는 규칙(memory_search_terms_of, query_terms_of)을 두고 저장과 검색이 같이 쓴다. DefaultMemoryWriter 의 create, update 가 저장할 때마다 낱말을 다시 만들어 MemoryRepository.save(memory, terms) 로 내린다. 검색은 usecase 가 검색어를 낱말로 바꿔 KnowledgeSearcher 에 넘기고, 검색 구현은 search_tokens @@ 낱말 OR 질의 + ts_rank 순으로 바꾼다. 이미 있는 지식은 한 번 채운다. 웹 목록(GET /api/memories)은 이번에 바꾸지 않는다.

데이터 스펙 변경 (search_tokens 열, MemorySearchTerms, TextTokenizer, MemoryRepository.save(memory, terms), KnowledgeSearcher 가 검색어 낱말을 받음) 은 사용자 승인 2026-11-21.

## Phase 1: 평가

### assess-api

1. 충족 여부: 충족 (API 층 변경 없음)
   - `POST /api/memories/search`, `POST /api/memories`, `PATCH /api/memories/{memory_id}` 가 이미 있고 (specs/api.md 65·78·91 행), 요청·응답 모양을 바꾸지 않는다
   - 이번 요청은 API 아래(검색 방식, 저장할 때 낱말 만들기)를 바꾸는 일이라 하위 평가를 이어 간다
2. 하위 레이어에 필요한 기능
   - A. service
     - 기존 사용: `MemoryReader.search(search_param)`, `MemoryCreateUsecase.execute`, `MemoryUpdateUsecase.execute` (시그니처 그대로)
     - 동작 변경 요청: `DefaultMemoryWriter.create`, `update` 가 저장할 때마다 검색용 낱말을 만들어 내린다. `DefaultMemoryReader.search` 가 검색어를 낱말로 바꿔 검색에 넘긴다
   - B. model: API 응답에 쓰는 `MemorySearchHit`, `MemoryRead` 그대로. 검색용 값 `MemorySearchTerms` 는 아래 층의 요청 (사용자 승인 2026-11-21)
3. 현재 레이어 작업 계획: 없음. 라우터(`api/memory/memory_router.py`), Request·Response DTO 그대로. 점수(`score`) 의 값 범위만 바뀐다 (아래 Phase 2)

### assess-usecase

1. 충족 여부: 부분 충족 (메서드 시그니처는 그대로, 구현과 의존이 바뀜)
2. 하위 레이어에 필요한 기능
   - A. infrastructure (사용자 승인 2026-11-21)
     - 기존 사용: `MemoryRepository.find_write_by_id`, `delete_by_id`, `find_by_condition` (채우기에서 모든 지식 읽기)
     - 변경 요청 (쓰기): `MemoryRepository.save(memory: Memory, terms: MemorySearchTerms) -> Memory`. 지식과 함께 검색용 낱말을 저장한다
     - 신규 요청 (쓰기): `MemoryRepository.save_search_terms(identity: MemoryIdentity, terms: MemorySearchTerms) -> None`. 이미 있는 지식의 낱말만 채운다 (한 번 채우기용). 고친 시각은 바꾸지 않는다
     - 변경 요청 (읽기): `KnowledgeSearcher.search_knowledge(search_param: SearchParam, query_terms: tuple[str, ...]) -> list[MemorySearchHit]`. 검색어 낱말로 찾는다. 낱말이 없으면 지금처럼 고친 시각 최근 순
     - 신규 요청 (포트): `TextTokenizer.tokens(text: str) -> tuple[str, ...]`. 검색에 쓸 낱말 (명사, 영문, 동사·형용사 어간). kiwi 구현은 persistence
   - B. model (사용자 승인 2026-11-21)
     - 신규: `MemorySearchTerms(theme: tuple[str, ...], body: tuple[str, ...])` 값만
     - 기존 사용: `Memory`, `SearchParam`, `MemorySearchHit` 그대로
3. 현재 레이어 작업 계획
   - [신규] `service/memory/search_terms/memory_search_terms_of.py`: `memory_search_terms_of(tokenizer, theme, body) -> MemorySearchTerms`. 저장(인덱싱)용
   - [신규] `service/memory/search_terms/query_terms_of.py`: `query_terms_of(tokenizer, query) -> tuple[str, ...]`. 검색용. 겹친 낱말은 한 번만
   - [변경] `DefaultMemoryWriter(tx, repository, tokenizer)`: `create`, `update` 가 저장 직전에 `memory_search_terms_of` 로 낱말을 만들어 `repository.save(memory, terms)`. 저장할 때마다 다시 만든다. `@transactional` 안에서 (낱말 만들기는 DB 를 쓰지 않는다). 시그니처·반환 그대로
   - [변경] `DefaultMemoryReader(repository, searcher, tokenizer)`: `search` 가 `query_terms_of(tokenizer, search_param.query)` 로 낱말을 만들어 `searcher.search_knowledge(search_param, terms)`. 시그니처·반환 그대로
   - [신규] 한 번 채우기: `MemorySearchTermsRefreshUsecase.execute() -> int` (채운 지식 수). 지운 것 빼고 낱말이 빈 지식을 읽어 낱말을 만들어 `save_search_terms`. `@transactional`. 라우터에는 내지 않고 서버가 시작할 때 app 의 lifespan 이 부른다 (사용자, 2026-11-21)
   - 소유권 체크: 없음 (인증 없는 서버)
   - DI: `MemoryProvider` 에 `TextTokenizer` (앱 전체에서 하나, Scope.APP), `MemorySearchTermsRefreshUsecase`

### assess-infra

1. 충족 여부: 부분 충족 (기존 ABC 두 개 변경, 메서드 하나 추가, 포트 하나 신규. 사용자 승인 2026-11-21)
2. 하위 레이어에 필요한 기능
   - A. model
     - 신규 (VO): `MemorySearchTerms(theme: tuple[str, ...], body: tuple[str, ...])`. 지식 하나의 검색용 낱말. 작업 이름에서 나온 것과 본문에서 나온 것을 나눠 둔다 (저장할 때 무게 A, B 를 따로 붙이려고). 바깥 의존 없음
     - 기존 사용: `Memory`, `MemoryIdentity`, `SearchParam`, `MemorySearchHit` 그대로
3. 현재 레이어 작업 계획 (as-is / to-be)
   - [변경] `MemoryRepository.save`
     - as-is: `save(memory: Memory) -> Memory`
     - to-be: `save(memory: Memory, terms: MemorySearchTerms) -> Memory`. 쓰기. 지식과 낱말을 같이 저장
   - [신규] `MemoryRepository.save_search_terms(identity: MemoryIdentity, terms: MemorySearchTerms) -> None`. 쓰기. 낱말만 바꾼다. 고친 시각은 그대로. 지운 지식이면 아무것도 하지 않는다
   - [변경] `KnowledgeSearcher.search_knowledge`
     - as-is: `search_knowledge(search_param: SearchParam) -> list[MemorySearchHit]`
     - to-be: `search_knowledge(search_param: SearchParam, query_terms: tuple[str, ...]) -> list[MemorySearchHit]`. 읽기. 거르기(종류, 페르소나 겹침, theme, 지운 것 뺌)는 그대로. 낱말이 하나라도 맞는 지식을 맞은 정도 순으로. 낱말이 없으면 고친 시각 최근 순 (지금과 같음)
   - [신규] 포트 `TextTokenizer` (`infrastructure/memory/text_tokenizer.py`): `tokens(text: str) -> tuple[str, ...]`. 검색에 쓸 낱말 (명사, 영문, 동사·형용사 어간). 나온 순서대로, 겹쳐도 그대로
   - 원자적 연산: 없음. Stats 분리: 없음
   - 어댑터 갱신 필요: 있음. `DefaultMemoryRepository`, `DefaultKnowledgeSearcher` 를 add-query 에서 바꾸고, `KiwiTextTokenizer` 를 새로 둔다

### assess-model

1. 충족 여부: 부분 충족 (VO 하나 신규. 기존 모델 변경 없음. 사용자 승인 2026-11-21)
2. 현재 레이어 작업 계획
   - [신규 VO] `MemorySearchTerms` (`model/memory/memory_search_terms.py`)
     - 필드: `theme: tuple[str, ...]` (작업 이름에서 나온 낱말), `body: tuple[str, ...]` (본문에서 나온 낱말)
     - `@dataclass(frozen=True, slots=True)`, 팩토리·상태 변경 없음. 바깥 의존 없음
   - `Memory`, `MemoryRead`, `SearchParam`, `MemorySearchHit` 는 바꾸지 않는다. 검색용 낱말은 읽는 쪽(웹, CLI)에 보일 필요가 없어 `Memory` 에 넣지 않는다
   - 새 예외 없음

## Phase 2: 구현 계획

### 평가 결과
- api: 충족. 경로·요청·응답 그대로 (점수 값의 범위만 바뀜, 아래)
- service: 부분 충족. Writer·Reader 구현이 낱말을 만들어 내림, 낱말 규칙 두 함수, 한 번 채우기 Usecase
- infra: 부분 충족. `MemoryRepository.save(memory, terms)`, `save_search_terms`, `KnowledgeSearcher.search_knowledge(search_param, query_terms)`, 포트 `TextTokenizer`
- model: 부분 충족. VO `MemorySearchTerms`

### 설계 결정
- 의존성: `kiwipiepy` (0.25.x) 를 `packages/persistence/pyproject.toml` 에 더한다 (구현이 persistence 에 있으므로). `uv.lock` 갱신. 모델 패키지 `kiwipiepy_model` 88MB 가 따라와 서버 이미지가 그만큼 커진다
- kiwi 구현 `KiwiTextTokenizer` (`persistence/memory/kiwi_text_tokenizer.py`): `Kiwi()` 를 한 번 만들어 둔다. 남기는 품사: 일반·고유 명사(NNG, NNP), 영문(SL), 한자(SH), 동사·형용사 어간(VV, VA). 의존 명사(NNB, "것", "수"), 숫자(SN), 조사·어미·문장 부호는 뺀다. 영문은 소문자로
  - 잰 값 (맥, kiwipiepy 0.25.1): 처음 띄우는 데 1.3 초, 메모리 최대 약 480MB, 문장 하나 0.2ms
- DI: `MemoryProvider` 에 `provide(KiwiTextTokenizer, provides=TextTokenizer, scope=Scope.APP)` (앱 전체에서 하나). `DefaultMemoryWriter`, `DefaultMemoryReader` 가 받는다. 처음 쓰는 요청에서 띄운다
- 저장: `DefaultMemoryRepository.save(memory, terms)` 가 `search_tokens` 에 `setweight(to_tsvector('simple', 작업 이름 낱말을 공백으로 이은 글), 'A') || setweight(to_tsvector('simple', 본문 낱말), 'B')` 를 넣는다. `save_search_terms` 도 같은 식으로 그 열만 바꾸고 `updated_at` 은 그대로
- 검색: `DefaultKnowledgeSearcher.search_knowledge(search_param, query_terms)`
  - 거르기(종류, 페르소나 겹침, theme, 지운 것 뺌)는 그대로
  - 낱말이 있으면: 낱말마다 `plainto_tsquery('simple', 낱말)` 을 `||`(OR) 로 이은 질의로 `search_tokens @@ 질의`, 점수는 `ts_rank(search_tokens, 질의, 32)` (0~1), 점수 높은 순, 같으면 고친 시각 최근 순, limit. 낱말을 SQL 글로 잇지 않아 따옴표·기호가 섞여도 안전하다
  - 낱말이 없으면 (검색어가 비었거나 조사만 있음): 지금처럼 고친 시각 최근 순, 점수 0
  - `text_match_score.py` 는 지운다
- migration `memory_search_tokens` (down_revision: 지금 head `f6618d7f484f`)
  - `CREATE EXTENSION IF NOT EXISTS vector`, `CREATE EXTENSION IF NOT EXISTS pg_trgm`
  - `memories.search_tokens TSVECTOR NOT NULL DEFAULT ''::tsvector`
  - GIN 인덱스 `ix_memories_search_tokens`
  - entity 에도 같은 열과 인덱스(`__table_args__`)를 적어 `alembic check` 가 통과하게 한다
  - downgrade: 인덱스와 열을 지운다. 확장은 다른 곳에서 쓸 수 있어 지우지 않는다
- 이미 있는 지식 채우기 (사용자, 2026-11-21 "a 로 해주세요"): 서버가 시작할 때 `search_tokens` 가 빈 지식만 스스로 채운다
  - 낱말은 파이썬(kiwi)이 만들므로 migration 만으로는 채울 수 없다
  - `MemorySearchTermsRefreshUsecase.execute() -> int` (채운 수): 지운 것 빼고 낱말이 빈 지식을 읽어 낱말을 만들어 `save_search_terms`. 고친 시각은 그대로
  - `MemoryRepository.find_ids_without_search_terms() -> list[MemoryIdentity]` 를 더한다 (낱말이 빈 지식만 읽으려고)
  - app 의 lifespan 이 시작할 때 한 번 부르고 채운 수를 로그로 남긴다. `scripts/import_mock_data.py` 로 직접 넣은 지식도 다음 시작 때 채워진다
- 점수 값 (as-is / to-be): 응답 모양은 그대로, 값의 뜻만 바뀐다
  - as-is: 낱말마다 작업 이름 2, 본문 1 을 더해 (낱말 수 × 3) 으로 나눈 0~1
  - to-be: `ts_rank(…, 32)` 의 0~1. 같은 결과라도 숫자가 작게 나온다. CLI 는 점수를 순서로만 쓴다
- 시험
  - `be/conftest.py` 의 시험 DB 이미지 `postgres:16-alpine` → `pgvector/pgvector:pg16` (migration 의 `CREATE EXTENSION vector` 가 alpine 이미지에서 실패한다)
  - 기존 `packages/app/tests/test_memory_api.py` 의 검색 시험 세 개는 그대로 통과해야 한다 (점수 순서와 0 보다 큼만 본다)
  - 더할 시험: 조사가 붙어도 찾음 ("설계에서" 로 "설계" 지식), 고치면 낱말이 다시 만들어짐 (본문을 바꾼 뒤 새 낱말로 찾음), 검색어가 비면 고친 시각 순, 채우기 Usecase 가 비어 있는 지식을 채움, `KiwiTextTokenizer` 의 품사 거르기 (`packages/persistence/tests`)
- 문서: specs/models.md, infrastructure.md, repository.md, schema.md, usecase.md
- 웹 목록(`GET /api/memories`)은 바꾸지 않는다

### 구현 순서 (역순)
1. add-model: `MemorySearchTerms`
2. add-infrastructure: `TextTokenizer` 신규, `MemoryRepository.save(memory, terms)` 변경, `save_search_terms` 신규, `KnowledgeSearcher.search_knowledge(search_param, query_terms)` 변경
3. add-entity-specs: `MemoryEntity.search_tokens` 와 GIN 인덱스, migration `memory_search_tokens` (확장 두 개 포함)
4. add-query: `DefaultMemoryRepository.save`·`save_search_terms`, `DefaultKnowledgeSearcher` 를 전문 검색으로, `KiwiTextTokenizer` 신규, `text_match_score.py` 지움, persistence 의존성 `kiwipiepy`
5. add-usecase: `service/memory/search_terms/` 두 함수, `DefaultMemoryWriter`·`DefaultMemoryReader` 가 tokenizer 를 받음, `MemorySearchTermsRefreshUsecase`, `MemoryProvider` 등록
6. app lifespan 에서 시작할 때 채우기, 시험 DB 이미지, 시험, 개발 DB·배포 DB 에 migration 과 채우기 실행
- add-api: 없음

### 정한 것 (사용자, 2026-11-21)
1. 이미 있는 지식 채우기: 서버가 시작할 때 낱말이 빈 지식만 스스로 채운다 (위 설계)
2. kiwi 의 메모리 약 480MB: 그대로 간다 (Docker 에 3.8GB, 지금 컨테이너 넷을 합쳐 약 170MB)

## Phase 3: 구현 진행

### 1. add-model (2026-11-21)
- 만든 파일: `packages/model/src/task_plan_server/model/memory/memory_search_terms.py` (`MemorySearchTerms(theme, body)`, frozen slots dataclass, 바깥 의존 없음)
- 예외·Identity 없음 (기존 memory 도메인 아래의 VO)
- specs/models.md 에 MemorySearchTerms 절
- 검증: ruff check 통과, mypy 통과 (224 files)

### 2. add-infrastructure (2026-11-21)
- 만든 파일: `packages/infrastructure/src/task_plan_server/infrastructure/memory/text_tokenizer.py` (`TextTokenizer.tokens(text) -> tuple[str, ...]`)
- 바꾼 파일 (사용자 승인 2026-11-21)
  - `memory_repository.py`: `save(memory)` → `save(memory, terms)`. `save_search_terms(identity, terms)`, `find_ids_without_search_terms()` 를 더함 (시작할 때 채우기용)
  - `knowledge_searcher.py`: `search_knowledge(search_param)` → `search_knowledge(search_param, query_terms)`
- 어댑터 갱신 필요: `DefaultMemoryRepository`, `DefaultKnowledgeSearcher` (add-query), 부르는 쪽 `DefaultMemoryWriter`, `DefaultMemoryReader` (add-usecase)
- specs/infrastructure.md 갱신
- 검증: ruff 통과, lint-imports 2 kept. mypy 는 부르는 쪽 3 곳(writer 2, reader 1)의 인자 부족만 남음 (add-usecase 에서 맞춘다)

### 3. add-entity-specs (2026-11-21)
- 바꾼 파일: `packages/persistence/src/task_plan_server/persistence/memory/memory_entity.py` — `search_tokens: TSVECTOR NOT NULL server_default ''::tsvector` (deferred, 도메인 변환에 쓰지 않음), `__table_args__` 에 GIN 인덱스 `ix_memories_search_tokens`
- migration `packages/schema/alembic/versions/20261121_fc4ad6b1e3bd_memory_search_tokens.py` (revision `fc4ad6b1e3bd`, down `f6618d7f484f`): `CREATE EXTENSION IF NOT EXISTS vector`, `pg_trgm`, 열, GIN 인덱스. downgrade 는 인덱스와 열만
- 개발 DB(be-db-1): upgrade head → `alembic check` "No new upgrade operations detected" → downgrade -1 → upgrade head 왕복 확인. 확장 vector, pg_trgm 켜짐. 낱말이 빈 지식 7 개 (시작할 때 채우기 대상)
- specs/schema.md, specs/repository.md 갱신
- 검증: ruff check·format 통과

### 4. add-query (2026-11-21)
- 바꾼 파일
  - `memory_entity_query.py`: `find_for_search_by_terms_and_active` (낱말 OR 질의 `@@`, `ts_rank(…, 32)` 순, 같으면 고친 시각 최근 순, limit), `update_search_tokens_by_id_and_active` (updated_at 을 지금 값 그대로 넣어 onupdate 를 막음), `find_ids_without_search_tokens_and_active` (`length(search_tokens) = 0`), `search_tokens_of(terms)` (무게 A·B)
  - `memory_repository.py`: `save(memory, terms)` 가 새로 만들 때와 고칠 때 모두 `search_tokens` 를 넣음, `save_search_terms`, `find_ids_without_search_terms`
  - `default_knowledge_searcher.py`: 전문 검색으로. 낱말이 없으면 고친 시각 최근 순, 점수 0
- 만든 파일: `kiwi_text_tokenizer.py` (`KiwiTextTokenizer`)
- 지운 파일: `text_match_score.py` (다른 곳에서 쓰지 않음)
- 의존성: `packages/persistence/pyproject.toml` 에 `kiwipiepy>=0.25`. `uv.lock` 갱신 (kiwipiepy, kiwipiepy_model, numpy, tqdm 추가)
- 실제 나누기: "API 설계에서 에러 코드를 정한 것은 3개의 REST 엔드포인트다. 걸어 두었다" → api, 설계, 에러, 코드, 정하, rest, 엔드, 포인트, 걸 ("것"·숫자·조사 빠짐. "엔드포인트" 는 문맥에 따라 둘로 나뉘기도 하지만 저장과 검색이 같은 규칙이라 맞는다)
- Provider 에 더할 것 (add-usecase): `provide(KiwiTextTokenizer, provides=TextTokenizer, scope=Scope.APP)`
- specs/repository.md 갱신
- 검증: ruff check·format 통과, lint-imports 2 kept. mypy 는 service 부르는 쪽 3 곳만 남음

### 5. add-usecase (2026-11-21)
- 만든 파일: `service/memory/search_terms/memory_search_terms_of.py`, `query_terms_of.py`, `service/memory/usecase/memory_search_terms_refresh_usecase.py`
- 바꾼 파일
  - `default_memory_writer.py`: tokenizer 를 받아 create·update 가 `save(memory, self._search_terms(memory))` (저장할 때마다 다시 만든다)
  - `default_memory_reader.py`: tokenizer 를 받아 `search` 가 `query_terms_of` 로 나눈 낱말을 `search_knowledge(search_param, query_terms)` 에
  - `app/providers/memory_provider.py`: `KiwiTextTokenizer` (provides TextTokenizer, Scope.APP), `MemorySearchTermsRefreshUsecase`
  - `app/lifespan.py`: 시작할 때 `fill_empty_search_terms(container)` 가 REQUEST 범위를 열어 Usecase 를 부른다. 채운 수를 로그 `Memory search terms filled: count=n`. 실패하면 예외를 로그로 남기고 서버는 뜬다
  - `kiwi_text_tokenizer.py`: Kiwi 를 프로세스에 하나 (`functools.cache`). 시험이 앱을 여러 번 만들어도 모델을 한 번만 읽는다
- specs/usecase.md 갱신
- 검증: ruff check·format 통과 (276 files), lint-imports 2 kept, mypy 통과 (229 files), create_app 통과

### 6. 시험, 두 DB, 최종 검증 (2026-11-21)
- 시험 DB 이미지: `conftest.py` 의 `PostgresContainer("postgres:16-alpine")` → `PostgresContainer("pgvector/pgvector:pg16")`
- 더한 시험
  - `packages/app/tests/test_memory_api.py`: 조사가 붙어도 찾기 ("설계에서 에러를" 로 "API 설계"), 고치면 낱말이 다시 만들어짐 ("정합성" 이 고친 뒤에만 찾아짐, 지운 낱말 "마지막" 은 안 찾아짐), 검색어가 비거나 조사만 있으면 고친 시각 최근 순·점수 0, 채우기 Usecase 가 낱말이 빈 지식만 채우고 고친 시각은 그대로
  - `packages/persistence/tests/test_kiwi_text_tokenizer.py`: 품사 거르기, 조사·숫자·의존 명사 빼기와 영문 소문자, 빈 글
- 기존 검색 시험 3 개는 바꾸지 않고 통과
- 최종 검증: ruff check 통과, ruff format 277 files, lint-imports 2 kept, mypy 229 files 통과, create_app 통과, pytest 71 passed
- 개발 DB(be-db-1): `alembic upgrade head` → `alembic check` "No new upgrade operations detected". 시작할 때 채우기와 같은 함수로 7 개 채움, 낱말이 빈 지식(지운 것 뺌) 0
- 배포 DB: `docker compose -f infra/docker-compose.yml up -d --build be`. migration `fc4ad6b1e3bd` 적용, 시작 로그 `Memory search terms filled: count=7`, 낱말이 빈 지식은 지운 지식 2 개뿐 (지운 것은 채우지 않는다)
  - 검색 확인 (kind plan, persona [1], "문서 계획에서 검토를"): #5 문서 작성 계획 0.3451, #7 서비스 설계 문서 작성 0.2432, #6 기획 문서 작성 0.1823, #3 API 서버 개발 0.075
  - GET /memories/3 의 덧붙인 본문 그대로, 웹 200

### 계획과 다른 점
- `MemoryRepository.find_ids_without_search_terms()` 를 더함 (시작할 때 낱말이 빈 지식만 채우기로 정해서)
- Kiwi 를 프로세스에 하나로 (`functools.cache`). 시험이 앱을 여러 번 만들 때마다 모델을 다시 읽지 않게
- `setweight` 의 무게를 바인드 값이 아니라 SQL 상수(`'A'`, `'B'`)로 넣음 (Postgres 가 varchar 를 "char" 로 받지 않음)
- kiwi 가 "만드는" 의 "만들" 을 보조 용언(VX)으로 보는 경우가 있어 그 낱말은 빠진다 (보조 용언 "않" 을 빼려고 VX 는 남기지 않음)

### 알아 둘 것
- 서버 시작이 느려졌다: 배포 컨테이너에서 시작부터 채우기 끝까지 약 41 초 (kiwi 모델 읽기). health check 는 5 초 × 20 번이라 그 안에 든다
- 서버 컨테이너 메모리 약 608MiB (전에는 약 71MiB)
- 점수: 응답 모양은 그대로, 값은 `ts_rank` (예 0.0~0.35). 전에는 낱말 비율 0~1

### 리뷰 반영 (사용자 동의 2026-11-21)
- 서버가 시작할 때 kiwi 를 한 번 미리 돌린다 (`app/lifespan.py` 의 `warm_up_tokenizer`). 첫 검색·저장이 약 4 초 걸리고 그동안 다른 요청이 잠금에서 기다리던 것을 없앤다. 실패해도 서버는 뜬다
- 검색어에 글자는 있는데 낱말이 하나도 남지 않으면 (숫자, 기호, 조사만) 빈 결과 (`DefaultMemoryReader.search` 의 `_has_text_but_no_terms`). 검색어가 비었을 때만 고친 시각 최근 순
  - 시험 as-is: `test_search_without_words_returns_newest_updated_first` 가 "" 와 "에서는" 모두 최근 순을 기대
  - 시험 to-be: `test_search_without_query_returns_newest_updated_first` ("" 만), `test_search_with_text_but_no_words_returns_nothing` ("에서는", "404", "!!" 는 [])
- 같은 지식에 PATCH 두 개가 동시에 올 때 낱말이 옛 본문 기준으로 남을 수 있는 것은 그대로 둔다 (한 사람이 쓰는 지금은 거의 생기지 않음)
- 검증: ruff, ruff format, lint-imports, mypy 통과, pytest 72 passed

