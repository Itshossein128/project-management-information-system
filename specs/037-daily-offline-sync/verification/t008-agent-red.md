# T008 — browser persistence and upgrade evidence (RED)

Date: 2026-10-27. Product code was not changed by this work. Chromium ran headless with a fresh isolated browser context per scenario against Vite on `127.0.0.1:5198`; storage was not cleared to obtain a passing result.

Command (from `apps/web`): `pnpm exec vite --host 127.0.0.1 --port 5198 --strictPort`.

Command (repository root): `OFFLINE_TEST_ORIGIN=http://127.0.0.1:5198 node --test apps/web/src/app/lib/__tests__/offlineMigration.test.ts`.

Observed: 5 tests, 2 passed, 3 failed, 0 skipped. These are browser assertion failures, not setup/import failures:

- Unknown owner: `pendingIds.includes("legacy-unknown")` was `true`, expected `false`; full payload preservation passed.
- Aborted IndexedDB version upgrade: original data remained readable and failure was reported, but the same module's subsequent `initDB()` retry returned failure (`retried` was `false`, expected `true`).
- Realistic legacy project activity: the complete raw record was preserved, but it remained in the active pending queue (`true`, expected `false`) despite having no proven owner or canonical unit.
- Injected abort of an IndexedDB read-write transaction: write rejected, earlier record remained readable, and the attempted new record was absent (PASS). This simulates a transaction abort, not actual browser quota exhaustion or a power loss.

The legacy record follows the structure and project report activity route emitted by `apps/web/src/app/lib/offlineWrite.ts` (`reportBase` and `queueChildWrite`). That writer records neither actor nor unit and does not prove that a project activity belongs to a specialty unit. A previous test used a fabricated specialty route and asserted a successful mapping and operation ID; that assumption was unsupported, so it was removed and its former failure is not evidence. This test instead requires quarantine and preservation. Mapping of a legacy record with independent, authoritative proof of owner and target remains untested.

Limitations: fixtures instantiate the relevant legacy queue store and its indexes, not a full historical profile. Actual upgrade of all historical stores, quota exhaustion, same-profile browser restart, proof-based mapping and end-to-end account isolation remain unverified. These results are RED only; no product fix or GREEN run was performed.
