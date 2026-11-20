# personas 제작 계획

라우트: /personas
화면: Personas.dc.html
입력: docs/pages/personas/data.md, components.md, api.md
작성: 2026-11-20
상태: 제작 완료 (2026-11-20). 허가 (사용자 지시에 따라 스스로)

## 1. 충돌 검사

없음. 웹 쪽 만들기·고치기·지우기 호출 함수는 이번에 만들었다 (서버 API 는 이미 있다).

## 2. 구조

파일: src/app/personas/page.tsx, PersonasClient.tsx, PersonasSkeleton.tsx, loading.tsx

```
PersonasClient
├── layout/AppHeader current="personas"
├── ui/PageHeading "페르소나" + ui/Button "+ 새 페르소나"
├── persona/PersonaForm (만들기, creating 일 때)
├── ui/Table: 줄마다 이름 버튼(펼치기) + 펼친 줄 persona/PersonaDetail
│   └── PersonaDetail: 수정·삭제, 이름·설명 또는 PersonaForm, "이 페르소나의 지식 →", 거절 Notice
└── 설명 문구
```

상태: personas, failed, expandedId, creating, editing, busy, blocked({personaId, message})

| 동작 | 트리거 | 결과 | 부르는 것 |
|---|---|---|---|
| 읽기 | 진입, 쓰기 뒤 | 표 | fetchPersonas |
| 만들기 | 만들기 폼 | 새 페르소나를 펼친 채 다시 읽기 | createPersona |
| 고치기 | 수정 폼 | 보기로 돌아가 다시 읽기 | updatePersona |
| 지우기 | 삭제 | 성공은 접고 다시 읽기, 409 는 펼친 줄 안 Notice | deletePersona |
| 이 페르소나의 지식 | 링크 | /memories?persona_id={id} | 없음 |

## 3. 정하지 않은 UI 세부

| 항목 | 정한 값 | 이유 |
|---|---|---|
| 만들기 폼 위치 | 제목 아래, 표 위 | 가안에 없음 |
| 지우기 확인 창 | 두지 않는다 | 쓰이는 페르소나는 서버가 막고, 안 쓰이는 페르소나는 이름과 설명뿐이다 |
| 다른 줄 펼치기 | 수정 중·거절 알림을 닫는다 | 한 번에 한 줄만 |

## 4. 제작에 필요한 판단

- 만들기·고치기 오류(같은 이름 409, 빈 이름 400)는 토스트로 서버 문구

## 5. 와이어프레임

생략 (가안 아트보드로 대신, 만든 뒤 화면 대조).

## 6. 제작 기록 (2026-11-20)

- 만든 파일: 페이지 4개, components/persona 의 PersonaForm (+ 시험)·PersonaDetail, 페르소나 만들기·고치기·지우기 API 타입·mock·호출 함수 (+ 시험)
- 화면 대조 (ego-browser, 1440px, 실제 서버): build.png (펼친 줄과 지우기 거절), build-forms.png (만들기 폼과 수정 폼)
- 화면 대조에서 고친 것: 거절 알림에 서버 문구 대신 "Request failed with status code 409 …" 가 나왔다. 템플릿의 오류 처리가 ky 가 이미 읽은 본문을 다시 읽으려 해 늘 실패했다 (lib/api/client.ts 두 곳, app/api/proxy/route.ts 한 곳) → error.data 를 읽게 고쳤다. 다른 화면의 서버 오류 문구(지식 수정 400 등)도 이제 그대로 나온다
- 확인: dankim-persona 삭제 → "지울 수 없습니다. 지식 7개, 계획 1개가 이 페르소나를 씁니다" (실제 서버, 데이터 변화 없음)
- 실제 만들기·고치기·지우기 성공 경로는 실제 서버 데이터를 바꾸므로 누르지 않았다. mock 시험으로 확인했다
