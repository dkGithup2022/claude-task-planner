import type { MemorySource } from "@/types/data/domain/memory-source";

export interface MemorySourceListProps {
  source: MemorySource[];
  /** 서버에 있는 계획 id. 없는 계획은 링크 대신 "(서버에 없음)" 으로 보인다 */
  existingPlanIds: Set<number>;
}
