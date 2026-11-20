import type { MemoryKind, MemoryListItem } from "@/types/data/domain/memory";
import type { PlanSummary } from "@/types/data/domain/plan";

/** home 페이지 전용. 다른 페이지에서 import 하지 않는다 — Main.dc.html */
export interface HomeData {
  running: PlanSummary[];                  // 실행 중인 계획
  reviewing: PlanSummary[];                // 확정을 기다리는 계획
  recentPlans: PlanSummary[];              // 최근 계획 5개
  recentMemories: MemoryListItem[];        // 최근 지식 5개
  memoryTotal: number;                     // "지식 전체 7개"
  kindCounts: Record<MemoryKind, number>;  // "지식 3 · 태도 0 · 계획 4"
}
