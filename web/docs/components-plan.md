# 공용 컴포넌트 작업 목록 (fe-apply-components, 2026-11-20)

입력: `docs/design-export/*.dc.html` (UI 가안 아티팩트 6화면). 컴포넌트 시트가 따로 없어 화면들에서 두 번 이상 반복되는 UI 를 뽑았다. 사용자 지시("순차적으로 자유롭게 진행, API 데이터 관련만 질문")에 따라 확인 없이 진행하고 판단을 여기에 적는다.

가안 공통: 둥글기 없음(직각), 그림자 없음, 글자 12·13·14px, 제목 20·22·24px, 버튼 높이 36~40px, 입력칸 44px.

## 만드는 것

| 컴포넌트 | 위치 | 변형 · props | 쓰이는 곳 (가안) |
|---|---|---|---|
| Button | ui | variant primary(검정 칠) · outline(검정 테두리) · subtle(회색 테두리), size sm(36px) · md(40px), 나머지는 button 속성 | 명령서 보기, 수정·삭제·저장·취소, + 새 페르소나 |
| TextLink | ui | href, tone default · secondary | "전체 보기 →", "← 지식 목록", 근거의 "계획 11 →" |
| PageHeading | ui | title, meta?(ReactNode), actions?(ReactNode) | 계획·지식·페르소나 화면 제목 줄 |
| SectionHeader | ui | title, action?(ReactNode) | 메인의 구역 제목과 "전체 보기 →", 패널 소제목 |
| EmptyState | ui | children | "실행 중인 계획이 없습니다" |
| Notice | ui | children. role="alert", 굵은 테두리 | 페르소나 지우기 거절, 지식 지우기 확인 |
| LabeledDivider | ui | label | 지식 본문의 "덧붙임 n" 구분선 |
| TextField | ui | label, 나머지는 input 속성 | 지식 검색어, 지식 수정의 작업 이름 |
| SelectField | ui | label, children(option), 나머지는 select 속성 | 종류·페르소나 필터, 지식 수정의 종류 |
| TextAreaField | ui | label, 나머지는 textarea 속성. 글꼴 mono | 지식 본문 수정 |
| Checkbox | ui | label, 나머지는 input 속성 | 지식 수정의 페르소나 고르기 |
| Table | ui | children, minWidth?(px, 넘치면 가로 스크롤) | 계획 목록, 지식 목록, 페르소나 목록 |
| TableHeaderCell | ui | children, 나머지는 th 속성(width 는 className) | 표 머리 |
| TableRow | ui | selected?, 나머지는 tr 속성 | 표의 줄 (페르소나 펼친 줄은 selected) |
| TableCell | ui | tone default · secondary · tertiary, 나머지는 td 속성 | 표의 칸 (번호·시각은 tertiary) |
| AppHeader | layout | current?: "plans" · "memories" · "personas" | 모든 화면 위 메뉴 |
| NodeStatusMark | plan | status: todo · running · done · failed · skipped | 그래프 노드, 노드 패널, 앞뒤 노드 |
| PlanStatusMark | plan | status: drafting · reviewing · approved · rejected · running · done | 메인, 계획 목록, 그래프 위쪽 |

인터랙션: 모두 콜백 prop 이나 HTML 속성으로 받는다 (쓰는 곳마다 동작이 다르다). 동작이 하나로 정해진 컴포넌트는 없다. AppHeader 와 두 StatusMark 는 표시만 한다.

상태 기호 (웹 UI 문서 1번 화면): ● 완료, ◐ 실행 중, ○ 할 일, ✕ 실패, – 건너뜀. 계획 상태는 ● 끝남(완료), ◐ 실행 중, ○ 만드는 중·검토 중·승인, – 불허. 색은 쓰지 않는다 (흑백 회색만).

## 공용으로 두지 않는 것 (페이지 단계에서)

- 그래프 노드 상자: React Flow 의 노드로 그래프 화면에서 만든다 (그 화면만 쓴다)
- 노드 패널, 계획 요약 줄, 지식 본문: 한 화면만 쓴다
- 지식 지우기 확인 줄, 페르소나 펼친 상세: 한 화면만 쓴다. Notice · Button 을 조립한다
