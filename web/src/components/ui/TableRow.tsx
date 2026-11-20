import { cn } from "@/lib/utils";
import type { TableRowProps } from "./TableRow.types";

export function TableRow({ selected, className, ...rest }: TableRowProps) {
  return (
    <tr
      aria-selected={selected || undefined}
      className={cn("border-b border-border-subtle", selected && "bg-secondary-bg", className)}
      {...rest}
    />
  );
}
