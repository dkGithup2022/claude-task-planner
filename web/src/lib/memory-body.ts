/** CLI 가 덧붙일 때 다는 머리. "****** KNOWLEDGE APPENDED 2 ********" */
const APPENDED_HEADER = /^\*{6} KNOWLEDGE APPENDED (\d+) \*{8}$/m;

export interface MemoryBodyParts {
  base: string;
  appended: { number: number; text: string }[];
}

/** 지식 본문을 처음 본문과 덧붙인 조각으로 나눈다. 서버는 본문을 고치지 않으므로 화면에서만 나눈다 */
export function splitMemoryBody(body: string): MemoryBodyParts {
  const pieces = body.split(new RegExp(APPENDED_HEADER.source, "m"));
  const appended: MemoryBodyParts["appended"] = [];
  for (let i = 1; i < pieces.length; i += 2) {
    appended.push({ number: Number(pieces[i]), text: pieces[i + 1].trim() });
  }
  return { base: pieces[0].trim(), appended };
}
