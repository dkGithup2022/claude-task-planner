import { apiGet, toQueryParams } from "@/lib/api/client";
import type { MemoryListParams, MemoryListResponse } from "@/types/api/memory";

/** 페이지: home (최근 지식, 종류별 개수), memories (지식 검색) */
export const fetchMemories = (params: MemoryListParams = {}) =>
  apiGet<MemoryListResponse>("/api/memories", toQueryParams(params), { skipAuth: true });
