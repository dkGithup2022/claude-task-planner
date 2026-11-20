import { cn } from "@/lib/utils";
import type { TableCellProps, TableCellTone } from "./TableCell.types";

const toneClass: Record<TableCellTone, string> = {
  default: "text-foreground",
  secondary: "text-text-secondary",
  tertiary: "text-text-tertiary",
};

export function TableCell({ tone = "default", className, ...rest }: TableCellProps) {
  return <td className={cn("px-1 py-3 align-top", toneClass[tone], className)} {...rest} />;
}
