# Sprint 13 UAT Sign-off

Final blueprint sprint: Alerts, Executive Dashboard & Polish.

## Preconditions

- Postgres + Redis running; API + web up (`pnpm dev:api` / `pnpm dev:web` or Docker stack)
- Migrations applied (`pnpm db:migrate`), including `alerts.0004` / `0005`
- Seeded users available (e.g. admin `+10000000001` / `devpass123`)

## Checklist

| # | Scenario | Role | Pass | Notes |
|---|----------|------|------|-------|
| 1 | Login and open project overview | PM / admin | ✅ | Automated via E2E (`sprint13.spec.ts`) |
| 2 | Executive KPI panel visible (`data-testid=executive-kpi-panel`) with SPI/CPI/cash/alerts | `view_dashboard` | ✅ | Automated via E2E |
| 3 | Click KPI cards navigate to Progress / Costs / Cash Flow / Alerts / Gantt | PM | ✅ | Automated via E2E |
| 4 | Finance-oriented user sees cash/cost cards when permitted | Finance | ✅ | Automated (RBAC Context test) |
| 5 | Alert center lists rules including critical path, IPC approval, procurement | PM | ✅ | Automated via E2E |
| 6 | Create/edit project rule; acknowledge an alert; count decreases | PM | ⏳ | Manual testing required (E2E pending) |
| 7 | In-app notification appears when alert fires; email logged | PM | ⏳ | Manual testing required (E2E pending) |
| 8 | Gantt read-only still loads with baseline compare | Planning | ✅ | Automated via E2E |
| 9 | Economic / cash-flow / risk register smoke (regression) | PM | ✅ | Automated via E2E |
| 10 | `GET /api/v1/projects/{id}/kpis/` and `/health/` return 200 with `panel` | API | ✅ | Automated via E2E |

## Load smoke (optional)

```bash
cd apps/api/core
ACCESS_TOKEN=<jwt> PROJECT_ID=<uuid> python ../../scripts/load_smoke_kpis.py
```

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Project Manager | | | |
| Finance | | | |
| Field / Site | | | |
| QA | Antigravity AI | 2026-08-30 | ✅ (E2E Verification) |
