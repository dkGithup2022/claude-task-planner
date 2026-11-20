# plan-graph 데이터

화면: PlanGraph.dc.html
작성: 2026-11-20
상태: 검수 완료 (사용자 지시에 따라 BE 스펙을 근거로 스스로 정함)

영역: 위 메뉴 / 계획 요약 (번호·제목, 상태·만든 시각·참여 페르소나, 상태별 노드 수·다시 읽기 안내·명령서 펼치기) / 그래프 (노드와 간선, 상태 기호 설명) / 노드 패널 (머리, 앞뒤 노드, 정의서)

## 공용 데이터 (스펙 그대로 사용)

| 항목 | 위치 | 쓰는 필드 | 쓰는 영역 |
|---|---|---|---|
| PlanDetail | src/types/data/domain/plan.ts | plan_id, title, request, persona_ids, status, created_at, nodes, edges | 요약, 그래프 |
| PlanNode | src/types/data/domain/plan-node.ts | node_id, title, kind, persona_ids, output_spec, status | 그래프 노드, 패널 |
| PlanEdge | src/types/data/domain/plan-edge.ts | from_node_id, to_node_id | 그래프 선, 패널 앞뒤 노드 |
| Persona | src/types/data/domain/persona.ts | persona_id, name | 참여·담당 페르소나 이름 |
| NodeSpecSections | src/types/data/domain/node-spec-sections.ts | does, output_form, output_contents, notes | 패널의 정의서 |
| PlanStatus, PlanNodeStatus, NodeKind | domain 파일들 | 라벨 | 기호와 종류 |

## 스펙 부족

없음.

## API 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| PlanDetailResponse | src/types/api/plan.ts | PlanDetail 그대로 | GET /api/plans/{id} |
| PersonaListResponse | src/types/api/persona.ts | personas: Persona[] | GET /api/personas (이름 바꾸기) |

## 페이지 전용 데이터

| 이름 | 위치 | 필드 | 용도 |
|---|---|---|---|
| (상태만) | PlanGraphClient | selectedNodeId: number \| null, showRequest: boolean | 고른 노드, 명령서 펼침. 타입 파일이 필요 없다 |

계산값 (저장하지 않음): 노드 위치(층 배치), 앞뒤 노드, 상태별 노드 수, 정의서의 절. `src/lib/plan-graph.ts`, `src/lib/node-spec.ts` 에서 계산한다.

## 애매한 것 (사용자 판단 필요)

없음.
