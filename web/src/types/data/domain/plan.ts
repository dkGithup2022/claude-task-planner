import type { NodeCounts } from "./node-counts";
import type { PlanEdge } from "./plan-edge";
import type { PlanNode } from "./plan-node";

/**
 * Plan (도메인) — 작업 계획
 * 근거 화면: Plans.dc.html, PlanGraph.dc.html, Main.dc.html
 * 목록 한 줄(PlanSummary)과 조회(PlanDetail)는 BE 응답의 필드가 달라 둘로 둔다
 */
export interface PlanSummary {
  plan_id: number;        // Plans.dc.html "11"
  title: string;          // Plans.dc.html "계산기 웹 서비스 개발 전 문서 6종 작성 …"
  status: PlanStatus;     // Plans.dc.html "● 완료"
  persona_ids: number[];  // 참여 페르소나
  created_at: string;     // Plans.dc.html "11-20 13:16" (UTC 를 사용자 시간대로)
  node_counts: NodeCounts; // Plans.dc.html "10/10"
}

export interface PlanDetail {
  plan_id: number;       // PlanGraph.dc.html "계획 11"
  title: string;         // PlanGraph.dc.html 제목
  request: string;       // PlanGraph.dc.html "명령서 보기" (md)
  persona_ids: number[]; // PlanGraph.dc.html "dankim-persona"
  status: PlanStatus;    // PlanGraph.dc.html "● 완료"
  created_at: string;    // PlanGraph.dc.html "2026-11-20 13:16"
  nodes: PlanNode[];     // PlanGraph.dc.html 그래프 (node_id 순)
  edges: PlanEdge[];     // PlanGraph.dc.html 그래프 선 (edge_id 순)
}

/** 계획 상태 (enum) — Main.dc.html, Plans.dc.html, PlanGraph.dc.html. "실패" 는 없다 */
export type PlanStatus = "drafting" | "reviewing" | "approved" | "rejected" | "running" | "done";
export const PLAN_STATUS_LABEL: Record<PlanStatus, string> = {
  drafting: "만드는 중",
  reviewing: "검토 중",
  approved: "승인",
  rejected: "불허",
  running: "실행 중",
  done: "완료",
};
