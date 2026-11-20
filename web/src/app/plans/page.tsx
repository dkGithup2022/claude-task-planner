import { Suspense } from "react";
import type { Metadata } from "next";
import { PlansClient } from "./PlansClient";

export const metadata: Metadata = { title: "계획", description: "모든 계획을 만든 시각 최근 순으로" };

export default function Page() {
  return (
    <Suspense>
      <PlansClient />
    </Suspense>
  );
}
