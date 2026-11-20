import type { ReactNode } from "react";

export interface SectionHeaderProps {
  title: ReactNode;
  /** 오른쪽 끝 (예: "전체 보기 →" 링크) */
  action?: ReactNode;
}
