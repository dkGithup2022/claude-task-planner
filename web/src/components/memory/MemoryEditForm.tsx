"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Checkbox } from "@/components/ui/Checkbox";
import { SelectField } from "@/components/ui/SelectField";
import { TextAreaField } from "@/components/ui/TextAreaField";
import { TextField } from "@/components/ui/TextField";
import { MEMORY_KIND_LABEL, type MemoryKind } from "@/types/data/domain/memory";
import type { MemoryEditFormProps, MemoryEditValues } from "./MemoryEditForm.types";

/** 지식 수정 폼: 작업 이름, 종류, 페르소나, 본문 (웹 UI 문서 3번 화면, 사용자 결정 "b") */
export function MemoryEditForm({ memory, personas, saving, onSave, onCancel }: MemoryEditFormProps) {
  const [values, setValues] = useState<MemoryEditValues>({
    theme: memory.theme,
    kind: memory.kind,
    personaIds: memory.persona_ids,
    body: memory.body,
  });
  const togglePersona = (personaId: number) =>
    setValues((current) => ({
      ...current,
      personaIds: current.personaIds.includes(personaId)
        ? current.personaIds.filter((id) => id !== personaId)
        : [...current.personaIds, personaId],
    }));

  return (
    <form
      aria-label="지식 수정"
      className="flex flex-col gap-4 bg-secondary-bg p-5"
      onSubmit={(event) => {
        event.preventDefault();
        onSave(values);
      }}
    >
      <div className="flex flex-wrap gap-3">
        <TextField
          label="작업 이름"
          required
          className="flex-[999_1_280px]"
          value={values.theme}
          onChange={(event) => setValues({ ...values, theme: event.target.value })}
        />
        <SelectField
          label="종류"
          className="flex-[1_1_140px]"
          value={values.kind}
          onChange={(event) => setValues({ ...values, kind: event.target.value as MemoryKind })}
        >
          {(Object.keys(MEMORY_KIND_LABEL) as MemoryKind[]).map((kind) => (
            <option key={kind} value={kind}>
              {MEMORY_KIND_LABEL[kind]}
            </option>
          ))}
        </SelectField>
      </div>
      <fieldset className="m-0 flex flex-wrap gap-4 border-0 p-0">
        <legend className="mb-1 text-[12px] text-text-secondary">페르소나</legend>
        {personas.map((persona) => (
          <Checkbox
            key={persona.persona_id}
            label={persona.name}
            checked={values.personaIds.includes(persona.persona_id)}
            onChange={() => togglePersona(persona.persona_id)}
          />
        ))}
      </fieldset>
      <TextAreaField
        label="본문 (덧붙임 머리는 그대로 둔다)"
        required
        rows={12}
        value={values.body}
        onChange={(event) => setValues({ ...values, body: event.target.value })}
      />
      <div className="flex justify-end gap-2">
        <Button variant="subtle" onClick={onCancel} disabled={saving}>
          취소
        </Button>
        <Button variant="primary" type="submit" disabled={saving}>
          {saving ? "저장 중" : "저장"}
        </Button>
      </div>
    </form>
  );
}
