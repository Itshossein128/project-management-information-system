# Quickstart Validation: Native MPP Import

**Feature**: `029-native-mpp-import`  
**Date**: 2026-10-20

Design-time validation guide. Run after implementation (`/speckit-tasks` + code). Evidence categories: pytest, typecheck, browser/locale.

## Prerequisites

- PostgreSQL + Redis (see `AGENTS.md`).
- API venv with project requirements (**`mpxj` + JPype** preferred) and a working **JRE** on `PATH` (`java -version`).
- If Python `mpxj` cannot be installed, set `MPP_MPXJ_CLASSPATH` to `mpxj.jar` plus POI/JAXB jars (see local `/tmp/mpxj.jar` + `/tmp/mpxj-lib` pattern used in research) so the Java CLI converter works.
- Root `.env` sourced for API (`DATABASE_URL`, Redis, `CELERY_TASK_ALWAYS_EAGER=true` for local sync jobs). Optional: `MPP_CONVERT_TIMEOUT_SECONDS=60`.
- Seeded project + user with `edit_wbs`; second user/project for IDOR checks.
- Compatibility fixtures under `apps/api/core/schedule/tests/fixtures/mpp/` (see [research.md](./research.md) Decision 10).

## Setup (typical local)

```bash
sudo pg_ctlcluster 16 main start   # if needed
sudo redis-server /etc/redis/redis.conf --daemonize yes
# ensure JRE installed
java -version
cd apps/api && .venv/bin/pip install -r requirements.txt   # after mpxj added
pnpm db:migrate   # includes additive error_code if shipped
pnpm dev:api      # terminal A
pnpm dev:web      # terminal B
```

## Automated checks

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest schedule/tests/test_msp_import.py schedule/tests/test_p6_import.py -q
../.venv/bin/python -m pytest schedule/tests/test_mpp_import.py schedule/tests/test_mpp_convert.py common/tests/test_validators.py -q
```

```bash
pnpm typecheck
```

## Scenario matrix (manual / E2E)

| # | Scenario | Expected |
|---|----------|----------|
| 1 | User with `edit_wbs` uploads valid `.mpp` → preview → append/replace → import | Success summary; WBS/activities created; job `done` |
| 2 | Same schedule as `.mpp` and `.xml` | Equivalent supported WBS/activities/relations/warnings (SC-003) |
| 3 | Nested summaries, leaves, milestones, deps | Hierarchy + supported schedule fields preserved |
| 4 | Corrupt / renamed non-MPP as `.mpp` | `invalid_file_type` or `mpp_corrupt`; no project mutation |
| 5 | Password-protected MPP | `mpp_password_protected`; recovery copy; no mutation |
| 6 | User without `edit_wbs` | 403 on preview/start |
| 7 | Poll other project’s job id | 404/403; no data leak |
| 8 | Append with duplicate codes | Existing kept; duplicates skipped with warnings |
| 9 | Replace | Current replace rules applied |
| 10 | XML + XER regression | Existing tests still green |
| 11 | Forced timeout / converter kill | `processing_timeout` or `conversion_failed`; no partial structures; later import works |
| 12 | Keyboard + fa RTL / en LTR through states | Usable; warnings ≠ fatals; recovery path present |

## API smoke (optional)

```bash
# Preview MPP (token + project id required)
curl -sS -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/fixture.mpp" \
  "http://127.0.0.1:8000/api/v1/projects/$PROJECT_ID/import/msp/preview/"
```

Expect `200` + `wbs_tree` or `400` with stable `error.code`.

## Browser checklist

1. Open project WBS → open MSP/P6 wizard.
2. Confirm help lists `.mpp`, `.xml`, `.xer` (no “MPP not supported”).
3. Select `.mpp` → Preview shows processing → tree.
4. Import → progress → summary → navigate to WBS.
5. Repeat a fatal case (bad file) → recovery to choose another file.

## Pass criteria (maps to spec SC)

- SC-001/SC-006: upload→preview without MS Project; terminal success or clear failure.
- SC-002: ≥95% of “supported” corpus fixtures preview OK.
- SC-003: paired MPP/XML equivalence in tests.
- SC-004/SC-007: rejection + IDOR cases clean.
- SC-005: XML/XER tests green.
- SC-008: keyboard + RTL/LTR browser note recorded.

## Out of scope for this quickstart

- Implementing conversion code (tasks phase).
- MPP export/edit/sync.
- Full Playwright suite unless already wired; browser checklist may be manual for v1 evidence.
