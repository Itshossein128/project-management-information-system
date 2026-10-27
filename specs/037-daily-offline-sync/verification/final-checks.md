# Final checks for phases 10 and 11 (T074)

These are the commands run for this pass. They are not a full historical suite.

| Check | Command | Result |
|---|---|---|
| Claims | `node --experimental-strip-types --test apps/web/src/app/lib/__tests__/offlineClaims.test.ts` | 2 passed |
| Replay and migration | `pytest sub_reports/tests/test_sync_concurrent_replay.py sub_reports/tests/test_offline_sync_migrations.py --reuse-db` | 4 passed |
| Schema drift | `manage.py makemigrations --check --dry-run` | No changes detected |
| Browser | interruption, legacy backup, and status specs | 3 passed |
| Typecheck | `pnpm typecheck` | Passed after the row casts were corrected |

Not run in this pass: the entire `field_reports/tests` tree, the entire Playwright tree, and a production deploy. Earlier passes in this feature recorded their own counts in `us2.md`, `us3.md`, `aggregation.md`, `us5.md`, and `us6-us7.md`.
