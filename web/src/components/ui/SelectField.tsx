import { cn } from "@/lib/utils";
import type { SelectFieldProps } from "./SelectField.types";

export function SelectField({ label, className, children, ...rest }: SelectFieldProps) {
  return (
    <label className={cn("flex flex-col gap-1 text-[12px] text-text-secondary", className)}>
      {label}
      <select className="min-h-11 border border-border bg-surface px-3 py-2.5 text-[14px] text-foreground focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[var(--border-hover)]" {...rest}>
        {children}
      </select>
    </label>
  );
}
