import type { HTMLAttributes } from "react";

export interface TableRowProps extends HTMLAttributes<HTMLTableRowElement> {
  /** 펼치거나 고른 줄 */
  selected?: boolean;
}
