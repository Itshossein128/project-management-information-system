# Quickstart: Discipline Sub-Reports Lifecycle and Validation

## Environment Setup & Prerequisites

1. Ensure native PostgreSQL 16 is running on port 5433:
   ```bash
   sudo pg_ctlcluster 16 main start
   ```
2. Ensure Redis is running on port 6379:
   ```bash
   sudo redis-server /etc/redis/redis.conf --daemonize yes
   ```
3. Source environment variables:
   ```bash
   set -a && source .env && set +a
   ```

---

## Running Backend Migrations & Verification

1. Run Django migrations:
   ```bash
   apps/api/.venv/bin/python apps/api/core/manage.py migrate
   ```
2. Verify blueprint schema:
   ```bash
   apps/api/.venv/bin/python apps/api/core/manage.py verify_blueprint_schema
   ```

---

## Running Automated Backend Tests

Run pytest targeting the sub_reports test suite:

```bash
cd apps/api/core && set -a && source /home/hossein/Desktop/projects/building-management/.env && set +a && ../.venv/bin/python -m pytest --reuse-db sub_reports/tests/test_discipline_sub_reports_lifecycle.py
```

---

## Running Frontend Verification

1. Run Vitest component tests:
   ```bash
   pnpm --filter web test
   ```
2. Build and bundle verify:
   ```bash
   pnpm --filter web build
   ```
