# 웹 이미지. next build 의 standalone 결과만 담는다 (output: "standalone").
FROM node:24-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:24-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
# mock 여부는 브라우저 번들에 들어가므로 빌드할 때 정한다. 배포는 실제 서버를 쓴다
ENV NEXT_PUBLIC_USE_MOCK=false \
    NEXT_TELEMETRY_DISABLED=1
RUN npm run build

FROM node:24-alpine AS run
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
USER node
EXPOSE 3000
# BACKEND_API_URL 은 실행할 때 받는다 (프록시가 서버에서 읽는다)
CMD ["node", "server.js"]
