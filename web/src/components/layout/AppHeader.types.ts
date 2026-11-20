export type AppSection = "plans" | "memories" | "personas";

export interface AppHeaderProps {
  /** 지금 화면이 속한 메뉴. 메인이면 비운다 */
  current?: AppSection;
}
