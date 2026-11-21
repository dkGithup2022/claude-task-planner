# Plan: 지식 검색에 벡터 검색 더하기, 켜면 전문 검색과 RRF 로 합치기 (POST /api/memories/search 아래)

## 요청 스펙
/Users/dankim/orca/workspaces/productivility/task-plan-server/be 에서 지식 검색에 벡터 검색을 더하고, 켜면 전문 검색 결과와 RRF 로 합친다. API 경로와 요청·응답 모양은 그대로다 (POST /api/memories/search, POST /api/memories, PATCH /api/memories/{memory_id}).

정한 것 (사용자, 2026-11-21):
- 환경 변수로 끄고 켠다 (`APP_MEMORY_SEARCH_VECTOR`, 기본값 off)
- 설정에 모델 이름(`APP_MEMORY_SEARCH_VECTOR_MODEL`, 기본 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)과 차원(`APP_MEMORY_SEARCH_VECTOR_DIMENSION`, 기본 384)을 둔다
- 모델은 fastembed(ONNX, torch 없음)로 서버 안에서 돌린다. 시작할 때 모델이 내는 벡터 길이가 설정 차원과 다르면 서버가 뜨지 않는다
- memories 테이블에 `embedding`(vector, 차원 없음)과 `embedding_model`(text) 열을 더한다. 인덱스는 걸지 않는다
- 모델을 바꿀 때는 마이그레이션 없이 환경 변수를 바꾸고 서버를 다시 띄운다. 시작할 때 비었거나 다른 모델로 만든 벡터를 다시 만든다
- 검색은 켜짐 여부로 분기한다. 끄면 전문 검색만, 켜면 전문 검색 30 개와 벡터 검색 30 개를 RRF(k=60)로 합쳐 limit 개
- 저장은 켜져 있을 때만 작업 이름과 본문으로 벡터를 만든다. 끄면 벡터를 비운다

데이터 스펙 변경 (`embedding`·`embedding_model` 열, `MemoryEmbedding`, `TextEmbedder`, `MemoryRepository.save(memory, terms, embedding)`, `KnowledgeSearcher.search_by_embedding`) 은 사용자 승인 2026-11-21.

이 계획 전에 할 일 (이 계획에 넣지 않음): 전문 검색 리뷰에서 고치기로 한 두 가지 (사용자 동의 2026-11-21)
- 서버가 시작할 때 kiwi 로 한 번 미리 나눠 둔다 (첫 검색·저장이 약 4 초 걸리지 않게)
- 검색어에 글자는 있는데 낱말이 하나도 안 남으면 빈 결과를 돌려준다

이번 범위가 아닌 것: 검색어 없는 목록과 검색 나누기, 후보군 찾기 10 개와 페이징, 계획·수행 컨텍스트 5 개.

## Phase 1: 평가

### assess-api

1. 충족 여부: 부분 충족 (요청 limit 상한만 바꿈. 처음 평가는 충족이었고, 사용자가 상한 30 을 정해 2026-11-21 에 바꿈)
   - `POST /api/memories/search`, `POST /api/memories`, `PATCH /api/memories/{memory_id}` 가 이미 있고 (specs/api.md 65·78·91 행), 경로와 응답 모양은 바꾸지 않는다
   - 이번 요청은 API 아래(검색 방식, 저장할 때 벡터 만들기)를 바꾸는 일이라 하위 평가를 이어 간다
2. 하위 레이어에 필요한 기능
   - A. service
     - 기존 사용: `MemoryReader.search(search_param)`, `MemoryCreateUsecase.execute`, `MemoryUpdateUsecase.execute` (시그니처 그대로)
     - 동작 변경 요청: `DefaultMemoryReader.search` 가 벡터 검색 켜짐 여부로 분기한다. `DefaultMemoryWriter.create`, `update` 가 켜져 있을 때만 벡터를 만들어 내린다
   - B. model: API 응답에 쓰는 `MemorySearchHit` 그대로. 벡터 값 `MemoryEmbedding` 은 아래 층의 요청 (사용자 승인 2026-11-21)
