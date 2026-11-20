"use client";

import { useEffect, useState } from "react";
import { apiGet } from "@/lib/api/client";
import { showErrorToast } from "@/lib/api/error-toast";

export function HomeClient() {
  const [status, setStatus] = useState<string>("...");

  useEffect(() => {
    apiGet<{ status: string }>("/api/health", undefined, { skipAuth: true })
      .then((res) => setStatus(res.status))
      .catch((err) => {
        setStatus("error");
        showErrorToast(err, "상태 확인 실패");
      });
  }, []);

  return (
    <div className="mx-auto max-w-[1000px] px-6 py-12">
      <h1 className="text-2xl font-semibold">nextjs-fe-base</h1>
      <p className="mt-2 text-sm text-text-secondary">
        api: <span className="font-mono">{status}</span>
      </p>
    </div>
  );
}
