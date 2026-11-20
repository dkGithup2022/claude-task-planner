import { Button } from "@/components/ui/Button";
import { Notice } from "@/components/ui/Notice";
import { TextLink } from "@/components/ui/TextLink";
import { PersonaForm } from "./PersonaForm";
import type { PersonaDetailProps } from "./PersonaDetail.types";

/** 펼친 페르소나 줄의 상세: 수정·삭제, 이름·설명 (또는 수정 폼), 이 페르소나의 지식, 지우기 거절 알림 */
export function PersonaDetail({
  persona,
  editing,
  busy,
  blockedMessage,
  onEdit,
  onCancelEdit,
  onSave,
  onDelete,
}: PersonaDetailProps) {
  return (
    <div className="flex flex-col gap-4 px-1 py-2">
      <div className="flex items-center gap-2">
        <span className="grow text-[12px] text-text-tertiary">페르소나 {persona.persona_id}</span>
        {!editing && (
          <Button size="sm" variant="primary" onClick={onEdit} disabled={busy}>
            수정
          </Button>
        )}
        <Button size="sm" onClick={onDelete} disabled={busy}>
          삭제
        </Button>
      </div>
      {editing ? (
        <PersonaForm
          initial={{ name: persona.name, description: persona.description }}
          submitLabel="저장"
          saving={busy}
          onSubmit={onSave}
          onCancel={onCancelEdit}
        />
      ) : (
        <dl className="m-0 grid grid-cols-[64px_1fr] gap-y-1.5">
          <dt className="text-text-secondary">이름</dt>
          <dd className="m-0">{persona.name}</dd>
          <dt className="text-text-secondary">설명</dt>
          <dd className="m-0 whitespace-pre-wrap">{persona.description || <span className="text-text-tertiary">없음</span>}</dd>
        </dl>
      )}
      <TextLink href={`/memories?persona_id=${persona.persona_id}`}>이 페르소나의 지식 →</TextLink>
      {blockedMessage && <Notice>지울 수 없습니다. {blockedMessage}</Notice>}
    </div>
  );
}
