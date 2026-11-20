import { ApiError } from "@/lib/api/types";
import type { MemoryIdResponse, MemoryListParams, MemoryListResponse, MemoryUpdateRequest } from "@/types/api/memory";
import type { MemoryDetail, MemoryKind, MemoryListItem } from "@/types/data/domain/memory";
import seed from "./memory-data.seed.json";

/**
 * 지식 mock. 서버 DB 에 옮긴 tpm-trial 데이터(be/seed/tpm-trial)를 서버 응답 모양 그대로 둔다.
 * seed 에는 시각이 없어, 서버에 옮길 때처럼 모든 지식에 같은 시각을 둔다 (고친 적 없음).
 */
const IMPORTED_AT = "2026-11-20T08:56:00Z";
const APPENDED_MARK = "****** KNOWLEDGE APPENDED ";

const memories: MemoryDetail[] = (seed.memories as MemoryDetail[]).map((memory) => ({ ...memory }));
/** 고친 시각. 고치면 여기에 남는다 (목록의 edited, 순서) */
const updatedAt = new Map<number, string>();

function toListItem(memory: MemoryDetail): MemoryListItem {
  return {
    memory_id: memory.memory_id,
    kind: memory.kind,
    theme: memory.theme,
    persona_ids: memory.persona_ids,
    appended_count: memory.body.split(APPENDED_MARK).length - 1,
    source_plan_ids: [...new Set(memory.source.map((source) => source.plan_id))],
    created_at: IMPORTED_AT,
    updated_at: updatedAt.get(memory.memory_id) ?? IMPORTED_AT,
    edited: updatedAt.has(memory.memory_id),
  };
}

/**
 * GET /api/memories
 * case 1: 인자 {}
 *   정상 응답: { items: 지식 7개 (고친 시각이 같아 id 큰 순), total: 7 }
 * case 2: 인자 { kind: "plan", limit: 1 }
 *   정상 응답: { items: 계획 지식 1개, total: 4 }
 * case 3: 인자 { q: "기획" }
 *   정상 응답: 작업 이름이나 본문에 "기획" 이 있는 지식 (대소문자 무시)
 * case 4: 인자 { persona_id: 2 }
 *   정상 응답: { items: 지식 #2, total: 1 }
 */
export function getMemoryList(params: MemoryListParams): MemoryListResponse {
  const query = (params.q ?? "").toLowerCase();
  const matched = memories
    .filter((memory) => params.kind === undefined || memory.kind === params.kind)
    .filter((memory) => params.persona_id === undefined || memory.persona_ids.includes(params.persona_id))
    .filter(
      (memory) =>
        !query || memory.theme.toLowerCase().includes(query) || memory.body.toLowerCase().includes(query),
    )
    .map(toListItem)
    .sort((a, b) => b.updated_at.localeCompare(a.updated_at) || b.memory_id - a.memory_id);
  return {
    items: params.limit === undefined ? matched : matched.slice(0, params.limit),
    total: matched.length,
  };
}

/** mock 쿼리 값(문자열)을 MemoryKind 로. 모르는 값이면 undefined */
export function toMemoryKind(value: unknown): MemoryKind | undefined {
  return value === "knowledge" || value === "attitude" || value === "plan" ? value : undefined;
}

/** 페르소나 mock 의 지식 수 세기에 쓴다 */
export function getAllMemoryDetails(): MemoryDetail[] {
  return memories;
}

function findMemory(id: number): MemoryDetail {
  const memory = memories.find((item) => item.memory_id === id);
  if (!memory) throw new ApiError("해당 리소스를 찾을 수 없습니다", 404);
  return memory;
}

/**
 * GET /api/memories/:id
 * case 1: 인자 { id: 1 }
 *   정상 응답: 지식 #1 (본문에 덧붙임 머리 3개, 근거 4개)
 * case 2: 인자 { id: 없는 지식 }
 *   예외: 404
 */
export function getMemoryDetail(id: number): MemoryDetail {
  return findMemory(id);
}

/**
 * PATCH /api/memories/:id
 * case 1: 인자 { id: 1, body: { theme: "새 이름" } }
 *   동작: 보낸 필드만 바꾸고 고친 시각을 남긴다 (목록의 edited = true, 맨 앞)
 *   정상 응답: { memory_id: 1 }
 * case 2: 인자 { id: 없는 지식 }
 *   예외: 404
 * case 3: 인자 { theme: "" }
 *   예외: 400 "잘못된 요청입니다"
 */
export function updateMemory(id: number, request: MemoryUpdateRequest): MemoryIdResponse {
  const memory = findMemory(id);
  if (request.theme === "" || request.body === "") throw new ApiError("잘못된 요청입니다", 400);
  Object.assign(memory, Object.fromEntries(Object.entries(request).filter(([, value]) => value !== undefined)));
  updatedAt.set(id, new Date().toISOString().replace(/\.\d+Z$/, "Z"));
  return { memory_id: id };
}

/**
 * DELETE /api/memories/:id
 * case 1: 인자 { id: 있는 지식 }
 *   동작: 목록과 조회에서 빠진다
 *   정상 응답: null (204)
 * case 2: 인자 { id: 없는 지식 }
 *   예외: 404
 */
export function deleteMemory(id: number): null {
  const memory = findMemory(id);
  memories.splice(memories.indexOf(memory), 1);
  return null;
}
