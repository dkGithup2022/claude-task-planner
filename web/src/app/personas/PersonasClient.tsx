"use client";

import { Fragment, useEffect, useState } from "react";
import { AppHeader } from "@/components/layout/AppHeader";
import { PersonaDetail } from "@/components/persona/PersonaDetail";
import { PersonaForm } from "@/components/persona/PersonaForm";
import type { PersonaFormValues } from "@/components/persona/PersonaForm.types";
import { Button } from "@/components/ui/Button";
import { EmptyState } from "@/components/ui/EmptyState";
import { Notice } from "@/components/ui/Notice";
import { PageHeading } from "@/components/ui/PageHeading";
import { Table } from "@/components/ui/Table";
import { TableCell } from "@/components/ui/TableCell";
import { TableHeaderCell } from "@/components/ui/TableHeaderCell";
import { TableRow } from "@/components/ui/TableRow";
import { showErrorToast } from "@/lib/api/error-toast";
import { ApiError } from "@/lib/api/types";
import { createPersona, deletePersona, fetchPersonas, updatePersona } from "@/lib/persona-api";
import type { Persona } from "@/types/data/domain/persona";
import { PersonasSkeleton } from "./PersonasSkeleton";

export function PersonasClient() {
  const [personas, setPersonas] = useState<Persona[] | null>(null);
  const [failed, setFailed] = useState(false);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [creating, setCreating] = useState(false);
  const [editing, setEditing] = useState(false);
  const [busy, setBusy] = useState(false);
  const [blocked, setBlocked] = useState<{ personaId: number; message: string } | null>(null);

  const reload = () =>
    fetchPersonas()
      .then((res) => {
        setPersonas(res.personas);
        setFailed(false);
      })
      .catch((err) => {
        setFailed(true);
        showErrorToast(err, "페르소나를 불러오지 못했습니다");
      });

  useEffect(() => {
    reload();
  }, []);

  const toggle = (personaId: number) => {
    setExpandedId(expandedId === personaId ? null : personaId);
    setEditing(false);
    setBlocked(null);
  };

  const create = (values: PersonaFormValues) => {
    setBusy(true);
    createPersona(values)
      .then(({ persona_id }) => {
        setCreating(false);
        setExpandedId(persona_id);
        return reload();
      })
      .catch((err) => showErrorToast(err, "만들지 못했습니다"))
      .finally(() => setBusy(false));
  };

  const save = (personaId: number, values: PersonaFormValues) => {
    setBusy(true);
    updatePersona(personaId, values)
      .then(() => {
        setEditing(false);
        return reload();
      })
      .catch((err) => showErrorToast(err, "저장하지 못했습니다"))
      .finally(() => setBusy(false));
  };

  const remove = (personaId: number) => {
    setBusy(true);
    setBlocked(null);
    deletePersona(personaId)
      .then(() => {
        setExpandedId(null);
        return reload();
      })
      .catch((err) => {
        if (err instanceof ApiError && err.status === 409) {
          setBlocked({ personaId, message: err.message });
          return;
        }
        showErrorToast(err, "지우지 못했습니다");
      })
      .finally(() => setBusy(false));
  };

  return (
    <div>
      <AppHeader current="personas" />
      <main className="mx-auto flex max-w-[1120px] flex-col gap-5 px-6 pt-10 pb-16">
        <PageHeading
          title="페르소나"
          actions={
            <Button variant="primary" onClick={() => setCreating(true)} disabled={creating}>
              + 새 페르소나
            </Button>
          }
        />
        {creating && (
          <div className="bg-secondary-bg p-5">
            <PersonaForm submitLabel="만들기" saving={busy} onSubmit={create} onCancel={() => setCreating(false)} />
          </div>
        )}
        {failed && <Notice>불러오지 못했습니다. 서버가 켜져 있는지 확인해 주세요.</Notice>}
        {!failed && !personas && <PersonasSkeleton />}
        {personas && personas.length === 0 && <EmptyState>페르소나가 없습니다.</EmptyState>}
        {personas && personas.length > 0 && (
          <Table minWidth={720} caption="페르소나 목록">
            <thead>
              <tr>
                <TableHeaderCell className="w-12">#</TableHeaderCell>
                <TableHeaderCell className="w-60">이름</TableHeaderCell>
                <TableHeaderCell>설명</TableHeaderCell>
                <TableHeaderCell className="w-20">지식 수</TableHeaderCell>
                <TableHeaderCell className="w-20">계획 수</TableHeaderCell>
              </tr>
            </thead>
            <tbody>
              {personas.map((persona) => {
                const expanded = expandedId === persona.persona_id;
                return (
                  <Fragment key={persona.persona_id}>
                    <TableRow selected={expanded}>
                      <TableCell tone="tertiary">{persona.persona_id}</TableCell>
                      <TableCell>
                        <button
                          type="button"
                          aria-expanded={expanded}
                          onClick={() => toggle(persona.persona_id)}
                          className="cursor-pointer text-left font-medium hover:underline"
                        >
                          {persona.name} {expanded ? "▴" : "▾"}
                        </button>
                      </TableCell>
                      <TableCell tone="secondary">{persona.description}</TableCell>
                      <TableCell>{persona.memory_count}</TableCell>
                      <TableCell>{persona.plan_count}</TableCell>
                    </TableRow>
                    {expanded && (
                      <TableRow selected>
                        <TableCell colSpan={5}>
                          <PersonaDetail
                            persona={persona}
                            editing={editing}
                            busy={busy}
                            blockedMessage={blocked?.personaId === persona.persona_id ? blocked.message : null}
                            onEdit={() => setEditing(true)}
                            onCancelEdit={() => setEditing(false)}
                            onSave={(values) => save(persona.persona_id, values)}
                            onDelete={() => remove(persona.persona_id)}
                          />
                        </TableCell>
                      </TableRow>
                    )}
                  </Fragment>
                );
              })}
            </tbody>
          </Table>
        )}
        <p className="m-0 text-[12px] text-text-tertiary">
          계획 수는 참여 페르소나이거나 노드 담당인 계획을 센다. 이름은 페르소나마다 다르다.
        </p>
      </main>
    </div>
  );
}
