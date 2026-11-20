export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

export type QueryParams = Record<string, string | number | boolean>;

export interface ProxyRequest {
  method: HttpMethod;
  path: string;
  body?: unknown;
  params?: QueryParams;
  options?: {
    /** SSR 에서 쿠키 전달을 생략한다. 정적 생성되는 공개 API 에 사용 */
    skipAuth?: boolean;
  };
}

export interface ProxyResponse<T = unknown> {
  data?: T;
  error?: string;
  status: number;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}
