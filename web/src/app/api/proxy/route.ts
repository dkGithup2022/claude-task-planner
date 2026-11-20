import ky, { HTTPError } from "ky";
import { NextRequest, NextResponse } from "next/server";
import { z } from "zod";

/**
 * 브라우저 → Next 서버 → 백엔드 프록시.
 * 브라우저는 백엔드 주소를 모른다. 쿠키는 양방향으로 전달한다.
 * 클라이언트 쪽 호출은 src/lib/api/client.ts 의 apiGet/apiPost 등을 쓴다.
 */
const ProxyRequestSchema = z.object({
  method: z.enum(["GET", "POST", "PUT", "PATCH", "DELETE"]),
  path: z.string().startsWith("/"),
  body: z.unknown().optional(),
  params: z
    .record(z.string(), z.union([z.string(), z.number(), z.boolean()]))
    .optional(),
});

function getBackendUrl(): string {
  const url = process.env.BACKEND_API_URL;
  if (!url) throw new Error("BACKEND_API_URL environment variable is not set");
  return url;
}

export async function POST(request: NextRequest) {
  try {
    const parsed = ProxyRequestSchema.safeParse(await request.json());
    if (!parsed.success) {
      return NextResponse.json(
        { error: "Invalid request format", status: 400, details: z.treeifyError(parsed.error) },
        { status: 400 },
      );
    }

    const { method, path, body, params } = parsed.data;
    const backend = ky.create({ prefix: getBackendUrl(), timeout: 30000, retry: { limit: 0 } });

    if (process.env.NODE_ENV === "development") {
      console.log(`[API Proxy] ${method} ${path}`);
    }

    const cookie = request.headers.get("cookie");
    const backendResponse = await backend(path.replace(/^\//, ""), {
      method,
      json: body,
      searchParams: params
        ? Object.fromEntries(Object.entries(params).map(([k, v]) => [k, String(v)]))
        : undefined,
      headers: {
        "Content-Type": "application/json",
        ...(cookie ? { Cookie: cookie } : {}),
      },
    });

    let data: unknown = null;
    const contentType = backendResponse.headers.get("content-type");
    if (backendResponse.headers.get("content-length") !== "0" && contentType?.includes("application/json")) {
      const text = await backendResponse.text();
      data = text ? JSON.parse(text) : null;
    }

    const response = NextResponse.json({ data, status: 200 }, { status: 200 });
    const setCookie = backendResponse.headers.get("set-cookie");
    if (setCookie) response.headers.set("Set-Cookie", setCookie);
    return response;
  } catch (error) {
    if (error instanceof HTTPError) {
      const data = error.data ?? null; // ky 가 오류 본문을 미리 읽어 data 에 둔다 (response.json() 은 이미 비어 있다)
      const message = (data as Record<string, string> | null)?.message;
      return NextResponse.json(
        {
          error: message || `Backend request failed (${error.response.status})`,
          status: error.response.status,
          data,
        },
        { status: error.response.status },
      );
    }
    console.error("[API Proxy] Error:", error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "Internal server error", status: 500 },
      { status: 500 },
    );
  }
}
