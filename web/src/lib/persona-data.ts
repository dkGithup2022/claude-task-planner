import { ApiError } from "@/lib/api/types";
import type {
  PersonaCreateRequest,
  PersonaIdResponse,
  PersonaListResponse,
  PersonaUpdateRequest,
} from "@/types/api/persona";
import type { Persona } from "@/types/data/domain/persona";
import { getAllMemoryDetails } from "./memory-data";
import seed from "./persona-data.seed.json";
import { getAllPlanDetails } from "./plan-data";

/**
 * 페르소나 mock. 서버 DB 에 옮긴 tpm-trial 데이터(be/seed/tpm-trial). 지식 수·계획 수는 서버처럼 센다:
 * 지식은 persona_ids 에 있는 것, 계획은 참여 페르소나이거나 노드 담당인 것.
 */
const personas = (seed.personas as Omit<Persona, "memory_count" | "plan_count">[]).map((p) => ({ ...p }));

/**
 * GET /api/personas
 * case 1: 인자 없음
 *   정상 응답: { personas: [1 dankim-persona (지식 7, 계획 1), 2 be-developer (지식 1, 계획 0)] } persona_id 순
 */
export function getPersonaList(): PersonaListResponse {
  return {
    personas: [...personas]
      .sort((a, b) => a.persona_id - b.persona_id)
      .map((persona) => ({ ...persona, ...countUses(persona.persona_id) })),
  };
}

function countUses(personaId: number): Pick<Persona, "memory_count" | "plan_count"> {
  return {
    memory_count: getAllMemoryDetails().filter((memory) => memory.persona_ids.includes(personaId)).length,
    plan_count: getAllPlanDetails().filter(
      (plan) => plan.persona_ids.includes(personaId) || plan.nodes.some((node) => node.persona_ids.includes(personaId)),
    ).length,
  };
}

function findPersona(id: number) {
  const persona = personas.find((item) => item.persona_id === id);
  if (!persona) throw new ApiError("해당 리소스를 찾을 수 없습니다", 404);
  return persona;
}

function checkName(name: string, exceptId?: number) {
  if (!name.trim()) throw new ApiError("잘못된 요청입니다", 400);
  if (personas.some((item) => item.name === name && item.persona_id !== exceptId)) {
    throw new ApiError(`이름이 같은 페르소나가 있습니다: ${name}`, 409);
  }
}

/**
 * POST /api/personas
 * case 1: 인자 { name: "fe-developer", description: "" }
 *   동작: 목록 끝에 더한다 (지식 0, 계획 0)
 *   정상 응답: { persona_id: 가장 큰 id + 1 }
 * case 2: 인자 { name: 있는 이름 }
 *   예외: 409
 * case 3: 인자 { name: "" }
 *   예외: 400
 */
export function createPersona(request: PersonaCreateRequest): PersonaIdResponse {
  checkName(request.name);
  const persona_id = Math.max(0, ...personas.map((item) => item.persona_id)) + 1;
  personas.push({ persona_id, name: request.name, description: request.description });
  return { persona_id };
}

/**
 * PATCH /api/personas/:id
 * case 1: 인자 { id: 2, description: "새 설명" }
 *   동작: 보낸 필드만 바꾼다
 *   정상 응답: { persona_id: 2 }
 * case 2: 인자 { id: 없는 페르소나 }
 *   예외: 404
 * case 3: 인자 { id: 2, name: "dankim-persona" }
 *   예외: 409
 */
export function updatePersona(id: number, request: PersonaUpdateRequest): PersonaIdResponse {
  const persona = findPersona(id);
  if (request.name !== undefined) checkName(request.name, id);
  if (request.name !== undefined) persona.name = request.name;
  if (request.description !== undefined) persona.description = request.description;
  return { persona_id: id };
}

/**
 * DELETE /api/personas/:id
 * case 1: 인자 { id: 쓰는 곳 없는 페르소나 }
 *   동작: 목록에서 빠진다
 *   정상 응답: null (204)
 * case 2: 인자 { id: 1 (지식 7, 계획 1) }
 *   예외: 409 "지식 7개, 계획 1개가 이 페르소나를 씁니다"
 * case 3: 인자 { id: 없는 페르소나 }
 *   예외: 404
 */
export function deletePersona(id: number): null {
  const persona = findPersona(id);
  const uses = countUses(id);
  if (uses.memory_count > 0 || uses.plan_count > 0) {
    throw new ApiError(`지식 ${uses.memory_count}개, 계획 ${uses.plan_count}개가 이 페르소나를 씁니다`, 409);
  }
  personas.splice(personas.indexOf(persona), 1);
  return null;
}
