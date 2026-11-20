import { Suspense } from "react";
import type { Metadata } from "next";
import { MemoriesClient } from "./MemoriesClient";

export const metadata: Metadata = { title: "지식", description: "작업 이름·본문으로 지식을 찾는다" };

export default function Page() {
  return (
    <Suspense>
      <MemoriesClient />
    </Suspense>
  );
}
