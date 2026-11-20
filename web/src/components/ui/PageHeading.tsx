import type { PageHeadingProps } from "./PageHeading.types";

export function PageHeading({ title, meta, actions }: PageHeadingProps) {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <h1 className="m-0 grow text-[22px] font-bold">{title}</h1>
      {meta && <span className="text-[13px] text-text-tertiary">{meta}</span>}
      {actions}
    </div>
  );
}