3. 현재 레이어 작업 계획: `MemorySearchRequest.limit` 상한 100 → 30 (Phase 2 의 정한 것 1). 라우터(`api/memory/memory_router.py`)와 Response DTO 는 그대로
   - 켜면 응답 `score` 의 값이 RRF 점수가 된다 (아래 Phase 2). 모양은 같다
   - 요청 `limit` 은 지금 1~100 (`MemorySearchRequest`, `le=100`) 이고, 1~30 으로 낮춘다

### assess-usecase

1. 충족 여부: 부분 충족 (메서드 시그니처는 그대로, 구현과 의존이 바뀜)
2. 하위 레이어에 필요한 기능
   - A. infrastructure (사용자 승인 2026-11-21)
     - 기존 사용: `MemoryRepository.find_write_by_id`, `KnowledgeSearcher.search_knowledge(search_param, query_terms)`
     - 신규 요청 (포트): `TextEmbedder`
       - `enabled -> bool`: 벡터 검색을 켰는지
       - `model -> str`: 지금 쓰는 모델 이름
       - `embed(text: str) -> MemoryEmbedding`: 글의 벡터. `enabled` 가 False 이면 부르지 않는다
     - 신규 요청 (읽기): `KnowledgeSearcher.search_by_embedding(search_param: SearchParam, embedding: MemoryEmbedding, limit: int) -> list[MemorySearchHit]`. 거르기는 `search_knowledge` 와 같고, 같은 모델로 만든 벡터만 코사인 유사도 순
     - 변경 요청 (쓰기): `MemoryRepository.save(memory, terms, embedding: MemoryEmbedding | None) -> Memory`. None 이면 벡터를 비운다
     - 신규 요청 (쓰기): `MemoryRepository.save_embedding(identity: MemoryIdentity, embedding: MemoryEmbedding) -> None`. 벡터만 바꾼다. 고친 시각은 그대로
     - 신규 요청 (읽기): `MemoryRepository.find_ids_without_embedding_of(model: str) -> list[MemoryIdentity]`. 벡터가 비었거나 다른 모델로 만든 지식 (지운 것 뺌)
   - B. model (사용자 승인 2026-11-21)
     - 신규: `MemoryEmbedding(model: str, vector: tuple[float, ...])` 값만
     - 기존 사용: `Memory`, `SearchParam`, `MemorySearchHit` 그대로
3. 현재 레이어 작업 계획
   - [신규] `service/memory/search_terms/embedding_of.py`: `embedding_of(embedder, theme, body) -> MemoryEmbedding`. 작업 이름과 본문을 줄바꿈으로 이어 하나로 만든다. 저장과 시작할 때 다시 만들기가 같이 쓴다
   - [신규] `service/memory/search_rank/reciprocal_rank_fusion.py`: `reciprocal_rank_fusion(*rankings: list[MemorySearchHit]) -> list[MemorySearchHit]`. 지식마다 `1 / (60 + 순위)` 를 더한 점수 순. 점수는 RRF 점수로 바꿔 돌려준다. 바깥 의존 없음
   - [변경] `DefaultMemoryReader(repository, searcher, tokenizer, embedder)`: `search` 시그니처·반환 그대로
     - as-is: 검색어를 낱말로 나눠 `search_knowledge` 한 번
     - to-be: `if not embedder.enabled` 이면 `_full_text_search` (as-is 와 같음). 켜져 있으면 `_hybrid_search`: limit 을 후보 수(30)로 바꾼 조건으로 전문 검색, 검색어 벡터로 `search_by_embedding(…, 30)`, 둘을 RRF 로 합쳐 limit 개
     - Reader 라 `@transactional` 없음. 두 검색은 각자 searcher 의 트랜잭션에서 읽는다
   - [변경] `DefaultMemoryWriter(tx, repository, tokenizer, embedder)`: `create`, `update` 시그니처·반환 그대로
     - as-is: `save(memory, self._search_terms(memory))`
     - to-be: `save(memory, self._search_terms(memory), self._embedding(memory))`. `_embedding` 은 꺼져 있으면 None, 켜져 있으면 `embedding_of`. `@transactional` 안에서 (벡터 만들기는 검색어 하나 약 4ms, DB 를 쓰지 않는다)
   - [신규] `MemoryEmbeddingRefreshUsecase.execute() -> int` (다시 만든 지식 수): 꺼져 있으면 0. 켜져 있으면 `find_ids_without_embedding_of(embedder.model)` 의 지식을 읽어 `embedding_of` 로 만들어 `save_embedding`. `@transactional`. 라우터에는 내지 않고 서버가 시작할 때 app 의 lifespan 이 부른다
   - 소유권 체크: 없음 (인증 없는 서버)
   - DI: `MemoryProvider` 에 `TextEmbedder` (Scope.APP, 설정을 보고 구현을 고른다), `MemoryEmbeddingRefreshUsecase`

