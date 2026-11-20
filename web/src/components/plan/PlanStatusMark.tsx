import { cn } from "@/lib/utils";
import type { PlanStatusMarkProps, PlanStatusValue } from "./PlanStatusMark.types";

const MARK: Record<PlanStatusValue, { symbol: string; label: string; className: string }> = {
  done: { symbol: "●", label: "완료", className: "text-foreground" },
  running: { symbol: "◐", label: "실행 중", className: "text-foreground font-medium" },
  approved: { symbol: "○", label: "승인", className: "text-foreground" },
  reviewing: { symbol: "○", label: "검토 중", className: "text-foreground" },
  drafting: { symbol: "○", label: "만드는 중", className: "text-text-tertiary" },
  rejected: { symbol: "–", label: "불허", className: "text-text-tertiary" },
};

export function PlanStatusMark({ status }: PlanStatusMarkProps) {
  const mark = MARK[status];
  return (
    <span className={cn("whitespace-nowrap", mark.className)}>
      <span aria-hidden="true">{mark.symbol} </span>
      {mark.label}
    </span>
  );
}
