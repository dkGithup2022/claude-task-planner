import type { ReactNode } from "react";

export interface PageHeadingProps {
  title: ReactNode;
  /** 제목 오른쪽의 보조 글 (개수, 정렬 기준 등) */
  meta?: ReactNode;
  /** 제목 오른쪽 끝의 버튼 */
  actions?: ReactNode;
}
