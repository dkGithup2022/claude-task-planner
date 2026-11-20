# API

경로는 모두 `/api` 로 시작한다. CLI 서버 주소는 `http://localhost:8000/api`. 인증 없음. 오류 응답은 `{status, error, message}`.

## 계획

### POST /api/plans — 계획 만들기

- 요청 PlanCreateRequest: title: str (빈 값 불가), request: str, persona_ids: list[int]
- 응답 201 PlanCreateResponse: plan_id: int, status: "drafting", created_at: str (`2026-11-20T04:16:15Z` 모양)
- 오류: 형식이 틀리면 400 ValidationFailed
- 호출: PlanCreateUsecase

### GET /api/plans/{plan_id} — 계획 조회

- 응답 200 PlanResponse: plan_id, title, request, persona_ids, status, created_at, nodes[NodeResponse], edges[EdgeResponse]
  - NodeResponse: node_id, title, kind, persona_ids, output_spec, status (node_id 순)
  - EdgeResponse: edge_id, from_node_id, to_node_id (edge_id 순)
- 오류: 없으면 404 PlanNotFoundException
- 호출: PlanReader.get_by_id

### PATCH /api/plans/{plan_id}/status — 계획 상태 바꾸기

- 요청 PlanStatusChangeRequest: status: PlanStatus. 바꾸는 순서는 검사하지 않는다 (사용자 결정)
- 응답 200 PlanResponse (조회와 같은 모양)
- 오류: 없으면 404, 계획 상태가 아닌 값이면 400
- 호출: PlanStatusChangeUsecase

## 노드와 간선 (plan_router)

### POST /api/plans/{plan_id}/nodes — 노드 하나 저장

- 요청 NodeCreateRequest: title (빈 값 불가), kind: NodeKind, persona_ids: list[int], output_spec: str
- 응답 201 NodeCreateResponse: node_id, status ("todo")
- 오류: 계획이 없으면 404, 형식이 틀리면 400
- 호출: PlanNodeCreateUsecase

### PATCH /api/plans/{plan_id}/nodes/{node_id} — 노드 하나 고치기

- 요청 NodeUpdateRequest: title, kind, persona_ids, output_spec, status 모두 생략 가능. 빠지거나 null 이면 바꾸지 않는다. 상태 순서는 검사하지 않는다
- 응답 200: node_id, status
- 오류: 노드가 없거나 다른 계획의 노드면 404, 형식이 틀리면 400
- 호출: PlanNodeUpdateUsecase

### DELETE /api/plans/{plan_id}/nodes/{node_id} — 노드 하나 지우기

- 노드와 그 노드에 닿은 간선을 지운다. 이미 없거나 다른 계획의 노드면 아무것도 하지 않는다
- 응답 204 (본문 없음)
- 호출: PlanNodeDeleteUsecase

### POST /api/plans/{plan_id}/edges — 간선 하나 저장

- 요청 EdgeCreateRequest: from_node_id: int, to_node_id: int
- 응답 EdgeCreateResponse: edge_id. 새로 만들면 201, 같은 간선이 이미 있으면 200 과 그 간선의 id
- 오류: 계획이 없으면 404, 양 끝 노드가 그 계획에 없으면 400 PlanEdgeEndNotInPlanException
- 호출: PlanEdgeCreateUsecase

### DELETE /api/plans/{plan_id}/edges/{edge_id} — 간선 하나 지우기

- 이미 없거나 다른 계획의 간선이면 아무것도 하지 않는다. 응답 204
- 호출: PlanEdgeDeleteUsecase

## 지식 (memory_router)

### POST /api/memories — 지식 하나 만들기

- 요청 MemoryCreateRequest: kind: MemoryKind, theme (빈 값 불가), body (빈 값 불가), persona_ids: list[int], source: list[{quote, plan_id}]
- 응답 201 MemoryIdResponse: memory_id
- 오류: 형식이 틀리면 400
- 호출: MemoryCreateUsecase

### GET /api/memories/{memory_id} — 지식 하나 조회

