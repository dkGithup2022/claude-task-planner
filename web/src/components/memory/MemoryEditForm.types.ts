import type { MemoryDetail, MemoryKind } from "@/types/data/domain/memory";
import type { Persona } from "@/types/data/domain/persona";

/** 수정 폼의 입력값 */
export interface MemoryEditValues {
  theme: string;
  kind: MemoryKind;
  personaIds: number[];
  body: string;
}

export interface MemoryEditFormProps {
  memory: MemoryDetail;
  personas: Persona[];
  saving: boolean;
  onSave: (values: MemoryEditValues) => void;
  onCancel: () => void;
}
