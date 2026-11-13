# Baseline before P5 product changes

**Captured**: 2026-11-12, before the lifecycle migration and import services.

- Branch: `develop`
- HEAD: `ea38dda2eda939184afd502fa027680b40af7870`
- Schedule migration head before this change: `0015_periodreportfigure_version`
- New migrations: `0016_import_operations_lifecycle` and `0017_import_retry_related_name` (related-name state only)
- Feature binding: `SPECIFY_FEATURE_DIRECTORY=/home/hossein/Desktop/projects/building-management/specs/055-a7-p5-import-operations`
- `check_prerequisites.py --json --require-tasks --include-tasks` returned that same `FEATURE_DIR`.

Unrelated dirty paths already present and left in place:

- `output/a7-implementation/phase-map.json` (P5 entry already present; not rewritten)
- P1–P4 handoff/evidence files under `specs/051` through `specs/054`

`phase-map.json` still has the five A.7 entries. No other phase entry was removed.

Rollback of `0016` drops the new columns and the slot table. Bytes already purged cannot be restored from the migration. Drain old import workers before enabling fencing.
