import { deleteMemory, getMemoryDetail, getMemoryList, toMemoryKind, updateMemory } from "@/lib/memory-data";
import { createPersona, deletePersona, getPersonaList, updatePersona } from "@/lib/persona-data";
import { getPlanDetail, getPlanList } from "@/lib/plan-data";
import type { MemoryUpdateRequest } from "@/types/api/memory";
import type { PersonaCreateRequest, PersonaUpdateRequest } from "@/types/api/persona";
import type { PlanStatus } from "@/types/data/domain/plan";
import type { HttpMethod, QueryParams } from "../types";

const optionalNumber = (value: unknown) => (value === undefined ? undefined : Number(value));

export interface MockContext {
  /** "/api/items/:id" 의 :id 같은 경로 파라미터 */
  pathParams: Record<string, string>;
  /** 쿼리스트링 */
  params: QueryParams;
  /** 요청 본문 */
  body: unknown;
}

export interface MockHandler {
  method: HttpMethod;
  /** "/api/items" 또는 "/api/items/:id". 앞에서부터 순서대로 매칭한다. */
  path: string;
  resolve: (ctx: MockContext) => unknown | Promise<unknown>;
}

/**
 * mock 응답 등록 지점.
 * API 를 추가할 때 여기에 한 항목을 추가한다. 데이터는 src/lib/{domain}-data.ts 에 두고 여기서는 호출만 한다.
 *
 * 예시:
 * { method: "GET", path: "/api/items", resolve: ({ params }) => getItems(params) },
 * { method: "GET", path: "/api/items/:id", resolve: ({ pathParams }) => getItem(Number(pathParams.id)) },
 */
export const mockHandlers: MockHandler[] = [
  { method: "GET", path: "/api/health", resolve: () => ({ status: "ok", mock: true }) },
  {
    method: "GET",
    path: "/api/plans",
    resolve: ({ params }) =>
      getPlanList({ status: params.status as PlanStatus | undefined, limit: optionalNumber(params.limit) }),
  },
  { method: "GET", path: "/api/plans/:id", resolve: ({ pathParams }) => getPlanDetail(Number(pathParams.id)) },
  { method: "GET", path: "/api/personas", resolve: () => getPersonaList() },
  {
    method: "GET",
    path: "/api/memories",
    resolve: ({ params }) =>
      getMemoryList({
        q: params.q === undefined ? undefined : String(params.q),
        kind: toMemoryKind(params.kind),
        persona_id: optionalNumber(params.persona_id),
        limit: optionalNumber(params.limit),
      }),
  },
  { method: "GET", path: "/api/memories/:id", resolve: ({ pathParams }) => getMemoryDetail(Number(pathParams.id)) },
  {
    method: "PATCH",
    path: "/api/memories/:id",
    resolve: ({ pathParams, body }) => updateMemory(Number(pathParams.id), body as MemoryUpdateRequest),
  },
  { method: "DELETE", path: "/api/memories/:id", resolve: ({ pathParams }) => deleteMemory(Number(pathParams.id)) },
  { method: "POST", path: "/api/personas", resolve: ({ body }) => createPersona(body as PersonaCreateRequest) },
  {
    method: "PATCH",
    path: "/api/personas/:id",
    resolve: ({ pathParams, body }) => updatePersona(Number(pathParams.id), body as PersonaUpdateRequest),
  },
  { method: "DELETE", path: "/api/personas/:id", resolve: ({ pathParams }) => deletePersona(Number(pathParams.id)) },
];
