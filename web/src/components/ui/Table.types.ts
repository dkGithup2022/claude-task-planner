import type { ReactNode } from "react";

export interface TableProps {
  /** thead 와 tbody */
  children: ReactNode;
  /** 표의 최소 너비 (px). 화면이 좁으면 가로로 스크롤한다 */
  minWidth?: number;
  /** 표가 무엇인지 (스크린 리더) */
  caption?: string;
}
