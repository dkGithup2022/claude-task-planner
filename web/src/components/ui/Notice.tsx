import type { NoticeProps } from "./Notice.types";

/** 알림. 흑백 테마라 색 대신 굵은 테두리로 가른다. */
export function Notice({ children }: NoticeProps) {
  return (
    <div role="alert" className="flex flex-wrap items-center gap-3 border-2 border-border px-4 py-3">
      {children}
    </div>
  );
}
