@AGENTS.md

# 프로젝트 규칙

이 레포는 Next.js 프론트엔드의 출발점이다. 아래 관례를 따라 파일을 추가한다.

## 구조

```
src/
├── app/                # 라우트. page.tsx(서버, metadata) + *Client.tsx("use client", 본문)
│   └── api/proxy/      # 백엔드 프록시. 엔드포인트별 route.ts 를 만들지 않는다
├── components/
│   ├── ui/             # 도메인 무관 범용 (Button, Modal, Chip)
│   ├── layout/         # Header, Footer
│   └── {domain}/       # 특정 도메인 전용
├── lib/
│   ├── api/client.ts   # apiGet/apiPost/apiPut/apiPatch/apiDelete. 백엔드 호출은 전부 여기로
│   ├── api/mock/handlers.ts  # mock 응답 등록
│   ├── {domain}-data.ts      # mock 데이터와 조회 함수
│   └── utils.ts        # cn, formatRelativeDate
├── types/
│   ├── api/            # 백엔드 요청/응답 계약. 백엔드 필드명 그대로
│   └── data/           # 화면이 쓰는 형태. api 타입에서 변환해 만든다
├── store/              # zustand. {domain}-store.ts
├── hooks/
├── styles/             # 별도 CSS 시트 (마크다운 등)
└── test/               # vitest setup, next/navigation mock
```

## 페이지

- `page.tsx` 는 서버 컴포넌트. `metadata` 를 내보내고 `<Suspense>` 로 `*Client.tsx` 를 감싼다.
- 상태, 이벤트, 브라우저 API 는 `*Client.tsx` 에만 둔다.
- 페이지마다 `loading.tsx` 를 같이 만든다. 본문과 같은 `max-w` 로 스켈레톤을 그린다.
- 동적 라우트는 `generateMetadata` 로 제목/설명을 채운다.

## API

- 백엔드 호출은 `@/lib/api/client` 의 `apiGet` 계열만 쓴다. `fetch` 직접 호출 금지.
- 새 API 추가 순서: `types/api/{domain}.ts` 에 요청/응답 타입 → `lib/api/mock/handlers.ts` 에 mock 항목 → 화면에서 호출.
- 실패는 `ApiError` 로 온다. 사용자에게 알릴 때는 `showErrorToast(err, "대체 문구")`.
- 정적 생성되는 공개 API 는 `{ skipAuth: true }` 를 넘긴다.
- `NEXT_PUBLIC_USE_MOCK=true` 면 백엔드 없이 handlers.ts 로 응답한다.

## 스타일

- 색은 `globals.css` 의 토큰(`var(--bg-primary)` 등) 또는 `@theme` 별칭(`bg-surface`, `text-text-secondary`)만 쓴다. 색상 코드 직접 입력 금지.
- 클래스 조합은 `cn()`.
- 모바일 우선. `sm:` 이상에서 데스크톱 레이아웃.

## 상태

- 페이지 안에서 끝나는 상태는 `useState`.
- 여러 페이지가 공유하거나 새로고침 후에도 남아야 하면 `store/{domain}-store.ts` 에 zustand. persist 를 쓰면 읽기 전에 하이드레이션을 기다린다.

## 테스트

- 테스트 파일은 소스 옆에 `{name}.test.ts(x)`.
- `npm run test:run` 으로 실행. 라우터가 필요하면 `import "@/test/mocks/next-navigation"`.

## 검증

작업을 마치면 `npm run typecheck && npm run lint && npm run test:run` 을 통과시킨다.
