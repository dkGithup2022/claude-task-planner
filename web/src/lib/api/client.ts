import ky, { HTTPError } from "ky";
import { z } from "zod";
import { ApiError } from "./types";
import type { HttpMethod, ProxyRequest, ProxyResponse, QueryParams } from "./types";
import { handleMockRequest } from "./mock";
import { isMockEnabled, shouldForceRealApi } from "./mock/enabled";

/**
 * 모든 백엔드 호출의 단일 진입점.
 * - mock 모드: src/lib/api/mock/handlers.ts 로 응답
 * - 브라우저: /api/proxy 를 거쳐 백엔드로
 * - 서버(SSR): 백엔드를 직접 호출, 요청 쿠키를 전달
 * 성공 시 data 만 돌려주고, 실패 시 ApiError 를 던진다.
 */

const API_PROXY_URL = "/api/proxy";
const RETRY = { limit: 2, methods: ["get"], statusCodes: [408, 413, 429, 500, 502, 503, 504] };

const ProxyResponseSchema = z.object({
  data: z.unknown().optional(),
  error: z.string().optional(),
  status: z.number(),
});

const proxyClient = ky.create({ timeout: 30000, retry: RETRY });

function getBackendUrl(): string {
  const url = process.env.BACKEND_API_URL;
  if (!url) throw new Error("BACKEND_API_URL environment variable is not set");
  return url;
}

function toSearchParams(params?: QueryParams): Record<string, string> | undefined {
  if (!params) return undefined;
  return Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)]));
}

/** 401/403 을 받으면 앱 전역에 알린다. 인증 Provider 가 이 이벤트를 구독해 로그아웃 처리한다. */
function notifyUnauthorized(error: ApiError): void {
  if (typeof window === "undefined") return;
  if (error.status !== 401 && error.status !== 403) return;
  window.dispatchEvent(
    new CustomEvent("auth:unauthorized", { detail: { status: error.status, message: error.message } }),
  );
}

async function callBackendDirect(request: ProxyRequest): Promise<unknown> {
  const backend = ky.create({ prefix: getBackendUrl(), timeout: 30000, retry: RETRY });
  const headers: Record<string, string> = {};

  if (!request.options?.skipAuth) {
    try {
      const { headers: nextHeaders } = await import("next/headers");
      const cookie = (await nextHeaders()).get("cookie");
      if (cookie) headers.Cookie = cookie;
    } catch {
      throw new Error(
        `Cannot use authenticated API in static generation. Path: ${request.path}. ` +
          `Use { skipAuth: true } for public APIs.`,
      );
    }
  }

  try {
    const data = await backend(request.path.replace(/^\//, ""), {
      method: request.method,
      json: request.body,
      searchParams: toSearchParams(request.params),
      headers,
    }).json<unknown>();
    return { data, status: 200 };
  } catch (err) {
    if (!(err instanceof HTTPError)) throw err;
    const data = await err.response.json().catch(() => null);
    const record = data as Record<string, string> | null;
    return { error: record?.message || record?.error || err.message, status: err.response.status, data };
  }
}

async function callApi<T>(request: ProxyRequest): Promise<T> {
  try {
    if (isMockEnabled() && !shouldForceRealApi(request.path)) {
      return await handleMockRequest<T>(request);
    }

    const raw =
      typeof window === "undefined"
        ? await callBackendDirect(request)
        : await proxyClient.post(API_PROXY_URL, { json: request }).json<unknown>();

    const parsed = ProxyResponseSchema.safeParse(raw);
    if (!parsed.success) {
      throw new ApiError("Invalid response format from server", 500, z.treeifyError(parsed.error));
    }

    const result = parsed.data as ProxyResponse<T>;
    if (result.error) throw new ApiError(result.error, result.status, result.data);
    if (result.data === undefined) throw new ApiError("No data in response", result.status);
    return result.data;
  } catch (error) {
    if (error instanceof ApiError) {
      notifyUnauthorized(error);
      throw error;
    }
    if (error instanceof HTTPError) {
      const data = await error.response.json().catch(() => null);
      const apiError = new ApiError(
        (data as Record<string, string> | null)?.error || error.message,
        error.response.status,
        data,
      );
      notifyUnauthorized(apiError);
      throw apiError;
    }
    throw new ApiError(error instanceof Error ? error.message : "Unknown error", 0);
  }
}

type CallOptions = ProxyRequest["options"];

function request<T>(method: HttpMethod) {
  return (path: string, body?: unknown, params?: QueryParams, options?: CallOptions) =>
    callApi<T>({ method, path, body, params, options });
}

export async function apiGet<T>(path: string, params?: QueryParams, options?: CallOptions): Promise<T> {
  return callApi<T>({ method: "GET", path, params, options });
}
export const apiPost = <T>(path: string, body?: unknown, params?: QueryParams, options?: CallOptions) =>
  request<T>("POST")(path, body, params, options);
export const apiPut = <T>(path: string, body?: unknown, params?: QueryParams, options?: CallOptions) =>
  request<T>("PUT")(path, body, params, options);
export const apiPatch = <T>(path: string, body?: unknown, params?: QueryParams, options?: CallOptions) =>
  request<T>("PATCH")(path, body, params, options);
export const apiDelete = <T>(path: string, body?: unknown, params?: QueryParams, options?: CallOptions) =>
  request<T>("DELETE")(path, body, params, options);

/** 선택 파라미터 객체에서 undefined · null · "" 를 걷어내 QueryParams 로 만든다. */
export function toQueryParams(params: object): QueryParams {
  return Object.fromEntries(
    Object.entries(params).filter(([, value]) => value !== undefined && value !== null && value !== ""),
  ) as QueryParams;
}
