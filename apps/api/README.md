# IPCAS API (`apps/api`)

Django 4.2 + Django REST Framework backend for the IPCAS construction management platform.

## Layout

```
apps/api/
├── core/                    # Django project root (manage.py lives here)
│   ├── config/              # Settings, root URLs, Celery
│   ├── authentication/      # JWT auth, users, password reset
│   ├── projects/            # Projects, tenancy middleware, nested routes
│   ├── master_data/         # Roles, permissions, project members/positions
│   ├── business_meta/       # Dynamic tables, fields, rows, Excel IO
│   ├── permissions/         # Project-scoped permission classes
│   ├── audit/               # Write audit log (sync or async)
│   ├── storage/             # MinIO presigned URLs
│   ├── events/              # RabbitMQ event publisher + worker
│   ├── inventory/           # Legacy items + department activity logs
│   ├── resources/           # Materials ledger (blueprint inventory)
│   ├── wbs/, schedule/, field_reports/, cost_control/, contracts/, …
│   └── manage.py
├── requirements.txt
└── README.md
```

## Requirements

- PostgreSQL (`DATABASE_URL`) — no SQLite fallback
- Redis (cache + rate limiting)
- Optional Docker stack: Traefik (`:8080`), MinIO, RabbitMQ, Celery worker

From monorepo root:

```bash
pnpm db:migrate
pnpm db:seed          # dev users, sample projects (password: devpass123)
pnpm dev:api          # http://localhost:8000
```

## Key endpoints

| Area | Path |
|------|------|
| Auth | `/api/auth/login/`, `logout/`, `token/refresh/`, `forgot-password/` |
| Projects | `/api/v1/projects/` |
| Dynamic tables | `/api/v1/projects/{uuid}/tables/...` |
| API docs | `/api/docs/`, `/api/schema/` |
| Schema verify | `python manage.py verify_blueprint_schema` |

## Tests

```bash
cd apps/api/core
../.venv/bin/python -m pytest
# or: ../.venv/bin/python manage.py test <app>
```

Integration tests (`*_integration.py`) need RabbitMQ + MinIO (Docker).

## References

- Blueprint: `docs/IPCAS_Engineering_Blueprint.md`
- Implementation status: `docs/ipcas-scope-map.md`
- Per-app endpoint notes: `core/*/ENDPOINTS.md`
