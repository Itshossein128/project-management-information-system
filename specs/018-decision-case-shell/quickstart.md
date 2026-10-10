# Quickstart: Decision Support Case Shell (Phase 1)

Validate Phase 1 against [spec.md](./spec.md) using contracts and pytest. Does not include engine numeric checks (AC14+).

## Prerequisites

- PostgreSQL + Redis running (see root `AGENTS.md`)
- API venv at `apps/api/.venv`; root `.env` with `DATABASE_URL`
- Migrations applied after implementing the app: `pnpm db:migrate`
- Dev user with project membership and `edit_decision_support` (seed/update role grants per [data-model.md](./data-model.md))

## Automated checks (primary evidence)

From `apps/api/core` with env sourced:

```bash
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest decision_support/tests/test_validators.py -q
../.venv/bin/python -m pytest decision_support/tests/test_runs_immutability.py -q
../.venv/bin/python -m pytest decision_support/tests/test_case_api.py -q
```

**Expect**:

| Suite | Covers |
|-------|--------|
| `test_validators` | AC05–AC12 structural fixtures; empty≠0; issue `path` present (AC26); AC11 normalize equality |
| `test_runs_immutability` | Stub run snapshot retains names (AC23); case change + second run leaves first snapshot unchanged (AC24); PATCH run → `run_immutable` |
| `test_case_api` | Membership + permission gates; create/patch case; IDOR 404 across projects |

## Manual API smoke (optional)

Base: `/api/v1/projects/{project_id}/decision-cases/`  
Contracts: [decision-cases.md](./contracts/decision-cases.md), [decision-runs.md](./contracts/decision-runs.md)

1. `POST` case with title, methods `["saw"]`, criteria/alternatives length 2, weights/types, empty or filled matrix per contract.
2. `POST …/runs/` with `{"method":"saw"}` — if matrix incomplete, expect `decision_input_invalid` with `issues[].path` and **no** new run.
3. Complete ranking inputs → stub run `201`; `GET` run → `input_snapshot` matches.
4. `PATCH` case weight → `POST` second run → `GET` first run unchanged.
5. `PATCH` first run → `run_immutable`.

## UI smoke (after web shell)

1. Open project → nav **Decision Support** (not Decisions workflow).
2. Create case; edit criteria/alternatives (max 10); multi-select methods.
3. Trigger validation error (duplicate name) → issue list shows location.
4. Switch `fa` / `en` → shell labels localized.
5. History empty state, then after stub run, history row with method/time/actor (read-only).

## Out of scope for this quickstart

- SAW/TOPSIS scores, AHP CR, DEMATEL/ISM layers  
- Full matrix editors  
- Excel import  

## Evidence categories (constitution VI)

| Claim | Evidence |
|-------|----------|
| Input contract | pytest `test_validators` |
| Run immutability | pytest `test_runs_immutability` |
| Authz / tenancy | pytest `test_case_api` |
| Bilingual shell | UI smoke (or locale key review if UI deferred in a PR) |
