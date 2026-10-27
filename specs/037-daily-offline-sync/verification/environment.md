# T004 isolated test environment

On 2026-10-27, `pg_isready -p 5433` reported accepting connections, `redis-cli ping` returned PONG, API virtualenv Django is 4.2.11, pnpm 10.17.0, Node 25.2.1. Chromium and headless shell are present in the Playwright cache. RabbitMQ and MinIO availability was not established and no storage integration result is implied.

API baseline: run from `apps/api/core` with `set -a; source /home/hossein/Desktop/projects/building-management/.env; set +a`, `AUDIT_LOG_ASYNC=false`, `CELERY_TASK_ALWAYS_EAGER=true`, and a newly generated `TEST_DATABASE_NAME=test_037_baseline_<timestamp>_<pid>`. One pytest process per test DB; no passwords or .env values in logs. Full command and output are in `baseline-pytest.log` when complete. The named test DB is pytest-managed, not the development database.

Browser tests use `apps/web/e2e/playwright.config.ts`, but its `global-setup.ts` invokes migrations and `seed_e2e` on the configured database: create a disposable development database and point `DATABASE_URL` to it before running, do not seed/reset shared development data. Start or let config start API/web against the same isolated DB, with Redis available. To verify restart, make a unique temporary browser profile directory, keep it through close/reopen and remove only that test-owned directory after results are captured. Use project/actor fixtures generated for the isolated environment; retain trace/IDs with no credentials. Baseline Playwright has not been run in this setup.

Baseline pytest completed with exit 0: 37 passed, 2 warnings in 109.93 seconds; see `baseline-pytest.log`. This is a baseline, not proof of the 037 acceptance scenarios.
