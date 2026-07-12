# AGENTS.md

## Cursor Cloud specific instructions

Monorepo (pnpm workspace): `apps/web` (React Router 7 + Vite frontend) and `apps/api` (Django 4.2 + DRF backend). Standard commands live in the root `README.md` / `package.json` scripts; this section only covers non-obvious cloud caveats. The update script already runs `pnpm install`, creates the API venv at `apps/api/.venv`, installs `requirements.txt`, and creates `.env` from `.env.example`.

### Services

| Service | Dev command (from repo root) | Port | Notes |
|---------|------------------------------|------|-------|
| PostgreSQL | `sudo pg_ctlcluster 16 main start` | 5433 | Required; no SQLite fallback. Must be started manually each session (systemd is not managing it). |
| Django API | `pnpm dev:api` | 8000 | Reads root `.env`; requires `DATABASE_URL` and the venv at `apps/api/.venv`. Docs at `/api/docs/`, schema at `/api/schema/`. |
| Web frontend | `pnpm dev:web` | 5173 | Or run both with `pnpm dev`. |

### Startup gotchas

- **Postgres is not auto-started.** After a fresh VM boot run `sudo pg_ctlcluster 16 main start` before the API. It is configured on port **5433** (not the default 5432) to match `.env.example`. The `ipcas`/`ipcas` role and `ipcas` database already exist in the cluster data dir.
- **npm registry:** the committed `.npmrc` points at the Liara mirror (`package-mirror.liara.ir`), which is unreachable from the cloud VM. Always install JS deps with `pnpm install --registry https://registry.npmjs.org/` (the update script already does this).
- **First-time DB setup only:** after starting Postgres on a brand-new database, run `pnpm db:migrate` then `pnpm db:seed`. Seeding creates dev login users (password `devpass123`), e.g. admin phone `+10000000001`. These persist in the DB volume, so re-seeding is not needed on later boots.

### Checks / tests

- Typecheck: `pnpm typecheck` (runs `react-router typegen && tsc`). No ESLint/Biome config is present despite rules mentioning Biome.
- E2E: `cd apps/web && pnpm exec playwright test`. Playwright's `webServer` config auto-starts web + API (reuses running servers) but still needs Postgres up first. Browsers install via `pnpm exec playwright install --with-deps chromium` (cached in the snapshot; not part of the update script). The `auth.spec.ts` login test depends on the seeded `+10000000001` / `devpass123` user.
- No Python/Django test suite exists yet.
