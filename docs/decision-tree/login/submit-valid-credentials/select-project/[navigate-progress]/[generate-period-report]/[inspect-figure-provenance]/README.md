# Decision: Inspect figure provenance

## Context & Screen

- **Route**: `/projects/:projectId/progress`
- **Trigger**: Select the provenance action beside a report figure.

## Desired Result

- **API Call**: `GET /api/v1/projects/:projectId/progress-reports/figures/:figureId/sources/`
- **UI Feedback**: An accessible table presents Solar Hijri source date, daily report code, source type, contribution, creator, and approving supervisor.
- **Integrity Guard**: Referenced daily reports and child execution rows use protected foreign keys, so physical deletion is rejected while provenance exists.
