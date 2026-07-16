# Architecture Overview

## Monorepo layout

```text
apps/web/     React Router 7 + Vite frontend
apps/api/     Django 4.2 + DRF (IPCAS API)
docs/         Blueprint + scope map
infra/        Traefik / gateway config
.github/      Actions, Agents, issue/PR templates
```

## Mental model

```text
Browser (apps/web)
    → JWT
Django API (/api/v1/...)
    → PostgreSQL (required)
    → Redis (cache / rate limits)
    → MinIO (files, optional in local-dev)
    → RabbitMQ (audit/events when async enabled)
```

## Where to change what

| Need | Start here |
| --- | --- |
| New page / route | `apps/web/src/app/routes/` + `routeVars.ts` / nav config |
| New API endpoint | `apps/api/core/<app>/views.py` + `services.py` + `urls.py` |
| Permissions | `apps/api/core/permissions/` |
| Daily / field reports | `apps/api/core/field_reports/` + web daily_reports components |
| E2E coverage | `apps/web/e2e/tests/` |

## Naming note

Blueprint **Project** ≈ API `projects` (UUID). Older docs may say `Business`.

## Deeper reading

- [Blueprint](https://github.com/Itshossein128/project-management-information-system/blob/develop/docs/IPCAS_Engineering_Blueprint.md)
- [Scope map](https://github.com/Itshossein128/project-management-information-system/blob/develop/docs/ipcas-scope-map.md)
