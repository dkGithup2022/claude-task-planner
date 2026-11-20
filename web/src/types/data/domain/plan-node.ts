/**
 * PlanNode (도메인) — 계획의 작업 하나. 앞 노드·뒤 노드는 PlanEdge 에서 계산한다
 * 근거 화면: PlanGraph.dc.html
 * 보류: 실행 기록(회차, 시각, 결과, 실패 이유)은 서버에 없다
 */
export interface PlanNode {
  node_id: number;        // PlanGraph.dc.html 노드 상자 "49"
  title: string;          // PlanGraph.dc.html "도메인 문서 작성"
  kind: NodeKind;         // PlanGraph.dc.html "document", 확인 노드 "hitl"
  persona_ids: number[];  // PlanGraph.dc.html "담당 dankim-persona". 확인 노드는 보통 빈 목록
  output_spec: string;    // PlanGraph.dc.html 하는 일 · 산출물 · 그 외 설명 (md 하나)
  status: PlanNodeStatus; // PlanGraph.dc.html "● 완료"
}

/** 노드 상태 (enum) — PlanGraph.dc.html. 값은 BE 의 소문자 */
export type PlanNodeStatus = "todo" | "running" | "done" | "failed" | "skipped";
export const PLAN_NODE_STATUS_LABEL: Record<PlanNodeStatus, string> = {
  todo: "할 일",
  running: "실행 중",
  done: "완료",
  failed: "실패",
  skipped: "건너뜀",
};

/** 노드 종류 (enum) — PlanGraph.dc.html. hitl 은 사용자 확인 노드 */
export type NodeKind = "document" | "research" | "code" | "hitl";
export const NODE_KIND_LABEL: Record<NodeKind, string> = {
  document: "document",
  research: "research",
  code: "code",
  hitl: "확인",
};
