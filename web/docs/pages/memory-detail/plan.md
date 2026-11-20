# memory-detail 제작 계획

라우트: /memories/[id]
화면: MemoryDetail.dc.html
입력: docs/pages/memory-detail/data.md, components.md, api.md
작성: 2026-11-20
상태: 제작 완료 (2026-11-20). 허가 (사용자 지시에 따라 스스로)

## 1. 충돌 검사

없음. 웹 쪽 조회·고치기·지우기 호출 함수는 이번에 만들었다 (서버 API 는 이미 있다).

## 2. 구조

파일: src/app/memories/[id]/page.tsx (generateMetadata "지식 #n {작업 이름}"), MemoryDetailClient.tsx, MemoryDetailSkeleton.tsx, loading.tsx

```
MemoryDetailClient
├── layout/AppHeader current="memories"
├── ui/TextLink "← 지식 목록"
├── 머리: 번호, 작업 이름, 종류·페르소나·덧붙임 수, ui/Button 수정·삭제
├── 지우기 확인: ui/Notice + ui/Button 취소·지우기   (mode = confirming)
├── memory/MemoryEditForm                          (mode = editing)
├── 본문: memory/MemoryBody (ui/MarkdownText, ui/LabeledDivider)
└── 근거: memory/MemorySourceList
```

상태: memory, personas, planIds, error("not_found" | "failed" | null), mode("view" | "editing" | "confirming"), busy

| 동작 | 트리거 | 결과 | 부르는 것 |
|---|---|---|---|
| 읽기 | 진입 | 지식, 페르소나 이름, 근거 계획이 서버에 있는지 | fetchMemory, fetchPersonas, fetchPlans |
| 저장 | 수정 폼 [저장] | 다시 읽고 보기로 돌아감. 실패는 토스트 | updateMemory, fetchMemory |
| 지우기 | 확인 [지우기] | /memories 로 이동 | deleteMemory |

## 3. 정하지 않은 UI 세부

| 항목 | 정한 값 | 이유 |
|---|---|---|
| 본문 폭 | 880px | 긴 글을 읽는 화면 |
| 수정 폼 위치 | 머리 아래, 본문 위 (본문은 그대로 보인다) | 가안 |
| 서버에 없는 근거 계획 | 링크 대신 "계획 3 (서버에 없음)" | tpm-trial 만 옮겨 계획 3 이 없다 |
| 덧붙임 수 | 본문의 덧붙임 머리 수 | 조회 응답에는 appended_count 가 없다 |

## 4. 제작에 필요한 판단

- 웹은 근거를 고치지 않는다 (CLI 의 덧붙이기만 바꾼다)
- 서버 오류 메시지(빈 이름 400, 없는 페르소나 400)는 토스트로 그대로 보인다

## 5. 와이어프레임

생략 (가안 아트보드로 대신, 만든 뒤 화면 대조).

## 6. 제작 기록 (2026-11-20)

- 만든 파일: 페이지 4개, components/memory 의 MemoryBody·MemorySourceList·MemoryEditForm (+ 시험), lib/memory-body.ts (+ 시험), 조회·고치기·지우기 API 타입·mock·호출 함수 (+ 시험)
- 화면 대조 (ego-browser, 1440px, 실제 서버): build.png (보기), build-edit.png (수정 폼), build-delete.png (지우기 확인)
- 화면 대조에서 고친 것: 코드 블록의 줄마다 인라인 코드 회색 바탕이 깔렸다 → MarkdownText 의 pre 안 code 는 바탕 없음
- 확인: 수정 폼 열고 닫기, 지우기 확인 열고 취소, 없는 지식(/memories/999) 안내와 제목 "지식 #999"
- 실제 저장·지우기는 실제 서버 데이터를 바꾸므로 브라우저에서 누르지 않았다. mock 시험으로 확인했다 (고치면 목록 맨 앞에 edited, 지우면 404, 빈 이름 400)
