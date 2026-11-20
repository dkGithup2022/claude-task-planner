# task-plan-web

task-plan-manager 의 웹. `nextjs-fe-base` 템플릿(커밋 60e48bc)에서 시작했다. 서버는 `../be` (http://localhost:8000, 경로는 /api 로 시작). 웹은 http://localhost:3000.

## 시작

```bash
cp .env.local.example .env.local
npm install
npm run dev
```

`NEXT_PUBLIC_USE_MOCK=true` 상태에서는 백엔드 없이 동작한다.

## 명령

| 명령 | 역할 |
|---|---|
| `npm run dev` | 개발 서버 |
| `npm run build` | 프로덕션 빌드 |
| `npm run typecheck` | 타입 검사 |
| `npm run lint` | ESLint |
| `npm run test` / `test:run` | vitest |

## 포함된 것

- 백엔드 프록시 (`src/app/api/proxy`) 와 클라이언트 (`src/lib/api/client.ts`)
- mock 응답 등록 지점 (`src/lib/api/mock/handlers.ts`)
- 환경변수 스키마 (`src/env.mjs`)
- 디자인 토큰 뼈대 (`src/app/globals.css`)
- 서버 page + Client 분리 예시 (`src/app/page.tsx`, `HomeClient.tsx`)
- vitest + Testing Library

## 포함되지 않은 것

인증, 배포 설정(Docker, k8s), 마크다운 렌더링, 분석 도구. 프로젝트별로 추가한다.

관례는 `CLAUDE.md` 에 있다.
