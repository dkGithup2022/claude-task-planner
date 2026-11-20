export type AppSection = "plans" | "memories" | "personas";

export interface AppHeaderProps {
  /** 지금 화면이 속한 메뉴. 메인이면 비운다 */
  current?: AppSection;
  /** 넓은 화면(계획 그래프, 1232px)에 맞춘다. 기본은 1120px */
  wide?: boolean;
}
