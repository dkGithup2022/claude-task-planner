import { cn } from "@/lib/utils";
import type { CheckboxProps } from "./Checkbox.types";

export function Checkbox({ label, className, ...rest }: CheckboxProps) {
  return (
    <label className={cn("flex min-h-11 items-center gap-1.5 text-[13px]", className)}>
      <input type="checkbox" className="size-4 accent-[var(--accent-primary)]" {...rest} />
      {label}
    </label>
  );
}
