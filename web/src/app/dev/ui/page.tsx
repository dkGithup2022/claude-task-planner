import { Suspense } from "react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { UiGalleryClient } from "./UiGalleryClient";

export const metadata: Metadata = { title: "공용 컴포넌트" };

/** 공용 컴포넌트 확인 페이지. 개발에서만 보인다. */
export default function Page() {
  if (process.env.NODE_ENV === "production") notFound();
  return (
    <Suspense>
      <UiGalleryClient />
    </Suspense>
  );
}
