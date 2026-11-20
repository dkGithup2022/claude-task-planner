import type { LabeledDividerProps } from "./LabeledDivider.types";

export function LabeledDivider({ label }: LabeledDividerProps) {
  return (
    <div className="flex items-center gap-3 text-[12px] text-text-tertiary">
      <span>{label}</span>
      <span aria-hidden="true" className="h-px grow bg-border-subtle" />
    </div>
  );
}
