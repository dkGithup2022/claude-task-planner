/**
 * MemorySource (값 타입) — 지식의 근거. 사용자가 한 말과 그 말이 나온 계획
 * 근거 화면: MemoryDetail.dc.html
 */
export interface MemorySource {
  quote: string;   // MemoryDetail.dc.html 근거의 인용
  plan_id: number; // MemoryDetail.dc.html "계획 11 →"
}
