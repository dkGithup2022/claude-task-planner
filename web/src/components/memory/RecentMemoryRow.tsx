import Link from "next/link";
import { formatShortDateTime } from "@/lib/utils";
import { MEMORY_KIND_LABEL } from "@/types/data/domain/memory";
import type { RecentMemoryRowProps } from "./RecentMemoryRow.types";

/** 메인의 최근 지식 한 줄. 누르면 지식 조회 (/memories/{id}) */
export function RecentMemoryRow({ memory }: RecentMemoryRowProps) {
  return (
    <Link
      href={`/memories/${memory.memory_id}`}
      className="flex flex-wrap items-center gap-4 border-b border-border-subtle px-1 py-3 hover:bg-secondary-bg"
    >
      <span className="w-8 text-text-tertiary tabular-nums">{memory.memory_id}</span>
      <span className="min-w-0 flex-[999_1_280px]">{memory.theme}</span>
      <span className="w-14 text-text-secondary">{MEMORY_KIND_LABEL[memory.kind]}</span>
      <span className="w-18 text-text-secondary">{memory.edited ? "고침" : "새로 저장"}</span>
      <span className="w-24 text-text-tertiary tabular-nums">{formatShortDateTime(memory.updated_at)}</span>
    </Link>
  );
}
