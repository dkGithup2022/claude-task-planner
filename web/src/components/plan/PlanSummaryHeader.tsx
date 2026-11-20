import { Button } from "@/components/ui/Button";
import { MarkdownText } from "@/components/ui/MarkdownText";
import { formatShortDateTime } from "@/lib/utils";
import { PLAN_NODE_STATUS_LABEL } from "@/types/data/domain/plan-node";
import { PlanStatusMark } from "./PlanStatusMark";
import type { PlanSummaryHeaderProps } from "./PlanSummaryHeader.types";

/** 그래프 위쪽 세 줄: 번호·제목 / 상태·만든 시각·참여 페르소나 / 상태별 노드 수·다시 읽기·명령서 */
export function PlanSummaryHeader({
  plan,
  personaNames,
  autoRefresh,
  showRequest,
  onToggleRequest,
}: PlanSummaryHeaderProps) {
  const count = (status: keyof typeof PLAN_NODE_STATUS_LABEL) =>
    plan.nodes.filter((node) => node.status === status).length;
  const counts = (["done", "running", "todo", "failed", "skipped"] as const)
    .filter((status) => ["done", "running", "todo"].includes(status) || count(status) > 0)
    .map((status) => `${PLAN_NODE_STATUS_LABEL[status]} ${count(status)}`)
    .join(" · ");
  return (
    <section aria-label="계획 요약" className="flex flex-col gap-1 border-b border-border-subtle pb-4">
      <h1 className="m-0 text-[20px] font-bold">
        <span className="mr-2 font-normal text-text-tertiary">계획 {plan.plan_id}</span>
        {plan.title}
      </h1>
      <p className="m-0 text-text-secondary">
        <PlanStatusMark status={plan.status} /> · {formatShortDateTime(plan.created_at, true)} ·{" "}
        {personaNames.length > 0 ? personaNames.join(", ") : "참여 페르소나 없음"}
      </p>
      <div className="flex flex-wrap items-center gap-4">
        <span className="grow tabular-nums">{counts}</span>
        <span className="text-[12px] text-text-tertiary">
          {autoRefresh ? "실행 중이라 10초마다 새로 읽음" : "실행 중이 아니라 다시 읽지 않음"}
        </span>
        <Button size="sm" onClick={onToggleRequest} aria-expanded={showRequest}>
          명령서 {showRequest ? "접기 ▴" : "보기 ▾"}
        </Button>
      </div>
      {showRequest && (
        <div className="mt-2 bg-secondary-bg p-4 text-[13px]">
          <MarkdownText tone="quote">{plan.request}</MarkdownText>
        </div>
      )}
    </section>
  );
}
