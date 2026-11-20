import type { Persona } from "@/types/data/domain/persona";

/** 페르소나 API. BE 확정 (be/specs/api.md 와 같다). docs/pages/plan-graph/api.md */

/** GET /api/personas 응답. persona_id 순, 지식 수·계획 수 포함 */
export interface PersonaListResponse {
  personas: Persona[];
}
