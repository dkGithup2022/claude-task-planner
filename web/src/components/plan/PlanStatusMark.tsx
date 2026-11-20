import { cn } from "@/lib/utils";
import { PLAN_STATUS_LABEL, type PlanStatus } from "@/types/data/domain/plan";
import type { PlanStatusMarkProps } from "./PlanStatusMark.types";

const MARK: Record<PlanStatus, { symbol: string; className: string }> = {
  done: { symbol: "●", className: "text-foreground" },
  running: { symbol: "◐", className: "text-foreground font-medium" },
  approved: { symbol: "○", className: "text-foreground" },
  reviewing: { symbol: "○", className: "text-foreground" },
  drafting: { symbol: "○", className: "text-text-tertiary" },
  rejected: { symbol: "–", className: "text-text-tertiary" },
};

export function PlanStatusMark({ status }: PlanStatusMarkProps) {
  const mark = MARK[status];
  return (
    <span className={cn("whitespace-nowrap", mark.className)}>
      <span aria-hidden="true">{mark.symbol} </span>
      {PLAN_STATUS_LABEL[status]}
    </span>
  );
}
