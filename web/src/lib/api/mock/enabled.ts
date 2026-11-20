export function isMockEnabled(): boolean {
  return process.env.NEXT_PUBLIC_USE_MOCK === "true";
}

/** mock 모드여도 실제 백엔드를 타야 하는 경로가 있으면 여기서 판별한다. 예: path.startsWith("/api/auth/") */
export function shouldForceRealApi(path: string): boolean {
  void path;
  return false;
}
