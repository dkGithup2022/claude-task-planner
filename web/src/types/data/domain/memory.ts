import type { MemorySource } from "./memory-source";

/**
 * Memory (도메인) — 작업할 때 쓰는 지식 하나
 * 근거 화면: Memories.dc.html, MemoryDetail.dc.html, Main.dc.html
 * 목록 한 줄(MemoryListItem)과 조회(MemoryDetail)는 BE 응답의 필드가 달라 둘로 둔다
 * 보류: 검색 결과(MemorySearchHit) 는 CLI 용 API 라 웹에서 쓰지 않는다
 */
export interface MemoryListItem {
  memory_id: number;         // "지식 #1"
  kind: MemoryKind;          // Memories.dc.html "지식" · "계획"
  theme: string;             // Memories.dc.html "테이블 설계" (작업 이름)
  persona_ids: number[];     // Memories.dc.html "dankim-persona" (이름은 페르소나 목록으로 바꾼다)
  appended_count: number;    // Memories.dc.html "덧붙임 3"
  source_plan_ids: number[]; // Memories.dc.html "근거 계획 3, 11"
  created_at: string;        // 만든 시각 UTC "2026-11-20T04:39:00Z"
  updated_at: string;        // 고친 시각 UTC. 목록 순서
  edited: boolean;           // Main.dc.html "새로 저장"(false) / "고침"(true)
}

export interface MemoryDetail {
  memory_id: number;      // MemoryDetail.dc.html "지식 #1"
  kind: MemoryKind;       // MemoryDetail.dc.html "지식"
  theme: string;          // MemoryDetail.dc.html "테이블 설계"
  body: string;           // MemoryDetail.dc.html 본문. 덧붙임 머리 "****** KNOWLEDGE APPENDED <n> ********" 가 들어 있다
  persona_ids: number[];  // MemoryDetail.dc.html "dankim-persona"
  source: MemorySource[]; // MemoryDetail.dc.html 근거 (덧붙인 순서)
}

/** 지식 종류 (enum) — Main.dc.html, Memories.dc.html, MemoryDetail.dc.html. 값은 BE 의 소문자 */
export type MemoryKind = "knowledge" | "attitude" | "plan";
export const MEMORY_KIND_LABEL: Record<MemoryKind, string> = {
  knowledge: "지식",
  attitude: "태도",
  plan: "계획",
};
