/**
 * PlanEdge (도메인) — 앞 노드가 끝나야 뒤 노드를 시작한다
 * 근거 화면: PlanGraph.dc.html
 */
export interface PlanEdge {
  edge_id: number;
  from_node_id: number; // PlanGraph.dc.html "받는 산출물 (앞 노드)"
  to_node_id: number;   // PlanGraph.dc.html "넘기는 곳 (뒤 노드)"
}
