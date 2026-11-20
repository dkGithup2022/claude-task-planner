export type MarkdownTextTone = "default" | "quote";

export interface MarkdownTextProps {
  /** md 원문 */
  children: string;
  /** quote: 길게 읽는 글 (명령서, 정의서, 인용) */
  tone?: MarkdownTextTone;
}
