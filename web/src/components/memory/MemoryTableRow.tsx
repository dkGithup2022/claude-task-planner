import { TableCell } from "@/components/ui/TableCell";
import { TableRow } from "@/components/ui/TableRow";
import { TextLink } from "@/components/ui/TextLink";
import { MEMORY_KIND_LABEL } from "@/types/data/domain/memory";
import type { MemoryTableRowProps } from "./MemoryTableRow.types";

/** 지식 검색 표의 한 줄. 작업 이름을 누르면 지식 조회 (/memories/{id}) */
export function MemoryTableRow({ memory, personaNames }: MemoryTableRowProps) {
  return (
    <TableRow>
      <TableCell tone="tertiary">{memory.memory_id}</TableCell>
      <TableCell>{MEMORY_KIND_LABEL[memory.kind]}</TableCell>
      <TableCell>
        <TextLink href={`/memories/${memory.memory_id}`}>{memory.theme}</TextLink>
      </TableCell>
      <TableCell tone="secondary">
        {memory.persona_ids.map((id) => personaNames.get(id) ?? `페르소나 ${id}`).join(", ") || "없음"}
      </TableCell>
      <TableCell>{memory.appended_count}</TableCell>
      <TableCell tone="secondary">{memory.source_plan_ids.join(", ") || "—"}</TableCell>
    </TableRow>
  );
}
