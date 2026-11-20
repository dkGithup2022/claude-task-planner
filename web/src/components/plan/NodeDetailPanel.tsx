import { MarkdownText } from "@/components/ui/MarkdownText";
import { parseNodeSpec } from "@/lib/node-spec";
import { nextNodes, previousNodes } from "@/lib/plan-graph";
import { NODE_KIND_LABEL, type PlanNode } from "@/types/data/domain/plan-node";
import { NodeStatusMark } from "./NodeStatusMark";
import type { NodeDetailPanelProps } from "./NodeDetailPanel.types";

function NeighborList({
  title,
  nodes,
  onSelect,
}: {
  title: string;
  nodes: PlanNode[];
  onSelect: (nodeId: number) => void;
}) {
  return (
    <div className="flex flex-col gap-1">
      <h3 className="m-0 text-[12px] font-medium text-text-secondary">{title}</h3>
      {nodes.length === 0 && <span className="text-text-tertiary">없음</span>}
      {nodes.map((node) => (
        <button
          key={node.node_id}
          type="button"
          onClick={() => onSelect(node.node_id)}
          className="flex min-h-8 cursor-pointer gap-2 text-left hover:underline"
        >
          <span className="w-7 text-text-tertiary tabular-nums">{node.node_id}</span>
          <span className="grow">{node.title}</span>
          <NodeStatusMark status={node.status} />
        </button>
      ))}
    </div>
  );
}

function SpecSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <h3 className="m-0 text-[12px] font-medium text-text-secondary">{title}</h3>
      {children}
    </div>
  );
}

/** 고른 노드의 자세한 정보: 머리, 앞뒤 노드, 정의서 (웹 UI 문서 1번 화면) */
export function NodeDetailPanel({ plan, node, personaNames, onSelect }: NodeDetailPanelProps) {
  const spec = parseNodeSpec(node.output_spec);
  const owners = node.persona_ids.map((id) => personaNames.get(id) ?? `페르소나 ${id}`);
  return (
    <aside aria-label={`노드 ${node.node_id} 자세히`} className="flex flex-col border border-border">
      <div className="flex flex-col gap-0.5 border-b border-border-subtle px-5 py-4">
        <span className="text-[12px] text-text-tertiary">노드 {node.node_id}</span>
        <div className="flex items-baseline gap-3">
          <h2 className="m-0 grow text-[17px] font-bold">{node.title}</h2>
          <NodeStatusMark status={node.status} />
        </div>
        <span className="text-[13px] text-text-secondary">
          {NODE_KIND_LABEL[node.kind]} · 담당 {owners.length > 0 ? owners.join(", ") : "없음"}
        </span>
      </div>
      <div className="flex flex-col gap-3 border-b border-border-subtle px-5 py-4 text-[13px]">
        <NeighborList title="받는 산출물 (앞 노드)" nodes={previousNodes(plan, node.node_id)} onSelect={onSelect} />
        <NeighborList title="넘기는 곳 (뒤 노드)" nodes={nextNodes(plan, node.node_id)} onSelect={onSelect} />
      </div>
      <div className="flex flex-col gap-3 px-5 py-4 text-[13px]">
        <SpecSection title="하는 일">
          <MarkdownText tone="quote">{spec.does || "(없음)"}</MarkdownText>
        </SpecSection>
        <SpecSection title="산출물">
          <p className="m-0 text-quote">형태: {spec.output_form || "정하지 않음"}</p>
          {spec.output_contents && <MarkdownText tone="quote">{spec.output_contents}</MarkdownText>}
        </SpecSection>
        <SpecSection title="그 외 설명">
          <MarkdownText tone="quote">{spec.notes || "(없음)"}</MarkdownText>
        </SpecSection>
      </div>
    </aside>
  );
}
