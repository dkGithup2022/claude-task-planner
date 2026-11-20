import { apiGet } from "@/lib/api/client";
import type { PersonaListResponse } from "@/types/api/persona";

/** 페이지: plan-graph (페르소나 이름), memories (필터), personas (목록) */
export const fetchPersonas = () => apiGet<PersonaListResponse>("/api/personas", undefined, { skipAuth: true });
