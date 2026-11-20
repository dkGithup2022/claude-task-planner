import Link from "next/link";
import { formatShortDateTime } from "@/lib/utils";
import { NodeProgress } from "./NodeProgress";
import type { PlanListRowProps } from "./PlanListRow.types";
import { PlanStatusMark } from "./PlanStatusMark";

/** 계획 한 줄. 누르면 계획 그래프 (/plans/{id}) */
export function PlanListRow({ plan, show }: PlanListRowProps) {
  return (
    <Link
      href={`/plans/${plan.plan_id}`}
      className="flex flex-wrap items-center gap-4 border-b border-border-subtle px-1 py-3.5 hover:bg-secondary-bg"
    >
      <span className="w-8 text-text-tertiary tabular-nums">{plan.plan_id}</span>
      <span className="min-w-0 flex-[999_1_360px]">{plan.title}</span>
      <span className="w-22">
        <PlanStatusMark status={plan.status} />
      </span>
      {show === "progress" && (
        <span className="w-28 text-text-secondary">
          완료 <NodeProgress counts={plan.node_counts} />
        </span>
      )}
      {show === "node_total" && <span className="w-28 text-text-secondary">노드 {plan.node_counts.total}</span>}
      {show === "created" && (
        <>
          <span className="w-28 text-text-secondary">
            <NodeProgress counts={plan.node_counts} />
          </span>
          <span className="w-24 text-text-tertiary tabular-nums">{formatShortDateTime(plan.created_at)}</span>
        </>
      )}
    </Link>
  );
}
