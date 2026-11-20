import { createEnv } from "@t3-oss/env-nextjs";
import { z } from "zod";

/**
 * 환경변수 스키마. 빌드/실행 시 검증된다.
 * - server: 서버에서만 접근 가능
 * - client: NEXT_PUBLIC_ 접두사, 브라우저 번들에 포함
 */
export const env = createEnv({
  server: {
    BACKEND_API_URL: z.string().url().optional(),
  },
  client: {
    NEXT_PUBLIC_BASE_URL: z.string().url().optional(),
    NEXT_PUBLIC_USE_MOCK: z
      .enum(["true", "false"])
      .optional()
      .transform((value) => value === "true"),
  },
  runtimeEnv: {
    BACKEND_API_URL: process.env.BACKEND_API_URL,
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL,
    NEXT_PUBLIC_USE_MOCK: process.env.NEXT_PUBLIC_USE_MOCK,
  },
});
