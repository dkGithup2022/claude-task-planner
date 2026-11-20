import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { cn } from "@/lib/utils";
import type { MarkdownTextProps, MarkdownTextTone } from "./MarkdownText.types";

const toneClass: Record<MarkdownTextTone, string> = {
  default: "text-foreground",
  quote: "text-quote",
};

/** md 를 흑백 테마로 그린다. 제목은 본문보다 조금 굵게만, 코드는 회색 바탕의 mono. */
const components: Components = {
  h1: ({ children }) => <p className="m-0 font-bold">{children}</p>,
  h2: ({ children }) => <p className="m-0 font-bold">{children}</p>,
  h3: ({ children }) => <p className="m-0 font-bold">{children}</p>,
  h4: ({ children }) => <p className="m-0 font-bold">{children}</p>,
  p: ({ children }) => <p className="m-0">{children}</p>,
  ul: ({ children }) => <ul className="m-0 list-disc pl-5">{children}</ul>,
  ol: ({ children }) => <ol className="m-0 list-decimal pl-5">{children}</ol>,
  a: ({ href, children }) => (
    <a href={href} className="underline hover:text-accent-secondary" target="_blank" rel="noreferrer">
      {children}
    </a>
  ),
  pre: ({ children }) => (
    <pre className="m-0 overflow-x-auto bg-secondary-bg px-4 py-3.5 font-mono text-[13px] leading-normal [&_code]:bg-transparent [&_code]:p-0">
      {children}
    </pre>
  ),
  code: ({ className, children }) =>
    className ? (
      <code className={className}>{children}</code>
    ) : (
      <code className="bg-tertiary px-1 font-mono text-[13px]">{children}</code>
    ),
  table: ({ children }) => (
    <div className="overflow-x-auto">
      <table className="border-collapse text-[13px]">{children}</table>
    </div>
  ),
  th: ({ children }) => <th className="border border-border-subtle px-2 py-1 text-left font-medium">{children}</th>,
  td: ({ children }) => <td className="border border-border-subtle px-2 py-1">{children}</td>,
};

export function MarkdownText({ children, tone = "default" }: MarkdownTextProps) {
  return (
    <div className={cn("flex flex-col gap-2 break-words", toneClass[tone])}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {children}
      </ReactMarkdown>
    </div>
  );
}
