import type { NextConfig } from "next";

// 빌드 시 환경변수 스키마 검증 (src/env.mjs)
import "./src/env.mjs";

const nextConfig: NextConfig = {
  // 도커 배포용. .next/standalone 에 실행에 필요한 파일만 모은다 (infra/docker-compose.yml)
  output: "standalone",
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  async rewrites() {
    return [{ source: "/healthz", destination: "/api/health" }];
  },
};

export default nextConfig;
