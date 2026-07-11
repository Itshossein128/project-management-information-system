FROM node:20-alpine AS development-dependencies-env
WORKDIR /app
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml .npmrc ./
COPY apps/web/package.json ./apps/web/
RUN corepack enable && corepack prepare pnpm@9 --activate \
  && pnpm install --frozen-lockfile --filter web

FROM node:20-alpine AS production-dependencies-env
WORKDIR /app
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml .npmrc ./
COPY apps/web/package.json ./apps/web/
RUN corepack enable && corepack prepare pnpm@9 --activate \
  && pnpm install --frozen-lockfile --prod --filter web

FROM node:20-alpine AS build-env
WORKDIR /app
ARG VITE_API_BASE_URL=http://localhost:8000/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml .npmrc ./
COPY apps/web ./apps/web
COPY --from=development-dependencies-env /app/node_modules ./node_modules
COPY --from=development-dependencies-env /app/apps/web/node_modules ./apps/web/node_modules
RUN corepack enable && corepack prepare pnpm@9 --activate \
  && pnpm --filter web run build

FROM node:20-alpine
WORKDIR /app
COPY pnpm-workspace.yaml package.json pnpm-lock.yaml .npmrc ./
COPY apps/web/package.json ./apps/web/
COPY --from=production-dependencies-env /app/node_modules ./node_modules
COPY --from=production-dependencies-env /app/apps/web/node_modules ./apps/web/node_modules
COPY --from=build-env /app/apps/web/build ./apps/web/build
RUN corepack enable && corepack prepare pnpm@9 --activate
WORKDIR /app/apps/web
EXPOSE 3000
CMD ["pnpm", "run", "start"]
