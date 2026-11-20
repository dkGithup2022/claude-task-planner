import type { NodeProgressProps } from "./NodeProgress.types";

/** 완료·건너뜀 / 전체. 실패가 있으면 "(실패 n)" 을 붙인다. 예: "10/10", "6/9 (실패 1)" */
export function NodeProgress({ counts }: NodeProgressProps) {
  const finished = counts.done + counts.skipped;
  return (
    <span className="whitespace-nowrap tabular-nums">
      {finished}/{counts.total}
      {counts.failed > 0 && <span className="font-medium"> (실패 {counts.failed})</span>}
    </span>
  );
}
