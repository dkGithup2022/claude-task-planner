"use client";

import { useEffect, useMemo, useState } from "react";
import { AppHeader } from "@/components/layout/AppHeader";
import { NodeDetailPanel } from "@/components/plan/NodeDetailPanel";
import { PlanGraphView } from "@/components/plan/PlanGraphView";
import { PlanSummaryHeader } from "@/components/plan/PlanSummaryHeader";
import { Notice } from "@/components/ui/Notice";
import { TextLink } from "@/components/ui/TextLink";
import { ApiError } from "@/lib/api/types";
import { showErrorToast } from "@/lib/api/error-toast";
import { fetchPersonas } from "@/lib/persona-api";
import { fetchPlan } from "@/lib/plan-api";
import type { Persona } from "@/types/data/domain/persona";
import type { PlanDetail } from "@/types/data/domain/plan";
import { PlanGraphSkeleton } from "./PlanGraphSkeleton";

const REFRESH_MS = 10_000; // 실행 중인 계획을 다시 읽는 간격 (웹 UI 문서 1번 화면)

/** 처음 고를 노드: 실행 중·실패한 노드가 있으면 그것, 없으면 첫 노드 */
function firstNodeId(plan: PlanDetail): number | null {
  const active = plan.nodes.find((node) => node.status === "running" || node.status === "failed");
  return (active ?? plan.nodes[0])?.node_id ?? null;
}

export function PlanGraphClient({ planId }: { planId: number }) {
  const [plan, setPlan] = useState<PlanDetail | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [error, setError] = useState<"not_found" | "failed" | null>(null);
  const [selectedNodeId, setSelectedNodeId] = useState<number | null>(null);
  const [showRequest, setShowRequest] = useState(false);

  useEffect(() => {
    Promise.all([fetchPlan(planId), fetchPersonas()])
      .then(([loaded, list]) => {
        setPlan(loaded);
        setPersonas(list.personas);
        setSelectedNodeId(firstNodeId(loaded));
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 404) {
          setError("not_found");
          return;
        }
        setError("failed");
        showErrorToast(err, "계획을 불러오지 못했습니다");
      });
  }, [planId]);

  const running = plan?.status === "running";
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      fetchPlan(planId)
        .then(setPlan)
        .catch((err) => showErrorToast(err, "계획을 다시 읽지 못했습니다"));
    }, REFRESH_MS);
    return () => clearInterval(timer);
  }, [planId, running]);

  const personaNames = useMemo(() => new Map(personas.map((p) => [p.persona_id, p.name])), [personas]);
  const selectedNode = plan?.nodes.find((node) => node.node_id === selectedNodeId) ?? null;

  return (
    <div>
      <AppHeader current="plans" wide />
      <main className="mx-auto flex max-w-[1232px] flex-col gap-5 px-6 pt-7 pb-12">
        {error === "not_found" && (
          <Notice>
            계획 {planId} 이 없습니다. <TextLink href="/plans">계획 목록으로 →</TextLink>
          </Notice>
        )}
        {error === "failed" && <Notice>불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요.</Notice>}
        {!error && !plan && <PlanGraphSkeleton />}
        {plan && (
          <>
            <PlanSummaryHeader
              plan={plan}
              personaNames={plan.persona_ids.map((id) => personaNames.get(id) ?? `페르소나 ${id}`)}
              autoRefresh={running}
              showRequest={showRequest}
              onToggleRequest={() => setShowRequest((open) => !open)}
            />
            <div className="flex flex-wrap items-start gap-6">
              <section aria-label="그래프" className="flex min-w-0 flex-[999_1_560px] flex-col gap-3">
                <PlanGraphView plan={plan} selectedNodeId={selectedNodeId} onSelect={setSelectedNodeId} />
                <p className="m-0 flex flex-wrap justify-center gap-x-5 gap-y-1 text-[12px] text-text-secondary">
                  <span>● 완료 (검정 테두리)</span>
                  <span>◐ 실행 중 (굵은 테두리)</span>
                  <span className="text-text-tertiary">○ 할 일 (회색)</span>
                  <span>✕ 실패 (점선 테두리)</span>
                  <span className="text-text-tertiary line-through">– 건너뜀</span>
                  <span>이중 테두리 = 확인 노드</span>
                </p>
              </section>
              <div className="min-w-0 flex-[1_1_360px]">
                {selectedNode ? (
                  <NodeDetailPanel
                    plan={plan}
                    node={selectedNode}
                    personaNames={personaNames}
                    onSelect={setSelectedNodeId}
                  />
                ) : (
                  <p className="m-0 text-text-tertiary">노드가 없습니다.</p>
                )}
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
}
