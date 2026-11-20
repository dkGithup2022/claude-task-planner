import { cn } from "@/lib/utils";
import type { NodeStatusMarkProps, NodeStatusValue } from "./NodeStatusMark.types";

/** 웹 UI 문서 1번 화면의 기호. 흑백이라 색 대신 기호로 가른다. */
const MARK: Record<NodeStatusValue, { symbol: string; label: string; className: string }> = {
  done: { symbol: "●", label: "완료", className: "text-foreground" },
  running: { symbol: "◐", label: "실행 중", className: "text-foreground font-medium" },
  todo: { symbol: "○", label: "할 일", className: "text-text-tertiary" },
  failed: { symbol: "✕", label: "실패", className: "text-foreground font-medium" },
  skipped: { symbol: "–", label: "건너뜀", className: "text-text-tertiary line-through" },
};

export function NodeStatusMark({ status }: NodeStatusMarkProps) {
  const mark = MARK[status];
  return (
    <span className={cn("whitespace-nowrap", mark.className)}>
      <span aria-hidden="true">{mark.symbol} </span>
      {mark.label}
    </span>
  );
}
