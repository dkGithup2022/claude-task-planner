import type { ProxyRequest } from "../types";
import { ApiError } from "../types";
import { mockHandlers, type MockHandler } from "./handlers";

const MOCK_LATENCY_MS = 150;

/** "/api/items/:id" 형태의 패턴을 정규식으로 바꾼다. */
function compile(pattern: string): { regex: RegExp; keys: string[] } {
  const keys: string[] = [];
  const source = pattern
    .replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
    .replace(/:(\w+)/g, (_, key: string) => {
      keys.push(key);
      return "([^/]+)";
    });
  return { regex: new RegExp(`^${source}$`), keys };
}

function match(handler: MockHandler, request: ProxyRequest): Record<string, string> | null {
  if (handler.method !== request.method) return null;
  const { regex, keys } = compile(handler.path);
  const m = request.path.match(regex);
  if (!m) return null;
  return Object.fromEntries(keys.map((key, i) => [key, decodeURIComponent(m[i + 1])]));
}

/** mock 모드에서 클라이언트 호출을 handlers.ts 로 라우팅한다. */
export async function handleMockRequest<T>(request: ProxyRequest): Promise<T> {
  await new Promise((resolve) => setTimeout(resolve, MOCK_LATENCY_MS));

  for (const handler of mockHandlers) {
    const pathParams = match(handler, request);
    if (pathParams) {
      return (await handler.resolve({
        pathParams,
        params: request.params ?? {},
        body: request.body,
      })) as T;
    }
  }

  throw new ApiError(`Mock handler not found: ${request.method} ${request.path}`, 404);
}
