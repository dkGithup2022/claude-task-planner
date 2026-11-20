import type { MemoryListParams, MemoryListResponse } from "@/types/api/memory";
import type { MemoryDetail, MemoryKind, MemoryListItem } from "@/types/data/domain/memory";
import seed from "./memory-data.seed.json";

/**
 * 지식 mock. 서버 DB 에 옮긴 tpm-trial 데이터(be/seed/tpm-trial)를 서버 응답 모양 그대로 둔다.
 * seed 에는 시각이 없어, 서버에 옮길 때처럼 모든 지식에 같은 시각을 둔다 (고친 적 없음).
 */
const IMPORTED_AT = "2026-11-20T08:56:00Z";
const APPENDED_MARK = "****** KNOWLEDGE APPENDED ";

const memories: MemoryDetail[] = seed.memories as MemoryDetail[];

function toListItem(memory: MemoryDetail): MemoryListItem {
  return {
    memory_id: memory.memory_id,
    kind: memory.kind,
    theme: memory.theme,
    persona_ids: memory.persona_ids,
    appended_count: memory.body.split(APPENDED_MARK).length - 1,
    source_plan_ids: [...new Set(memory.source.map((source) => source.plan_id))],
    created_at: IMPORTED_AT,
    updated_at: IMPORTED_AT,
    edited: false,
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
    .sort((a, b) => b.memory_id - a.memory_id)
    .map(toListItem);
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
