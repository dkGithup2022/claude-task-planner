import { Suspense } from "react";
import type { Metadata } from "next";
import { PersonasClient } from "./PersonasClient";

export const metadata: Metadata = { title: "페르소나", description: "작업을 맡는 역할을 만들고 고치고 지운다" };

export default function Page() {
  return (
    <Suspense>
      <PersonasClient />
    </Suspense>
  );
}
