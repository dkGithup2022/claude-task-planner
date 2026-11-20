import { cn } from "@/lib/utils";
import type { TextAreaFieldProps } from "./TextAreaField.types";

export function TextAreaField({ label, className, ...rest }: TextAreaFieldProps) {
  return (
    <label className={cn("flex flex-col gap-1 text-[12px] text-text-secondary", className)}>
      {label}
      <textarea className="min-h-11 border border-border bg-surface px-3 py-2.5 text-[14px] text-foreground focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-[var(--border-hover)] font-mono text-[13px] leading-normal" {...rest} />
    </label>
  );
}
