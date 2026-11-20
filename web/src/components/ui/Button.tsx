import { cn } from "@/lib/utils";
import type { ButtonProps, ButtonSize, ButtonVariant } from "./Button.types";

const variantClass: Record<ButtonVariant, string> = {
  primary: "bg-accent text-on-accent border border-accent hover:bg-accent-secondary",
  outline: "bg-surface text-foreground border border-border hover:bg-secondary-bg",
  subtle: "bg-surface text-foreground border border-accent-muted hover:bg-secondary-bg",
};

const sizeClass: Record<ButtonSize, string> = {
  sm: "min-h-9 px-3 text-[13px]",
  md: "min-h-10 px-4 text-[13px]",
};

export function Button({ variant = "outline", size = "md", className, type = "button", ...rest }: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        "inline-flex items-center justify-center gap-1 cursor-pointer disabled:cursor-not-allowed disabled:opacity-50",
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--border-hover)]",
        variantClass[variant],
        sizeClass[size],
        className,
      )}
      {...rest}
    />
  );
}
