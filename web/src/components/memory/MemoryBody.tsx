import { LabeledDivider } from "@/components/ui/LabeledDivider";
import { MarkdownText } from "@/components/ui/MarkdownText";
import { splitMemoryBody } from "@/lib/memory-body";
import type { MemoryBodyProps } from "./MemoryBody.types";

/** 본문을 "덧붙임 n" 구분선으로 나눠 보인다 (웹 UI 문서 3번 화면) */
export function MemoryBody({ body }: MemoryBodyProps) {
  const { base, appended } = splitMemoryBody(body);
  return (
    <div className="flex flex-col gap-4 leading-[1.7]">
      <MarkdownText>{base}</MarkdownText>
      {appended.map((part) => (
        <div key={part.number} className="flex flex-col gap-4">
          <LabeledDivider label={`덧붙임 ${part.number}`} />
          <MarkdownText>{part.text}</MarkdownText>
        </div>
      ))}
    </div>
  );
}
