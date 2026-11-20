import type { Metadata } from "next";
import { Noto_Sans_KR, Noto_Sans_Mono } from "next/font/google";
import { Toaster } from "sonner";
import "./globals.css";

/** 테마의 --font-body, --font-code 가 이 변수를 읽는다 (src/styles/themes/monochrome.css) */
const notoSansKr = Noto_Sans_KR({
  weight: ["400", "500", "700"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-noto-sans-kr",
});
const notoSansMono = Noto_Sans_Mono({
  weight: ["400"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-noto-sans-mono",
});

export const metadata: Metadata = {
  title: {
    default: "task plan manager",
    template: "%s | task plan manager",
  },
  description: "",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="ko" className={`${notoSansKr.variable} ${notoSansMono.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col">
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "var(--bg-surface)",
              color: "var(--text-primary)",
              border: "1px solid var(--border-default)",
            },
          }}
        />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
