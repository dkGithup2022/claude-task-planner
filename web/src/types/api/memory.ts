import type { MemoryDetail, MemoryKind, MemoryListItem } from "@/types/data/domain/memory";
import type { MemorySource } from "@/types/data/domain/memory-source";

/**
 * 지식 API. BE 확정 (be/specs/api.md 와 같다). docs/pages/home/api.md
 */

/** GET /api/memories 요청 — Main.dc.html 최근 지식·종류별 개수, Memories.dc.html 필터 */
export interface MemoryListParams {
  q?: string;          // 작업 이름·본문에 들어 있는 글자
  kind?: MemoryKind;   // 이 종류만
  persona_id?: number; // 이 페르소나를 쓰는 지식만
  limit?: number;      // 최대 개수 (1~200). 없으면 전부
}

/** GET /api/memories 응답. 고친 시각 최근 순. total 은 limit 을 뺀 개수 */
export interface MemoryListResponse {
  items: MemoryListItem[];
  total: number;
}

/** GET /api/memories/{memory_id} 응답. 없으면 404 — docs/pages/memory-detail/api.md */
export type MemoryDetailResponse = MemoryDetail;

/** PATCH /api/memories/{memory_id} 요청. 바꿀 필드만 보낸다. 웹은 source 를 보내지 않는다 */
export interface MemoryUpdateRequest {
  kind?: MemoryKind;
  theme?: string;
  body?: string;
  persona_ids?: number[];
  source?: MemorySource[];
}

/** POST·PATCH /api/memories 응답 */
export interface MemoryIdResponse {
  memory_id: number;
}
