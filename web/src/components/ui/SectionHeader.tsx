import type { SectionHeaderProps } from "./SectionHeader.types";

export function SectionHeader({ title, action }: SectionHeaderProps) {
  return (
    <div className="flex items-baseline gap-3">
      <h2 className="m-0 grow text-[13px] font-medium text-text-secondary">{title}</h2>
      {action && <span className="text-[13px]">{action}</span>}
    </div>
  );
}
