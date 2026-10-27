# T001 baseline — 2026-10-27

- Checkout `/home/hossein/Desktop/projects/building-management`, branch `develop`, HEAD `89ac5db`; `.specify/feature.json` selects `specs/037-daily-offline-sync` and prerequisite script confirms that directory.
- Prior to implementation the only Git-status entries were the untracked feature 037 specification, plan, research, data model, contracts, checklist, quickstart and tasks. They are user-requested artifacts and must be preserved. `.specify/feature.json` is ignored by Git.
- `requirements.md`: 14/14 checked, no unchecked items; this is a specification-quality gate, not implementation evidence. No before/after implementation hooks registered in `.specify/extensions.yml` at this check.
- Evidence baseline is `reports_gaps/04/GAP-SPEC-04-DAILY-OFFLINE-SYNC.md` and `reports_gaps/04/evidence/README.md`, audited on `develop@765e54b` (not current HEAD). Existing 17 pytest passes are narrow; 4 successful backend probes explicitly assert defects, frontend harness uses mocks, and race probe is simulated. No current feature acceptance is inferred.

## Gap inventory (all require current canonical verification)

| Gap | Snapshot observation | Required proof |
|---|---|---|
| G01 | Current unit path lacks offline integration | Same unit UI persists and syncs actual data |
| G02 | POST slash parsing/ack may lose operation | Targeted operation and explicit ack |
| G03 | Partial snapshot can replace section | Target-only mutation preserves other writers |
| G04 | Legacy batch can mutate derived summary | All routes refuse direct derived mutation |
| G05 | Status check races approve/current change | Real independent PostgreSQL connections |
| G06 | Row error/retry loses targeting | Corrected row only, stable error and linked operation |
| G07 | Row identity/status incomplete | Stable UUIDv4 row, distinct operation and accessible pending |
| G08 | Local queue does not prove UI hydration | Browser refresh and profile reopen recovery |
| G09 | Old results/summary vs requested operation contract | Versioned compatibility and precise codes/IDs |
| G10 | Conflict display/transfer incomplete | Complete snapshots and formal correction |
| G11 | syncing recovery/overlap incomplete | Crash/two-tab recovery with idempotency |
| G12 | Invalid header may leave shell | Per-operation rollback/no side effect |
| G13 | Existing tests do not cover real scenarios | Canonical RED/GREEN, API, race, browser and migration evidence |
