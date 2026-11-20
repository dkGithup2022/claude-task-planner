import { apiDelete, apiGet, apiPatch, apiPost } from "@/lib/api/client";
import type {
  PersonaCreateRequest,
  PersonaIdResponse,
  PersonaListResponse,
  PersonaUpdateRequest,
} from "@/types/api/persona";

/** 페이지: plan-graph (페르소나 이름), memories (필터), memory-detail, personas (목록) */
export const fetchPersonas = () => apiGet<PersonaListResponse>("/api/personas", undefined, { skipAuth: true });

/** 페이지: personas (만들기 폼) */
export const createPersona = (request: PersonaCreateRequest) =>
  apiPost<PersonaIdResponse>("/api/personas", request, undefined, { skipAuth: true });

/** 페이지: personas (수정 폼. 바꿀 필드만) */
export const updatePersona = (personaId: number, request: PersonaUpdateRequest) =>
  apiPatch<PersonaIdResponse>(`/api/personas/${personaId}`, request, undefined, { skipAuth: true });

/** 페이지: personas (삭제. 쓰는 지식·계획이 있으면 409) */
export const deletePersona = (personaId: number) =>
  apiDelete<null>(`/api/personas/${personaId}`, undefined, undefined, { skipAuth: true });
