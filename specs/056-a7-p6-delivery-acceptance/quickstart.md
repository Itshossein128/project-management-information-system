# Reproduce the A.7 acceptance release

نسخه منبع: `2090da13f90756e9512070ffcd4feb87dcf5fd7a`؛ تصویر API: `sha256:0e4bef19068e6b36da9f7de2169486cd3fe73b7ec1f2f3a1c96ae60a62067066`؛ محیط: `a7p5-import:API18000/PostgreSQL55434/Redis56379/Web15173`؛ Django: `4.2.11`.

Use Linux/systemd with cgroup v2, Docker Compose, native PostgreSQL/Redis for host regressions, Node and pnpm. Preserve private environments. Do not run fault-control suites concurrently or against a shared/production database.

From repository root:

```bash
ops/a7-p5/run-acceptance.sh
python3 ops/a7-p5/check-broker-outage.py
python3 ops/a7-p5/check-concurrent-delivery.py
ops/a7-p5/check-host.sh
ops/a7-p5/check-delivery.sh
pnpm typecheck
VITE_API_BASE_URL=http://127.0.0.1:18000/api pnpm build
# Separate terminal; test the compiled release:
HOST=127.0.0.1 PORT=15173 pnpm --filter web start
# Main terminal:
ops/a7-p5/check-delivery-browser.sh
python3 specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py
```

The host scripts source `.env` but create uniquely named test databases. check-delivery runs project registration/lifecycle/restore/concurrency, WBS/template and schedule regressions; check-host runs containment-specific P5 regressions. Fresh migration seeds are important: a reused database flushed by transactional tests can lack permission catalog rows and produce misleading 403s. These test settings do not prove real background execution; the separate 13-group matrix, broker outage, duplicate-delivery and browser recovery tests do.

The browser runner provisions distinct human logins, then runs positive/bilingual/cancellation, ordinary-planner recovery/isolation, ordinary-viewer and P5 retry suites sequentially. It saves credentials only in mode-0600 ignored files and secret-free JSON reports in evidence. Current server must use the matching build/API image. A passing package validator requires report checksums, zero failures/skips, matching source files and schedule-tree digest, all 56 faithful audit rows and all 28 scenarios pass. Employer fields remain pending/blank.

`release-verification.json` is the final verification lock; changing tested source requires rerunning the affected checks and regenerating this lock, never copying old success labels. The original November-10 requirements snapshot stays untouched. Historical P5 independent-operator reproduction is retained separately; this final current-version execution is implementer-run. For delivery artifact loading and checksums use the bundle's README-fa.md.
