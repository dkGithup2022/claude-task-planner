import { toast } from "sonner";
import { ApiError } from "./types";

/** API 실패를 토스트로 알린다. 401/403 은 인증 흐름이 처리하므로 조용히 넘긴다. */
export function showErrorToast(error: unknown, fallback: string): void {
  if (error instanceof ApiError) {
    if (error.status === 401 || error.status === 403) return;
    toast.error(error.message || fallback);
    return;
  }
  toast.error(error instanceof Error ? error.message || fallback : fallback);
}
