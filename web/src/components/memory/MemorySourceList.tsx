import { TextLink } from "@/components/ui/TextLink";
import type { MemorySourceListProps } from "./MemorySourceList.types";

/** 지식의 근거: 사용자가 한 말과 그 계획. 누르면 그 계획의 그래프로 */
export function MemorySourceList({ source, existingPlanIds }: MemorySourceListProps) {
  if (source.length === 0) return <p className="m-0 text-text-tertiary">근거가 없습니다.</p>;
  return (
    <ul className="m-0 flex list-none flex-col p-0">
      {source.map((item, index) => (
        <li key={index} className="flex flex-wrap gap-4 border-b border-border-subtle py-2.5">
          <q className="min-w-0 flex-[999_1_420px] text-quote">{item.quote}</q>
          {existingPlanIds.has(item.plan_id) ? (
            <TextLink href={`/plans/${item.plan_id}`}>계획 {item.plan_id} →</TextLink>
          ) : (
            <span className="text-text-tertiary">계획 {item.plan_id} (서버에 없음)</span>
          )}
        </li>
      ))}
    </ul>
  );
}
