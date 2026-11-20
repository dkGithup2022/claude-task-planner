import { cn } from "@/lib/utils";
import type { TextFieldProps } from "./TextField.types";

export function TextField({ label, className, type = "text", ...rest }: TextFieldProps) {
  return (
    <label className={cn("flex flex-col gap-1 text-[12px] text-text-secondary", className)}>
      {label}
      <input type={type} className="min-h-11 border border-border bg-surface px-3 py-2.5 text-[14px] text-foreground focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[var(--border-hover)]" {...rest} />
    </label>
  );
}
