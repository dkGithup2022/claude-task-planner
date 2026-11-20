import { Suspense } from "react";
import type { Metadata } from "next";
import { HomeClient } from "./HomeClient";

export const metadata: Metadata = {
  title: { absolute: "task plan manager" },
  description: "작업 계획과 지식을 한눈에",
};

export default function Page() {
  return (
    <Suspense>
      <HomeClient />
    </Suspense>
  );
}
