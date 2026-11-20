import type { MemoryKind } from "@/types/data/domain/memory";

/** memories 페이지 전용. 검색 줄의 값. 주소 쿼리 ?q=&kind=&persona_id= 와 같다 — Memories.dc.html */
export interface MemoryFilter {
  q: string;                // "검색어 (작업 이름·본문)"
  kind: MemoryKind | "";    // "종류" — "" 는 전체
  personaId: number | null; // "페르소나" — null 은 전체
}
