FROM node:20-alpine AS development-dependencies-env
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate \
  && pnpm install --frozen-lockfile

FROM node:20-alpine AS production-dependencies-env
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && corepack prepare pnpm@latest --activate \
  && pnpm install --frozen-lockfile --prod

FROM node:20-alpine AS build-env
WORKDIR /app
ARG VITE_API_BASE_URL=http://localhost:8000/api
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
COPY . .
COPY --from=development-dependencies-env /app/node_modules ./node_modules
RUN corepack enable && corepack prepare pnpm@latest --activate \
  && pnpm run build

FROM node:20-alpine
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
COPY --from=production-dependencies-env /app/node_modules ./node_modules
COPY --from=build-env /app/build ./build
RUN corepack enable && corepack prepare pnpm@latest --activate
EXPOSE 3000
CMD ["pnpm", "run", "start"]
