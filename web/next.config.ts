import type { NextConfig } from "next";

// 빌드 시 환경변수 스키마 검증 (src/env.mjs)
import "./src/env.mjs";

const nextConfig: NextConfig = {
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
  async rewrites() {
    return [{ source: "/healthz", destination: "/api/health" }];
  },
};

export default nextConfig;