- 응답 200 MemoryResponse: memory_id, kind, theme, body, persona_ids, source[{quote, plan_id}]
- 오류: 없으면 404 MemoryNotFoundException
- 호출: MemoryReader.get_by_id

### PATCH /api/memories/{memory_id} — 지식 고치기

- 요청 MemoryUpdateRequest: kind, theme, body, persona_ids, source 모두 생략 가능. 빠지거나 null 이면 바꾸지 않는다. CLI 덧붙이기는 body·source, 웹은 kind·theme·body·persona_ids
- 서버는 받은 본문·근거를 그대로 저장한다 (덧붙임 머리를 만들지 않는다)
- 응답 200 MemoryIdResponse: memory_id
- 오류: 없으면 404, 빈 theme·body 400
- 호출: MemoryUpdateUsecase

### DELETE /api/memories/{memory_id} — 지식 지우기

- 응답 204. 없거나 이미 지운 지식이면 404 (웹의 사람이 누르는 동작이라 알린다. 노드·간선 지우기와 다르다)
- 호출: MemoryDeleteUsecase

### POST /api/memories/search — 지식 검색

- 요청 MemorySearchRequest: kind (필수), query, persona_ids, theme (null 가능), limit (기본 10, 1~100)
- 응답 200 MemorySearchResponse: items[{memory_id, kind, theme, body, score}] 점수 높은 순
- 오류: 형식이 틀리면 400
- 호출: MemoryReader.search → KnowledgeSearcher.search_knowledge

### GET /api/memories — 지식 목록 (웹)

- query: q (작업 이름·본문에 들어 있는 글자, 대소문자 무시), kind, persona_id, limit (1~200, 없으면 전부)
- 응답 200 MemoryListResponse: items[{memory_id, kind, theme, persona_ids, appended_count, source_plan_ids, created_at, updated_at, edited}], total (limit 무시)
- 순서: 고친 시각 최근 것부터. 메인의 최근 지식은 `?limit=5`
- 호출: MemoryReader.get_list

## 페르소나 (persona_router)

### GET /api/personas — 페르소나 목록

- 응답 200 PersonaListResponse: personas[{persona_id, name, description, memory_count, plan_count}] persona_id 순. CLI 는 앞의 셋만 읽는다
- 호출: PersonaReader.get_all

### POST /api/personas — 페르소나 만들기

- 요청 PersonaCreateRequest: name (1~255자), description (빈 값 허용)
- 응답 201 PersonaIdResponse: persona_id
- 오류: 같은 이름 409 PersonaNameDuplicatedException, 빈 이름 400
- 호출: PersonaCreateUsecase

### PATCH /api/personas/{persona_id} — 페르소나 고치기

- 요청 PersonaUpdateRequest: name, description 모두 생략 가능
- 응답 200 PersonaIdResponse
- 오류: 없으면 404, 다른 페르소나와 이름이 같으면 409, 빈 이름 400
- 호출: PersonaUpdateUsecase

### DELETE /api/personas/{persona_id} — 페르소나 지우기

- 응답 204
- 오류: 없으면 404, 쓰는 지식이나 계획(참여 또는 노드 담당)이 있으면 409 PersonaInUseException, message 는 "지식 n개, 계획 m개가 이 페르소나를 씁니다"
- 호출: PersonaDeleteUsecase

### GET /api/plans — 계획 목록 (웹)

- query: status (이 상태만), limit (1~200, 없으면 전부). 메인은 `?status=running`, `?status=reviewing`, `?limit=5`
- 응답 200 PlanListResponse: plans[{plan_id, title, status, persona_ids, created_at, node_counts{todo, running, done, failed, skipped, total}}] 만든 시각 최근 순
- 호출: PlanReader.get_summaries

## 공통 오류: 없는 페르소나

POST /api/plans, POST /api/plans/{id}/nodes, PATCH /api/plans/{id}/nodes/{node_id}, POST /api/memories, PATCH /api/memories/{id} 는 persona_ids 에 없는(지운) 페르소나가 있으면 400 UnknownPersonaException, message "페르소나 n 가 없습니다". 고치기에서 persona_ids 를 보내지 않으면 보지 않는다.