### assess-infra

1. 충족 여부: 부분 충족 (기존 ABC 두 개에 메서드 셋 추가, 하나 변경, 포트 하나 신규. 사용자 승인 2026-11-21)
2. 하위 레이어에 필요한 기능
   - A. model
     - 신규 (VO): `MemoryEmbedding(model: str, vector: tuple[float, ...])`. 글 하나의 벡터와 그 벡터를 만든 모델. 모델이 다르면 차원이 달라 서로 비교하지 않으므로 모델 이름을 같이 둔다. 바깥 의존 없음
     - 기존 사용: `Memory`, `MemoryIdentity`, `SearchParam`, `MemorySearchHit`, `MemorySearchTerms` 그대로
3. 현재 레이어 작업 계획 (as-is / to-be)
   - [신규] 포트 `TextEmbedder` (`infrastructure/memory/text_embedder.py`): `enabled` (property), `model` (property), `embed(text) -> MemoryEmbedding`
   - [신규] `KnowledgeSearcher.search_by_embedding(search_param: SearchParam, embedding: MemoryEmbedding, limit: int) -> list[MemorySearchHit]`. 읽기. 거르기(종류, 페르소나 겹침, theme, 지운 것 뺌)는 `search_knowledge` 와 같다. `embedding_model` 이 같은 지식만 가까운 순으로 limit 개. 점수는 코사인 유사도 (1 - 코사인 거리). 없으면 []
   - [변경] `MemoryRepository.save`
     - as-is: `save(memory: Memory, terms: MemorySearchTerms) -> Memory`
     - to-be: `save(memory: Memory, terms: MemorySearchTerms, embedding: MemoryEmbedding | None) -> Memory`. 쓰기. None 이면 `embedding`, `embedding_model` 을 비운다
   - [신규] `MemoryRepository.save_embedding(identity: MemoryIdentity, embedding: MemoryEmbedding) -> None`. 쓰기. 벡터만 바꾼다. 고친 시각은 그대로. 지운 지식이면 아무것도 하지 않는다
   - [신규] `MemoryRepository.find_ids_without_embedding_of(model: str) -> list[MemoryIdentity]`. 읽기. 벡터가 비었거나 `embedding_model` 이 다른 지식 (지운 것 뺌). 없으면 []
   - 원자적 연산: 없음. Stats 분리: 없음
   - 어댑터 갱신 필요: 있음. `DefaultMemoryRepository`, `DefaultKnowledgeSearcher` 를 add-query 에서 바꾸고, `FastembedTextEmbedder`, `DisabledTextEmbedder` 를 새로 둔다

### assess-model

1. 충족 여부: 부분 충족 (VO 하나 신규. 기존 모델 변경 없음. 사용자 승인 2026-11-21)
2. 현재 레이어 작업 계획
   - 패턴: 기존 memory 도메인 아래의 VO (`MemorySearchTerms` 와 같은 모양)
   - [신규 VO] `MemoryEmbedding` (`model/memory/memory_embedding.py`)
     - 필드: `model: str` (벡터를 만든 모델 이름), `vector: tuple[float, ...]`
     - `@dataclass(frozen=True, slots=True)`, 팩토리·상태 변경 없음. 바깥 의존 없음 (numpy 를 쓰지 않는다)
   - `Memory`, `MemoryRead`, `SearchParam`, `MemorySearchHit` 는 바꾸지 않는다. 벡터는 읽는 쪽(웹, CLI)에 보일 필요가 없어 `Memory` 에 넣지 않는다
   - 새 예외 없음

## Phase 2: 구현 계획

