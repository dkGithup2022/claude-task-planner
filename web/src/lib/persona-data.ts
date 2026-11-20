import type { PersonaListResponse } from "@/types/api/persona";
import type { Persona } from "@/types/data/domain/persona";
import { getAllMemoryDetails } from "./memory-data";
import seed from "./persona-data.seed.json";
import { getAllPlanDetails } from "./plan-data";

/**
 * 페르소나 mock. 서버 DB 에 옮긴 tpm-trial 데이터(be/seed/tpm-trial). 지식 수·계획 수는 서버처럼 센다:
 * 지식은 persona_ids 에 있는 것, 계획은 참여 페르소나이거나 노드 담당인 것.
 */
const personas = seed.personas as Omit<Persona, "memory_count" | "plan_count">[];

/**
 * GET /api/personas
 * case 1: 인자 없음
 *   정상 응답: { personas: [1 dankim-persona (지식 7, 계획 1), 2 be-developer (지식 1, 계획 0)] } persona_id 순
 */
export function getPersonaList(): PersonaListResponse {
  const memories = getAllMemoryDetails();
  const plans = getAllPlanDetails();
  return {
    personas: [...personas]
      .sort((a, b) => a.persona_id - b.persona_id)
      .map((persona) => ({
        ...persona,
        memory_count: memories.filter((memory) => memory.persona_ids.includes(persona.persona_id)).length,
        plan_count: plans.filter(
          (plan) =>
            plan.persona_ids.includes(persona.persona_id) ||
            plan.nodes.some((node) => node.persona_ids.includes(persona.persona_id)),
        ).length,
      })),
  };
}
