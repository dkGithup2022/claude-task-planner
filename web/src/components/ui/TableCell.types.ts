import type { TdHTMLAttributes } from "react";

export type TableCellTone = "default" | "secondary" | "tertiary";

export interface TableCellProps extends TdHTMLAttributes<HTMLTableCellElement> {
  tone?: TableCellTone;
}
