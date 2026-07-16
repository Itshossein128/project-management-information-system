# Local Development

## Full local (Docker available)

```bash
pnpm install
pnpm db:up          # Postgres + Redis via docker compose
pnpm db:migrate
pnpm db:seed        # admin phone +10000000001 / password devpass123
pnpm dev            # starts API + web helpers
```

Or full stack: `docker compose up --build` (Traefik `:8080`, MinIO, RabbitMQ, worker).

## Cloud / Docker-less (see `AGENTS.md`)

| Service | Command | Port |
| --- | --- | --- |
| PostgreSQL | `sudo pg_ctlcluster 16 main start` | 5433 |
| Redis | `sudo redis-server /etc/redis/redis.conf --daemonize yes` | 6379 |
| API | `pnpm dev:api` | 8000 |
| Web | `pnpm dev:web` | 5173 |

Set in `.env`: `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`.

## Useful URLs

- API docs: `http://localhost:8000/api/docs/`
- Schema: `http://localhost:8000/api/schema/`
- Web: `http://localhost:5173`

## Checks

- `pnpm typecheck`
- `cd apps/api/core && ../.venv/bin/python manage.py test …`
- `pnpm e2e` (Postgres + Redis must be up)
