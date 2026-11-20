/** 백엔드 페이지네이션 계약. 백엔드 형식에 맞게 수정한다. */
export interface PaginationParams {
  page?: number;
  size?: number;
}

export interface PaginatedResponse<T> {
  content: T[];
  totalElements: number;
  totalPages: number;
  page: number;
  size: number;
}
