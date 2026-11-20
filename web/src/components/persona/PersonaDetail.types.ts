import type { Persona } from "@/types/data/domain/persona";
import type { PersonaFormValues } from "./PersonaForm.types";

export interface PersonaDetailProps {
  persona: Persona;
  editing: boolean;
  /** 저장·지우기 요청 중 */
  busy: boolean;
  /** 서버가 지우기를 거절한 문구 (409). 없으면 null */
  blockedMessage: string | null;
  onEdit: () => void;
  onCancelEdit: () => void;
  onSave: (values: PersonaFormValues) => void;
  onDelete: () => void;
}
