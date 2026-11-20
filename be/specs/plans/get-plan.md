# Plan: GET /api/plans/{plan_id}

## 요청 스펙

계획 조회. 그 계획의 노드와 간선이 모두 나온다. 없으면 404. 출처: `corbina/notes/2026-11-20-api.md` 4절.

응답 (200)

```jsonc
{
  "plan_id": 11, "title": "...", "request": "# 명령\n...", "persona_ids": [1],
  "status": "reviewing", "created_at": "2026-11-20T04:16:15Z",
  "nodes": [ { "node_id": 54, "title": "상위 기획 작성", "kind": "document", "persona_ids": [1], "output_spec": "...", "status": "todo" } ],
  "edges": [ { "edge_id": 102, "from_node_id": 54, "to_node_id": 55 } ]
}
```

CLI 기준 코드: `plan_json_converter.py` `to_plan` 이 위 필드를 모두 읽는다 (nodes, edges 는 꼭 있어야 한다). 404 는 `plan_api_http.py` 가 PlanNotFoundError 로 바꾼다. 문서와 코드가 다른 점: 없음.

## Phase 1: 평가

### assess-api

충족 여부: 미충족.

- service 신규: [Reader] PlanReader.get_by_id(identity: PlanIdentity) -> PlanRead. 없으면 PlanNotFoundException
- model: 기존 PlanRead, PlanNodeRead, PlanEdgeRead 로 충분
- 작업 계획: GET /api/plans/{plan_id}, 응답 PlanResponse (노드 NodeResponse, 간선 EdgeResponse 를 안에 담음). created_at 은 초 단위 UTC 문자열. 노드·간선의 plan_id, 시각은 응답에 넣지 않는다 (CLI 모양 그대로). 200, 인증 없음

### assess-usecase

충족 여부: 미충족. PlanReader 가 없다.

- infrastructure
  - 기존: PlanRepository.find_write_by_id
  - 신규: PlanNodeRepository.find_by_plan_id(plan_identity: PlanIdentity) -> list[PlanNodeRead] (읽기). 지운 노드는 빼고 node_id 순
  - 신규: PlanEdgeRepository.find_by_plan_id(plan_identity: PlanIdentity) -> list[PlanEdgeRead] (읽기). 지운 간선은 빼고 edge_id 순
- 작업 계획
  - [신규] PlanReader.get_by_id: 계획을 읽고, 노드와 간선을 각 도메인의 Repository 로 읽어 `plan.to_read(nodes, edges)` 로 묶는다
  - 다른 도메인의 Repository 를 Reader 에 주입한다 (번들 규칙상 Repository 참조는 허용)
  - 트랜잭션: Reader 는 열지 않는다. 세 번 읽는 사이에 다른 요청이 노드를 바꿀 수 있으나, 계획 하나를 한 사람이 다루므로 받아들인다. 같은 계획을 한 트랜잭션으로 읽어야 하는 쓰기 Usecase(상태 바꾸기)는 자기 트랜잭션 안에서 이 Reader 를 부른다
  - DI: PlanProvider 에 DefaultPlanReader. PlanNodeProvider, PlanEdgeProvider 신규

### assess-infra

충족 여부: 미충족. 노드와 간선의 Repository 가 없다.

- [신규] PlanNodeRepository.find_by_plan_id (Pattern Foo 로 시작)
- [신규] PlanEdgeRepository.find_by_plan_id (Pattern Foo 로 시작)

Entity 와 테이블 (add-entity-specs)
- plan_nodes: id, plan_id(인덱스), title(Text), kind(VARCHAR), output_spec(Text), status(VARCHAR), 공통 4컬럼
- plan_node_personas: 노드의 담당 페르소나 자식. id, node_id(인덱스), persona_id, position
- plan_edges: id, plan_id(인덱스), from_node_id, to_node_id, 공통 4컬럼
- 노드·간선은 계획과 다른 aggregate 로 둔다 (각자 API 로 만들고 지운다). plan_id 는 값으로만 갖고 relationship 을 두지 않는다

### assess-model

충족 여부: 충족.

## Phase 2: 구현 계획

[설계 결정]
- 패턴: infra Foo(노드, 간선) / entity Baz(노드에 담당 페르소나 자식), Foo(간선) / service Bar(Reader) / api Foo
- StrEnum 컬럼 정의를 한 곳(`persistence/enum_column.py` 의 value_enum)에 모은다. 값(소문자)을 저장하는 설정을 계획·노드에서 같이 쓴다

[구현 계획]
1. add-infrastructure: PlanNodeRepository, PlanEdgeRepository (find_by_plan_id)
2. add-entity-specs: PlanNodeEntity, PlanNodePersonaEntity, PlanEdgeEntity, migration `plan_node_edge`
3. add-query: PlanNodeEntityQuery, DefaultPlanNodeRepository, PlanEdgeEntityQuery, DefaultPlanEdgeRepository
4. add-usecase: PlanReader, DefaultPlanReader, PlanNodeProvider, PlanEdgeProvider
5. add-api: GET, PlanResponse, NodeResponse, EdgeResponse
6. 시험: 빈 계획 조회, DB 에 넣은 노드·간선이 나오는지, 지운 노드가 빠지는지, 없는 계획 404

## Phase 3: 구현 진행

### 구현 (2026-11-20)
- add-infrastructure: `plan_node/plan_node_repository.py` PlanNodeRepository, `plan_edge/plan_edge_repository.py` PlanEdgeRepository (find_by_plan_id)
- add-entity-specs: PlanNodeEntity, PlanNodePersonaEntity, PlanEdgeEntity, `enum_column.py` value_enum (PlanEntity 도 이것으로 바꿈. 테이블 변화 없음 — `alembic check` 로 확인), migration `20261120_69138c91383e_plan_node_edge.py`. 자식 테이블 FK 제약을 손으로 지움. DB FK 제약 0개
- add-query: PlanNodeEntityQuery, DefaultPlanNodeRepository, PlanEdgeEntityQuery, DefaultPlanEdgeRepository
- add-usecase: PlanReader, DefaultPlanReader (세 Repository 주입), PlanNodeProvider, PlanEdgeProvider, PlanProvider 에 reader
- add-api: GET /api/plans/{plan_id}, PlanResponse, NodeResponse, EdgeResponse
- 검증: ruff, lint-imports, mypy(124 파일), `alembic check` 통과
- 시험: 3개 더해 모두 7개 통과 (새 계획 조회의 전체 모양, 지운 노드와 다른 계획의 노드가 빠짐·페르소나 순서, 없는 계획 404)
