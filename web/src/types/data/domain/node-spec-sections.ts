/**
 * NodeSpecSections (값 타입) — 노드 패널이 output_spec md 에서 나눠 보이는 절. 저장하지 않는다
 * 근거 화면: PlanGraph.dc.html 하는 일 · 산출물 · 그 외 설명
 * 나누는 규칙은 CLI 의 NodeSpec 과 같다. 없으면 ""
 */
export interface NodeSpecSections {
  does: string;            // "### 하는 일"
  output_form: string;     // "### 산출물" 첫 줄 "- 형태: 문서"
  output_contents: string; // "### 산출물" 의 나머지
  notes: string;           // "### 그 외 설명"
}
