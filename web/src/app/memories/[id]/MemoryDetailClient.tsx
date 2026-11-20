"use client";

import { useRouter } from "next/navigation";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AppHeader } from "@/components/layout/AppHeader";
import { MemoryBody } from "@/components/memory/MemoryBody";
import { MemoryEditForm } from "@/components/memory/MemoryEditForm";
import type { MemoryEditValues } from "@/components/memory/MemoryEditForm.types";
import { MemorySourceList } from "@/components/memory/MemorySourceList";
import { Button } from "@/components/ui/Button";
import { Notice } from "@/components/ui/Notice";
import { TextLink } from "@/components/ui/TextLink";
import { showErrorToast } from "@/lib/api/error-toast";
import { ApiError } from "@/lib/api/types";
import { deleteMemory, fetchMemory, updateMemory } from "@/lib/memory-api";
import { splitMemoryBody } from "@/lib/memory-body";
import { fetchPersonas } from "@/lib/persona-api";
import { fetchPlans } from "@/lib/plan-api";
import { MEMORY_KIND_LABEL, type MemoryDetail } from "@/types/data/domain/memory";
import type { Persona } from "@/types/data/domain/persona";
import { MemoryDetailSkeleton } from "./MemoryDetailSkeleton";

type Mode = "view" | "editing" | "confirming";

export function MemoryDetailClient({ memoryId }: { memoryId: number }) {
  const router = useRouter();
  const [memory, setMemory] = useState<MemoryDetail | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [planIds, setPlanIds] = useState<Set<number>>(new Set());
  const [error, setError] = useState<"not_found" | "failed" | null>(null);
  const [mode, setMode] = useState<Mode>("view");
  const [busy, setBusy] = useState(false);

  const handleLoadError = useCallback((err: unknown) => {
    if (err instanceof ApiError && err.status === 404) {
      setError("not_found");
      return;
    }
    setError("failed");
    showErrorToast(err, "지식을 불러오지 못했습니다");
  }, []);

  useEffect(() => {
    Promise.all([fetchMemory(memoryId), fetchPersonas(), fetchPlans()])
      .then(([loaded, personaList, planList]) => {
        setMemory(loaded);
        setPersonas(personaList.personas);
        setPlanIds(new Set(planList.plans.map((plan) => plan.plan_id)));
      })
      .catch(handleLoadError);
  }, [memoryId, handleLoadError]);

  const personaNames = useMemo(() => new Map(personas.map((p) => [p.persona_id, p.name])), [personas]);

  const save = (values: MemoryEditValues) => {
    setBusy(true);
    updateMemory(memoryId, {
      theme: values.theme,
      kind: values.kind,
      persona_ids: values.personaIds,
      body: values.body,
    })
      .then(() => fetchMemory(memoryId))
      .then((loaded) => {
        setMemory(loaded);
        setMode("view");
      })
      .catch((err) => showErrorToast(err, "저장하지 못했습니다"))
      .finally(() => setBusy(false));
  };

  const remove = () => {
    setBusy(true);
    deleteMemory(memoryId)
      .then(() => router.push("/memories"))
      .catch((err) => {
        setBusy(false);
        showErrorToast(err, "지우지 못했습니다");
      });
  };

  return (
    <div>
      <AppHeader current="memories" />
      <main className="mx-auto flex max-w-[880px] flex-col gap-6 px-6 pt-8 pb-16">
        <TextLink href="/memories" tone="secondary" className="text-[13px]">
          ← 지식 목록
        </TextLink>
        {error === "not_found" && <Notice>지식 #{memoryId} 이 없습니다. 지웠거나 잘못된 주소입니다.</Notice>}
        {error === "failed" && <Notice>불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요.</Notice>}
        {!error && !memory && <MemoryDetailSkeleton />}
        {memory && (
          <>
            <div className="flex flex-wrap items-start gap-3">
              <div className="flex grow flex-col gap-0.5">
                <span className="text-[12px] text-text-tertiary">지식 #{memory.memory_id}</span>
                <h1 className="m-0 text-[24px] font-bold">{memory.theme}</h1>
                <span className="text-text-secondary">
                  {MEMORY_KIND_LABEL[memory.kind]} ·{" "}
                  {memory.persona_ids.map((id) => personaNames.get(id) ?? `페르소나 ${id}`).join(", ") || "페르소나 없음"}{" "}
                  · 덧붙임 {splitMemoryBody(memory.body).appended.length}
                </span>
              </div>
              <Button variant="primary" onClick={() => setMode(mode === "editing" ? "view" : "editing")} disabled={busy}>
                {mode === "editing" ? "수정 닫기" : "수정"}
              </Button>
              <Button onClick={() => setMode("confirming")} disabled={busy}>
                삭제
              </Button>
            </div>

            {mode === "confirming" && (
              <Notice>
                <span className="grow">
                  지식 #{memory.memory_id} &quot;{memory.theme}&quot; 를 지웁니다. 되돌릴 수 없습니다.
                </span>
                <Button variant="subtle" onClick={() => setMode("view")} disabled={busy}>
                  취소
                </Button>
                <Button variant="primary" onClick={remove} disabled={busy}>
                  지우기
                </Button>
              </Notice>
            )}

            {mode === "editing" && (
              <MemoryEditForm
                memory={memory}
                personas={personas}
                saving={busy}
                onSave={save}
                onCancel={() => setMode("view")}
              />
            )}

            <section aria-label="본문" className="flex flex-col gap-4">
              <h2 className="m-0 text-[13px] font-medium text-text-secondary">본문</h2>
              <MemoryBody body={memory.body} />
            </section>

            <section aria-label="근거" className="flex flex-col border-t border-border">
              <h2 className="mt-3 mb-1 text-[13px] font-medium text-text-secondary">근거</h2>
              <MemorySourceList source={memory.source} existingPlanIds={planIds} />
            </section>
          </>
        )}
      </main>
    </div>
  );
}