### 평가 결과
- api: 부분 충족. 경로·응답 그대로, 요청 limit 상한만 100 → 30 (켜면 점수 값의 뜻도 바뀜)
- service: 부분 충족. Reader 의 분기, Writer 의 벡터 만들기, 벡터 규칙 함수, RRF 함수, 시작할 때 다시 만들기 Usecase
- infra: 부분 충족. 포트 `TextEmbedder`, `KnowledgeSearcher.search_by_embedding`, `MemoryRepository.save(memory, terms, embedding)`, `save_embedding`, `find_ids_without_embedding_of`
- model: 부분 충족. VO `MemoryEmbedding`

### 설계 결정
- 설정 (`app/settings.py`, 접두어 `APP_`)
  - `memory_search_vector: bool = False` (`APP_MEMORY_SEARCH_VECTOR`)
  - `memory_search_vector_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"` (`APP_MEMORY_SEARCH_VECTOR_MODEL`). fastembed 0.9.1 의 지원 목록에 이 이름으로 있다 (384 차원, 0.22GB)
  - `memory_search_vector_dimension: int = 384` (`APP_MEMORY_SEARCH_VECTOR_DIMENSION`). 모델을 바꾸면 같이 바꾼다
  - `Settings` 는 `AppProvider` (Scope.APP) 가 이미 내주므로 `MemoryProvider` 가 인자로 받을 수 있다 (`app/di.py`)
- 의존성: `fastembed`(0.9.x), `pgvector`(0.5.x, SQLAlchemy 의 `Vector` 타입) 를 `packages/persistence/pyproject.toml` 에 더한다. `uv.lock` 갱신. fastembed 는 onnxruntime 을 끌고 와 서버 이미지가 커진다
- 구현 (persistence)
  - `FastembedTextEmbedder(model, dimension)` (`persistence/memory/fastembed_text_embedder.py`): `fastembed.TextEmbedding(model)` 을 한 번 만들어 둔다. 만들 때 "준비" 를 한 번 벡터로 바꿔 길이가 `dimension` 과 다르면 `ValueError` (모델, 기대 차원, 실제 차원을 메시지에). 같은 호출이 모델을 처음 읽는 시간도 시작할 때 쓰게 한다. `enabled` 는 True
  - `DisabledTextEmbedder` (`persistence/memory/disabled_text_embedder.py`): `enabled` 는 False, `model` 은 빈 글, `embed` 를 부르면 에러 (부르는 쪽이 `enabled` 를 먼저 본다)
  - 벡터를 만들 때 동시에 여러 요청이 오면: fastembed(onnxruntime) 는 같은 세션을 여러 스레드가 써도 된다. kiwi 처럼 잠금을 두지 않는다
- DI: `MemoryProvider` 에 `@provide(scope=Scope.APP) def embedder(self, settings: Settings) -> TextEmbedder`. 꺼져 있으면 `DisabledTextEmbedder()`, 켜져 있으면 `FastembedTextEmbedder(model, dimension)`
- 차원이 다르면 서버가 뜨지 않게 하기: 지금 lifespan 의 채우기(`fill_empty_search_terms`)는 예외를 로그로만 남기고 서버를 띄운다. 그래서 벡터 다시 만들기 안에서 처음 `TextEmbedder` 를 만들면 차원 에러도 삼켜진다. lifespan 이 채우기 전에 `container.get(TextEmbedder)` 를 try 밖에서 불러, 차원이 다르면 시작이 실패하게 한다. 다시 만들기(`fill_empty_embeddings`)의 실패는 지금처럼 로그만 남기고 서버는 뜬다
- 열 (`MemoryEntity`)
  - `embedding: vector` (차원 없음, nullable, deferred). pgvector 0.5.1 의 `Vector()` 는 차원 없이 `VECTOR` 로 선언된다
  - `embedding_model: text` (nullable, deferred)
  - 인덱스 없음. 차원이 정해진 열에만 HNSW 인덱스를 걸 수 있다. 지식이 수천 개, 384 차원이어도 전체 비교가 수 밀리초다
