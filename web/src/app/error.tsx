"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center px-4">
      <h2 className="mb-4 text-2xl font-bold">문제가 발생했습니다</h2>
      <p className="mb-8 max-w-md text-center text-sm text-text-secondary">
        페이지를 불러오는 중 오류가 발생했습니다. 다시 시도해주세요.
      </p>
      <button
        onClick={reset}
        className="cursor-pointer rounded-lg border border-border px-4 py-2 text-sm font-medium transition-opacity hover:opacity-80"
      >
        다시 시도
      </button>
    </div>
  );
}
