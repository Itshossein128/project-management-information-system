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

## Project-scoped ViewSets

Most domain CRUD APIs inherit from `common.viewsets.ProjectScopedViewSet`:

- **Tenancy:** `get_queryset()` filters by `project_id` from URL kwarg `project_pk`.
- **Permissions:** `view_permission` / `edit_permission` class attrs; `HasProjectPermission` reads `required_permission`.
- **Audit:** `perform_create` / `perform_update` set `created_by` / `updated_by`.
- **Soft delete:** `destroy()` sets `is_deleted=True` instead of hard delete.

Scoped subclasses set permission names and optionally override `post_save` / `post_delete` hooks (e.g. cache invalidation in `cost_control.views.CostScopedViewSet`, `contracts.views.ContractScopedViewSet`).

Business logic belongs in `services.py`; viewsets should delegate to services for multi-step workflows (see `field_reports/services/` for daily report approval and offline sync).

## File upload validation

Shared validators live in `common/validators.py`:

| Helper | Allowed | Used by |
|--------|---------|---------|
| `validate_document_upload` | pdf, doc(x), xls(x), jpg, png, zip (50 MB max) | Documents, correspondence |
| `validate_msp_upload` | `.xml` | Schedule MSP import |
| `validate_p6_upload` | `.xer` | Schedule P6 import |
| `validate_xlsx_upload` | `.xlsx` | Excel imports |

Upload paths also reject path traversal in filenames (`..`, `/`, `\`); S3 keys use a generated UUID basename (`documents/services/upload_service.py`).

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
- Per-app endpoint notes: `core/*/ENDPOINTS.md` (including `field_reports/`, `schedule/`, `cost_control/`)