- migration `memory_embedding` (down_revision: `fc4ad6b1e3bd`, 전문 검색 migration). 열 둘을 더하고 downgrade 는 열 둘을 지운다. vector 확장은 `fc4ad6b1e3bd` 에서 이미 켰다
- 저장: `DefaultMemoryRepository.save(memory, terms, embedding)` 가 새로 만들 때와 고칠 때 모두 `embedding = list(embedding.vector)`, `embedding_model = embedding.model` 를 넣는다. None 이면 둘 다 NULL. `save_embedding` 은 그 두 열만 바꾸고 `updated_at` 은 그대로 (`update_search_tokens_by_id_and_active` 와 같은 방식)
- 벡터 검색: `DefaultKnowledgeSearcher.search_by_embedding`
  - 거르기는 `find_for_search_by_terms_and_active` 와 같다 (종류, 페르소나 겹침, 지운 것 뺌, theme)
  - 더해서 `embedding_model = embedding.model`. 이 조건이 꼭 있어야 한다: 개발 DB(pgvector 0.8.7)에서 차원이 다른 벡터를 비교하면 `ERROR: different vector dimensions 2 and 3` 으로 쿼리 전체가 실패한다 (2026-11-21 확인)
  - 순서: `embedding <=> 검색어 벡터` (코사인 거리) 작은 순, limit. 점수는 `1 - 거리`
- 검색 분기 (`DefaultMemoryReader.search`)
  - 끄면 `_full_text_search`: 지금과 같다
  - 켜면 `_hybrid_search`: 전문 검색 30 개 + 벡터 검색 30 개 → `reciprocal_rank_fusion` → 앞에서 limit 개
  - 후보 수 `CANDIDATE_COUNT = 30` 은 service 의 상수. 요청 limit 상한도 30 이라 늘 충분하다
- 점수 값 (as-is / to-be): 응답 모양은 그대로
  - 끄면: 지금처럼 `ts_rank` (0~1)
  - 켜면: RRF 점수. 두 목록 모두 1 위면 2/61 ≈ 0.033, 한 목록에만 1 위면 1/61 ≈ 0.016. CLI 는 점수를 순서로만 쓴다
- 시작할 때 다시 만들기: lifespan 이 낱말 채우기 다음에 `fill_empty_embeddings(container)` 를 부르고 다시 만든 수를 로그 `Memory embeddings filled: count=n` 으로 남긴다. 꺼져 있으면 0
- 모델 파일: fastembed 는 처음 쓸 때 모델(0.22GB)을 내려받아 `FASTEMBED_CACHE_PATH` (없으면 OS 임시 폴더 아래 `fastembed_cache`)에 둔다. 배포는 compose 의 볼륨에 둔다 (아래 정한 것 2)
- 시험 (모델을 내려받지 않게 가짜 벡터로)
  - `reciprocal_rank_fusion` 단위 시험: 두 목록에 다 있는 지식이 위로, 한 목록에만 있는 지식, 빈 목록
  - `DefaultMemoryReader.search` 단위 시험 (be-test-service 방식, 가짜 `TextEmbedder`): 꺼져 있으면 전문 검색만 부르고 벡터 검색은 부르지 않음, 켜져 있으면 둘 다 30 개로 부르고 합친 결과를 limit 개
  - `DefaultMemoryWriter` 단위 시험: 꺼져 있으면 `save(…, None)`, 켜져 있으면 벡터를 넘김
  - persistence 통합 시험 (실제 Postgres): 손으로 만든 벡터로 `search_by_embedding` 순서, 다른 모델의 벡터는 빼고 에러가 나지 않음, `save(…, None)` 이 벡터를 비움, `find_ids_without_embedding_of` 가 빈 것과 다른 모델 것을 돌려줌
  - 기존 `packages/app/tests/test_memory_api.py` 는 그대로 통과해야 한다 (기본값 off 라 전문 검색만 쓴다)
  - `FastembedTextEmbedder` 의 차원 검사는 모델을 내려받아야 해서 자동 시험에 넣지 않는다. 구현 뒤 개발 서버를 켜서 한 번 확인한다 (차원을 틀리게 주면 시작 실패, 맞게 주면 시작하고 지식 7 개 다시 만듦)
- 문서: specs/models.md, infrastructure.md, repository.md, schema.md, usecase.md

