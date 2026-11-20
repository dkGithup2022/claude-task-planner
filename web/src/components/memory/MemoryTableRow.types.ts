import type { MemoryListItem } from "@/types/data/domain/memory";

export interface MemoryTableRowProps {
  memory: MemoryListItem;
  /** persona_id → 이름 */
  personaNames: Map<number, string>;
}
