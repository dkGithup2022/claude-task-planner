import { apiDelete, apiGet, apiPatch, toQueryParams } from "@/lib/api/client";
import type {
  MemoryDetailResponse,
  MemoryIdResponse,
  MemoryListParams,
  MemoryListResponse,
  MemoryUpdateRequest,
} from "@/types/api/memory";

/** 페이지: home (최근 지식, 종류별 개수), memories (지식 검색) */
export const fetchMemories = (params: MemoryListParams = {}) =>
  apiGet<MemoryListResponse>("/api/memories", toQueryParams(params), { skipAuth: true });

/** 페이지: memory-detail (조회, 저장 뒤 다시) */
export const fetchMemory = (memoryId: number) =>
  apiGet<MemoryDetailResponse>(`/api/memories/${memoryId}`, undefined, { skipAuth: true });

/** 페이지: memory-detail (수정 폼 저장. 바꿀 필드만) */
export const updateMemory = (memoryId: number, request: MemoryUpdateRequest) =>
  apiPatch<MemoryIdResponse>(`/api/memories/${memoryId}`, request, undefined, { skipAuth: true });

/** 페이지: memory-detail (지우기 확인) */
export const deleteMemory = (memoryId: number) =>
  apiDelete<null>(`/api/memories/${memoryId}`, undefined, undefined, { skipAuth: true });
