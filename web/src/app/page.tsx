import { Suspense } from "react";
import type { Metadata } from "next";
import { HomeClient } from "./HomeClient";

/**
 * 페이지 관례: page.tsx 는 서버 컴포넌트로 metadata 만 내보내고,
 * 상태와 이벤트가 있는 본문은 같은 폴더의 *Client.tsx 에 둔다.
 */
export const metadata: Metadata = {
  title: { absolute: "App" },
  description: "",
};

export default function Page() {
  return (
    <Suspense>
      <HomeClient />
    </Suspense>
  );
}
