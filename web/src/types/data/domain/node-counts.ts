/**
 * NodeCounts (값 타입) — 계획의 상태별 노드 수
 * 근거 화면: Plans.dc.html "10/10", "6/9 (실패 1)", Main.dc.html
 */
export interface NodeCounts {
  todo: number;
  running: number;
  done: number;
  failed: number;
  skipped: number;
  total: number;
}
