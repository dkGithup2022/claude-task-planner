"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { TextAreaField } from "@/components/ui/TextAreaField";
import { TextField } from "@/components/ui/TextField";
import type { PersonaFormProps, PersonaFormValues } from "./PersonaForm.types";

/** 페르소나 이름과 설명 폼. 만들기와 수정이 같이 쓴다 */
export function PersonaForm({ initial, submitLabel, saving, onSubmit, onCancel }: PersonaFormProps) {
  const [values, setValues] = useState<PersonaFormValues>(initial ?? { name: "", description: "" });
  return (
    <form
      aria-label={initial ? "페르소나 수정" : "새 페르소나"}
      className="flex flex-col gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit({ name: values.name.trim(), description: values.description });
      }}
    >
      <TextField
        label="이름"
        required
        maxLength={255}
        placeholder="예: fe-developer"
        value={values.name}
        onChange={(event) => setValues({ ...values, name: event.target.value })}
      />
      <TextAreaField
        label="설명"
        rows={3}
        value={values.description}
        onChange={(event) => setValues({ ...values, description: event.target.value })}
      />
      <div className="flex justify-end gap-2">
        <Button variant="subtle" onClick={onCancel} disabled={saving}>
          취소
        </Button>
        <Button variant="primary" type="submit" disabled={saving || !values.name.trim()}>
          {saving ? "저장 중" : submitLabel}
        </Button>
      </div>
    </form>
  );
}
