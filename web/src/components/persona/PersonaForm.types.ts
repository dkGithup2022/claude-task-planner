/** 페르소나 만들기·수정 폼의 입력값 */
export interface PersonaFormValues {
  name: string;
  description: string;
}

export interface PersonaFormProps {
  /** 수정이면 지금 값. 없으면 빈 폼 (만들기) */
  initial?: PersonaFormValues;
  submitLabel: string;
  saving: boolean;
  onSubmit: (values: PersonaFormValues) => void;
  onCancel: () => void;
}
