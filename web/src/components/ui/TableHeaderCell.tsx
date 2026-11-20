import { cn } from "@/lib/utils";
import type { TableHeaderCellProps } from "./TableHeaderCell.types";

export function TableHeaderCell({ className, scope = "col", ...rest }: TableHeaderCellProps) {
  return (
    <th
      scope={scope}
      className={cn("border-b border-border px-1 py-2.5 text-[13px] font-medium text-text-secondary", className)}
      {...rest}
    />
  );
}
