# CI and Actions

All workflows live in `.github/workflows/`.

## Core quality gates

### CI (`ci.yml`)

Runs on push/PR to `main` when `apps/**` or lockfiles change.

- **web job:** `pnpm install` → typecheck → build
- **api job:** Postgres + RabbitMQ + MinIO services → migrate → pytest / manage.py tests

Skips draft PRs.

### E2E (`e2e.yml`)

Playwright against the web app. Needs services described in the workflow file.

### Integration Smoke (`integration-smoke.yml`)

Lightweight stack health check (see workflow for triggers).

## Housekeeping samples

| Workflow | Purpose |
| --- | --- |
| `pr-labeler.yml` | Auto-label PRs from path changes (see `.github/labeler.yml`) |
| `stale.yml` | Mark inactive issues/PRs after 60 days |

## Dependabot

`.github/dependabot.yml` opens PRs for:

- npm (repo root / pnpm workspace)
- pip (`apps/api`)
- GitHub Actions versions

## How to add a new Action (pattern)

1. Create `.github/workflows/my-job.yml`.
2. Choose `on:` (`pull_request`, `push`, `schedule`, `workflow_dispatch`).
3. Keep jobs focused; reuse caches (`actions/setup-node` with `cache: pnpm`).
4. Open a PR — the **Actions** tab shows the run.

## Permissions tip

Prefer least privilege:

```yaml
permissions:
  contents: read
  pull-requests: write
```
