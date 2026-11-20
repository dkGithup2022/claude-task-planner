"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { AppHeader } from "@/components/layout/AppHeader";
import { MemoryTableRow } from "@/components/memory/MemoryTableRow";
import { EmptyState } from "@/components/ui/EmptyState";
import { Notice } from "@/components/ui/Notice";
import { PageHeading } from "@/components/ui/PageHeading";
import { SelectField } from "@/components/ui/SelectField";
import { Table } from "@/components/ui/Table";
import { TableHeaderCell } from "@/components/ui/TableHeaderCell";
import { TextField } from "@/components/ui/TextField";
import { showErrorToast } from "@/lib/api/error-toast";
import { fetchMemories } from "@/lib/memory-api";
import { fetchPersonas } from "@/lib/persona-api";
import type { MemoryListResponse } from "@/types/api/memory";
import { MEMORY_KIND_LABEL, type MemoryKind } from "@/types/data/domain/memory";
import type { Persona } from "@/types/data/domain/persona";
import type { MemoryFilter } from "./memories.types";
import { MemoriesSkeleton } from "./MemoriesSkeleton";

const SEARCH_DELAY_MS = 300; // 검색어 입력이 멈추고 부르기까지

function readFilter(params: URLSearchParams): MemoryFilter {
  const kind = params.get("kind");
  const personaId = Number(params.get("persona_id"));
  return {
    q: params.get("q") ?? "",
    kind: kind === "knowledge" || kind === "attitude" || kind === "plan" ? kind : "",
    personaId: Number.isInteger(personaId) && personaId > 0 ? personaId : null,
  };
}

function toQuery(filter: MemoryFilter): string {
  const params = new URLSearchParams();
  if (filter.q) params.set("q", filter.q);
  if (filter.kind) params.set("kind", filter.kind);
  if (filter.personaId) params.set("persona_id", String(filter.personaId));
  const text = params.toString();
  return text ? `?${text}` : "";
}

export function MemoriesClient() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const [filter, setFilter] = useState<MemoryFilter>(() => readFilter(searchParams));
  const [result, setResult] = useState<MemoryListResponse | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    fetchPersonas()
      .then((res) => setPersonas(res.personas))
      .catch((err) => showErrorToast(err, "페르소나를 불러오지 못했습니다"));
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace(`${pathname}${toQuery(filter)}`, { scroll: false });
      fetchMemories({ q: filter.q, kind: filter.kind || undefined, persona_id: filter.personaId ?? undefined })
        .then((res) => {
          setResult(res);
          setFailed(false);
        })
        .catch((err) => {
          setFailed(true);
          showErrorToast(err, "지식을 불러오지 못했습니다");
        });
    }, SEARCH_DELAY_MS);
    return () => clearTimeout(timer);
  }, [filter, pathname, router]);

  const personaNames = useMemo(() => new Map(personas.map((p) => [p.persona_id, p.name])), [personas]);

  return (
    <div>
      <AppHeader current="memories" />
      <main className="mx-auto flex max-w-[1120px] flex-col gap-5 px-6 pt-10 pb-16">
        <PageHeading title="지식" />
        <form role="search" className="flex flex-wrap items-end gap-3" onSubmit={(event) => event.preventDefault()}>
          <TextField
            type="search"
            label="검색어 (작업 이름·본문)"
            placeholder="예: 테이블 설계"
            className="flex-[999_1_320px]"
            value={filter.q}
            onChange={(event) => setFilter({ ...filter, q: event.target.value })}
          />
          <SelectField
            label="종류"
            className="flex-[1_1_140px]"
            value={filter.kind}
            onChange={(event) => setFilter({ ...filter, kind: event.target.value as MemoryKind | "" })}
          >
            <option value="">전체</option>
            {(Object.keys(MEMORY_KIND_LABEL) as MemoryKind[]).map((kind) => (
              <option key={kind} value={kind}>
                {MEMORY_KIND_LABEL[kind]}
              </option>
            ))}
          </SelectField>
          <SelectField
            label="페르소나"
            className="flex-[1_1_180px]"
            value={filter.personaId ?? ""}
            onChange={(event) =>
              setFilter({ ...filter, personaId: event.target.value ? Number(event.target.value) : null })
            }
          >
            <option value="">전체</option>
            {personas.map((persona) => (
              <option key={persona.persona_id} value={persona.persona_id}>
                {persona.name}
              </option>
            ))}
          </SelectField>
        </form>

        {failed && <Notice>불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요.</Notice>}
        {!failed && !result && <MemoriesSkeleton />}
        {result && (
          <>
            <p className="m-0 text-[13px] text-text-tertiary">{result.total}개 · 고친 시각 최근 것부터</p>
            {result.items.length === 0 ? (
              <EmptyState>조건에 맞는 지식이 없습니다.</EmptyState>
            ) : (
              <Table minWidth={760} caption="지식 목록">
                <thead>
                  <tr>
                    <TableHeaderCell className="w-12">#</TableHeaderCell>
                    <TableHeaderCell className="w-18">종류</TableHeaderCell>
                    <TableHeaderCell>작업 이름</TableHeaderCell>
                    <TableHeaderCell className="w-56">페르소나</TableHeaderCell>
                    <TableHeaderCell className="w-18">덧붙임</TableHeaderCell>
                    <TableHeaderCell className="w-24">근거 계획</TableHeaderCell>
                  </tr>
                </thead>
                <tbody>
                  {result.items.map((memory) => (
                    <MemoryTableRow key={memory.memory_id} memory={memory} personaNames={personaNames} />
                  ))}
                </tbody>
              </Table>
            )}
          </>
        )}
      </main>
    </div>
  );
}
