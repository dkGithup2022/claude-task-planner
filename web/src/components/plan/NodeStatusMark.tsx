import { cn } from "@/lib/utils";
import { PLAN_NODE_STATUS_LABEL, type PlanNodeStatus } from "@/types/data/domain/plan-node";
import type { NodeStatusMarkProps } from "./NodeStatusMark.types";

/** 웹 UI 문서 1번 화면의 기호. 흑백이라 색 대신 기호로 가른다. */
const MARK: Record<PlanNodeStatus, { symbol: string; className: string }> = {
  done: { symbol: "●", className: "text-foreground" },
  running: { symbol: "◐", className: "text-foreground font-medium" },
  todo: { symbol: "○", className: "text-text-tertiary" },
  failed: { symbol: "✕", className: "text-foreground font-medium" },
  skipped: { symbol: "–", className: "text-text-tertiary line-through" },
};

export function NodeStatusMark({ status }: NodeStatusMarkProps) {
  const mark = MARK[status];
  return (
    <span className={cn("whitespace-nowrap", mark.className)}>
      <span aria-hidden="true">{mark.symbol} </span>
      {PLAN_NODE_STATUS_LABEL[status]}
    </span>
  );
}
