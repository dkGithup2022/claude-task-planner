import type { Persona } from "@/types/data/domain/persona";

/** 페르소나 API. BE 확정 (be/specs/api.md 와 같다). docs/pages/plan-graph/api.md */

/** GET /api/personas 응답. persona_id 순, 지식 수·계획 수 포함 */
export interface PersonaListResponse {
  personas: Persona[];
}

/** POST /api/personas 요청. 같은 이름 409, 빈 이름 400 */
export interface PersonaCreateRequest {
  name: string;
  description: string;
}

/** PATCH /api/personas/{persona_id} 요청. 바꿀 필드만 */
export interface PersonaUpdateRequest {
  name?: string;
  description?: string;
}

/** POST·PATCH /api/personas 응답 */
export interface PersonaIdResponse {
  persona_id: number;
}