### 구현 순서 (역순)
1. add-model: `MemoryEmbedding`
2. add-infrastructure: `TextEmbedder` 신규, `KnowledgeSearcher.search_by_embedding` 신규, `MemoryRepository.save(memory, terms, embedding)` 변경, `save_embedding`·`find_ids_without_embedding_of` 신규
3. add-entity-specs: `MemoryEntity.embedding`·`embedding_model`, migration `memory_embedding`
4. add-query: `DefaultMemoryRepository` (save, save_embedding, find_ids_without_embedding_of), `DefaultKnowledgeSearcher.search_by_embedding`, `MemoryEntityQuery` 에 벡터 쿼리, `FastembedTextEmbedder`·`DisabledTextEmbedder` 신규, persistence 의존성 `fastembed`·`pgvector`
5. add-usecase: `embedding_of`, `reciprocal_rank_fusion`, `DefaultMemoryReader` 분기, `DefaultMemoryWriter._embedding`, `MemoryEmbeddingRefreshUsecase`, 설정 세 개, `MemoryProvider` 등록, lifespan (TextEmbedder 먼저 만들기, 다시 만들기)
6. add-api: `MemorySearchRequest.limit` 상한 30 (위 정한 것 1), `specs/api.md`
7. `infra/docker-compose.yml`, `infra/.env.example` (위 정한 것 2)
8. 시험, 개발 DB 에 migration, 켠 상태로 개발 서버 한 번 확인

### 파일 목록
- 새 파일
  - `model/memory/memory_embedding.py`
  - `infrastructure/memory/text_embedder.py`
  - `persistence/memory/fastembed_text_embedder.py`, `persistence/memory/disabled_text_embedder.py`
  - `schema/alembic/versions/20261121_<rev>_memory_embedding.py`
  - `service/memory/search_terms/embedding_of.py`
  - `service/memory/search_rank/__init__.py`, `service/memory/search_rank/reciprocal_rank_fusion.py`
  - `service/memory/usecase/memory_embedding_refresh_usecase.py`
  - 시험 파일 (service 단위, persistence 통합)
- 바꾸는 파일
  - `api/memory/dto/memory_search_request.py`
  - `infrastructure/memory/knowledge_searcher.py`, `infrastructure/memory/memory_repository.py`
  - `persistence/memory/memory_entity.py`, `memory_entity_query.py`, `memory_repository.py`, `default_knowledge_searcher.py`
  - `persistence/pyproject.toml`, `uv.lock`
  - `service/memory/impl/default_memory_reader.py`, `default_memory_writer.py`
  - `app/settings.py`, `app/providers/memory_provider.py`, `app/lifespan.py`
  - specs 문서 여섯 개 (api.md 더함)
  - `infra/docker-compose.yml`, `infra/.env.example` (저장소 맨 위의 infra)

### 정한 것 (사용자, 2026-11-21, 처음에 "정할 것" 으로 올린 세 가지)
1. 검색 개수 상한을 30 으로 낮춘다. 후보 30 개씩을 합치면 늘 충분하다
   - 위치: `api/memory/dto/memory_search_request.py:11`
   - as-is: `limit: int = Field(default=10, ge=1, le=100, description="최대 개수")`
   - to-be: `limit: int = Field(default=10, ge=1, le=30, description="최대 개수")`
   - `specs/api.md` 의 "limit (기본 10, 1~100)" 을 "1~30" 으로
   - 영향: CLI 는 정해 둔 개수(`SEARCH_LIMIT`, 30 보다 작음)로 부르고, 웹 지식 화면은 목록 API 를 쓴다. 31 이상은 지금처럼 400
2. 배포의 모델 파일 자리는 `infra/docker-compose.yml` 에 선언한다. be 에 아래를 더한다
   ```yaml
   environment:
     APP_MEMORY_SEARCH_VECTOR: ${MEMORY_SEARCH_VECTOR:-false}
     FASTEMBED_CACHE_PATH: /models
   volumes:
     - models:/models
   ```
   맨 아래 `volumes:` 에 `models:` 를 더한다. `infra/.env.example` 에 `MEMORY_SEARCH_VECTOR` 설명 한 줄
3. 켰을 때 메모리(kiwi 와 합쳐 1GB 남짓)는 그대로 둔다

### 시험 더하기 (사용자, 2026-11-21)
- persistence 통합 시험: 다른 모델(다른 차원)로 만든 벡터가 섞인 테이블에서 `search_by_embedding` 이 에러 없이 같은 모델의 지식만 돌려준다. 같은 모델 조건이 없으면 `ERROR: different vector dimensions 4 and 3` 으로 쿼리 전체가 실패하는 것을 개발 DB 임시 테이블에서 확인했다 (2026-11-21)

## Phase 3: 구현 진행
