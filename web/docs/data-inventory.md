# 데이터 목록

작성: 2026-11-20

근거: 화면은 UI 가안 아티팩트의 아트보드 6개. 백엔드 스펙이 먼저 있으므로 도메인 이름과 필드 이름은 서버 모델(`../be/specs/models.md`)과 API(`../be/specs/api.md`)를 따른다.

## 화면

- Main.dc.html: 메인. 실행 중인 계획, 확정을 기다리는 계획, 최근 계획, 최근 지식, 지식 종류별 개수
- Plans.dc.html: 계획 목록 (실행 이력). 만든 시각 최근 순, 상태와 상태별 노드 수
- PlanGraph.dc.html: 계획 하나의 그래프. 위쪽 요약(상태, 만든 시각, 참여 페르소나, 상태별 노드 수, 명령서 펼치기), 노드와 간선, 고른 노드의 오른쪽 패널(앞뒤 노드, 정의서)
- Memories.dc.html: 지식 검색. 검색어·종류·페르소나로 거른 지식 표 (덧붙인 횟수, 근거 계획)
- MemoryDetail.dc.html: 지식 하나 조회·수정·지우기. 본문을 덧붙임 구분선으로 나눠 보이고 근거 목록을 보인다
- Personas.dc.html: 페르소나 목록 (지식 수, 계획 수), 펼친 상세, 만들기·고치기·지우기

## 논리적 도메인

- 페르소나 (Persona): 작업을 맡는 역할. 이름과 설명, 그 페르소나를 쓰는 지식 수·계획 수
- 지식 (Memory): 작업할 때 쓰는 지식 하나. 종류, 작업 이름, 본문(덧붙임 포함), 적용 페르소나, 근거 목록
- 계획 (Plan): 작업 계획. 제목, 명령서, 참여 페르소나, 상태, 만든 시각
- 노드 (PlanNode): 계획의 작업 하나. 제목, 종류, 담당 페르소나, 정의서, 상태
- 간선 (PlanEdge): 앞 노드가 끝나야 뒤 노드를 시작한다는 관계

## 기능 데이터

- 계획 상태 (PlanStatus, enum): 만드는 중 · 검토 중 · 승인 · 불허 · 실행 중 · 완료. "실패" 는 없다 — Main.dc.html, Plans.dc.html, PlanGraph.dc.html
- 노드 상태 (PlanNodeStatus, enum): 할 일 · 실행 중 · 완료 · 실패 · 건너뜀 — PlanGraph.dc.html
- 노드 종류 (NodeKind, enum): document · research · code · hitl(확인 노드, 이중 테두리) — PlanGraph.dc.html
- 지식 종류 (MemoryKind, enum): 지식(knowledge) · 태도(attitude) · 계획(plan) — Main.dc.html, Memories.dc.html, MemoryDetail.dc.html
- 상태별 노드 수 (node_counts): 계획마다 할 일·실행 중·완료·실패·건너뜀 수와 합. "6/9 (실패 1)" 로 보인다 — Main.dc.html, Plans.dc.html, PlanGraph.dc.html
- 지식 목록 조건 (검색어 q, 종류 kind, 페르소나 persona_id, 개수 limit): 지식 검색의 필터와 메인의 최근 5개 — Memories.dc.html, Main.dc.html
- 계획 목록 조건 (상태 status, 개수 limit): 메인의 실행 중·검토 중·최근 5개 — Main.dc.html
- 고른 노드 (selected node id): 그래프에서 누른 노드. 패널이 그 노드를 보인다. 화면 안 상태 — PlanGraph.dc.html
- 명령서 펼침 (보기/접기): 화면 안 상태 — PlanGraph.dc.html
- 자동 다시 읽기: 실행 중인 계획이면 10초마다 계획을 다시 읽는다. 끝난 계획은 읽지 않는다 (웹 UI 문서 1번 화면) — PlanGraph.dc.html
- 지식 수정 폼 (작업 이름, 종류, 페르소나, 본문): 고칠 값 — MemoryDetail.dc.html
- 지우기 확인 (지식), 지우기 거절 알림 (페르소나, 서버의 409 메시지): 화면 안 상태 — MemoryDetail.dc.html, Personas.dc.html
- 페르소나 펼침과 만들기·고치기 폼 (이름, 설명): 화면 안 상태와 고칠 값 — Personas.dc.html

## 애매한 것 (사용자 판단 필요)

사용자 지시("순차적으로 자유롭게 진행, API 데이터 관련만 질문")에 따라 서버 스펙을 근거로 정했다.

- 근거 (MemorySource): 사용자가 한 말과 그 계획 — MemoryDetail.dc.html. 후보: 도메인 | 기능 데이터. **정함: 지식 도메인의 값 목록(필드 `source`)**. 서버도 지식 안의 목록으로 둔다
- 정의서의 절 (하는 일, 산출물 형태·내용, 그 외 설명): 노드 패널 — PlanGraph.dc.html. 후보: 노드 도메인 | 기능 데이터. **정함: 노드의 `output_spec` md 에서 화면이 나눠 보인다 (저장 필드가 아님)**. CLI 의 NodeSpec 과 같은 규칙 (`### 하는 일`, `### 산출물` 첫 줄 `- 형태: `, `### 그 외 설명`)
- 앞 노드·뒤 노드: 노드 패널 — PlanGraph.dc.html. 후보: 노드 도메인 | 계산값. **정함: 간선에서 계산 (저장 필드가 아님)**. 서버 모델 규칙과 같다

## 소속 미정 필드 (사용자 판단 필요)

모두 서버 응답 필드로 정했다.

- 덧붙인 횟수: "덧붙임 3" — Memories.dc.html, MemoryDetail.dc.html. **정함: 지식 목록 응답의 `appended_count`**. 조회 화면은 본문의 `****** KNOWLEDGE APPENDED <n> ********` 머리를 세어 나눈다
- 근거 계획: "3, 11" — Memories.dc.html. **정함: 지식 목록 응답의 `source_plan_ids`**
- 새로 저장 / 고침: 메인의 최근 지식 — Main.dc.html. **정함: 지식 목록 응답의 `edited`**
- 지식 수·계획 수: Personas.dc.html. **정함: 페르소나 목록 응답의 `memory_count`, `plan_count`**
- 참여 페르소나 이름 ("dankim-persona"): 계획·지식·노드는 id 만 갖는다 — PlanGraph.dc.html, Memories.dc.html. **정함: 화면이 `GET /api/personas` 를 함께 읽어 id 를 이름으로 바꾼다**
