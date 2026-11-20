import { TableCell } from "@/components/ui/TableCell";
import { TableRow } from "@/components/ui/TableRow";
import { TextLink } from "@/components/ui/TextLink";
import { formatShortDateTime } from "@/lib/utils";
import { NodeProgress } from "./NodeProgress";
import type { PlanTableRowProps } from "./PlanTableRow.types";
import { PlanStatusMark } from "./PlanStatusMark";

/** 계획 목록 표의 한 줄. 제목을 누르면 계획 그래프 (/plans/{id}) */
export function PlanTableRow({ plan }: PlanTableRowProps) {
  return (
    <TableRow>
      <TableCell tone="tertiary">{plan.plan_id}</TableCell>
      <TableCell>
        <TextLink href={`/plans/${plan.plan_id}`}>{plan.title}</TextLink>
      </TableCell>
      <TableCell>
        <PlanStatusMark status={plan.status} />
      </TableCell>
      <TableCell tone="secondary">
        <NodeProgress counts={plan.node_counts} />
      </TableCell>
      <TableCell tone="tertiary">{formatShortDateTime(plan.created_at)}</TableCell>
    </TableRow>
  );
}
