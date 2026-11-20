/**
 * Persona (도메인) — 작업을 맡는 역할. 필드 이름은 BE 응답 그대로
 * 근거 화면: Personas.dc.html, PlanGraph.dc.html, Memories.dc.html
 */
export interface Persona {
  persona_id: number;   // Personas.dc.html "#" 열
  name: string;         // Personas.dc.html "dankim-persona". 페르소나마다 다르다
  description: string;  // Personas.dc.html "사용자의 기본 작업 역할". 빈 문자열일 수 있다
  memory_count: number; // Personas.dc.html "지식 수 7"
  plan_count: number;   // Personas.dc.html "계획 수 1". 참여 또는 노드 담당인 계획
}
