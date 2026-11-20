import type { HttpMethod, QueryParams } from "../types";

export interface MockContext {
  /** "/api/items/:id" 의 :id 같은 경로 파라미터 */
  pathParams: Record<string, string>;
  /** 쿼리스트링 */
  params: QueryParams;
  /** 요청 본문 */
  body: unknown;
}

export interface MockHandler {
  method: HttpMethod;
  /** "/api/items" 또는 "/api/items/:id". 앞에서부터 순서대로 매칭한다. */
  path: string;
  resolve: (ctx: MockContext) => unknown | Promise<unknown>;
}

/**
 * mock 응답 등록 지점.
 * API 를 추가할 때 여기에 한 항목을 추가한다. 데이터는 src/lib/{domain}-data.ts 에 두고 여기서는 호출만 한다.
 *
 * 예시:
 * { method: "GET", path: "/api/items", resolve: ({ params }) => getItems(params) },
 * { method: "GET", path: "/api/items/:id", resolve: ({ pathParams }) => getItem(Number(pathParams.id)) },
 */
export const mockHandlers: MockHandler[] = [
  { method: "GET", path: "/api/health", resolve: () => ({ status: "ok", mock: true }) },
];
