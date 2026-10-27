# US2 evidence (T025–T030)

## Reinspection, 2026-10-27

The checklist currently contains 14 checked items. The earlier 16/16 statement below is historical and does not describe the current file. T025, T027 and T030 were reopened because the cases recorded below do not establish all of their requested conditions, including error/identity recovery and every accessible sync state.

Checklist gate: `checklists/requirements.md` 16/16 checked.

## T026

Command:

`node --experimental-strip-types --test apps/web/src/app/lib/__tests__/offlineHydration.test.ts`

Result: 3 passed. The reconciliation behavior was already present, so this run is GREEN proof rather than a newly forced RED. Assertions cover local header overlay, unchanged server rows, local edits, appended rows, and tombstone exclusion.

## T025 and T027

Commands (from `apps/web`, Playwright reused the running API and Vite servers):

- `pnpm exec playwright test --config=e2e/playwright.config.ts e2e/tests/unit-offline-recovery.spec.ts`
- `pnpm exec playwright test --config=e2e/playwright.config.ts e2e/tests/unit-offline-status.spec.ts`

Results: both passed (1/1 each).

T025 opens `/projects/{id}/electrical?date=2026-10-27`, stores a scoped snapshot, blocks `127.0.0.1:8000`, reloads, and reopens the same Chromium persistent profile. It checks recovered notes, the local draft list, edited and created activity cells, and absence of the tombstoned row. Chrome offline mode cannot reload the Vite module graph, so the dead-server check aborts the API instead of `setOffline`.

T027 checks a pending row badge: `data-status=pending`, yellow cloud icon, non-empty accessible name, keyboard focus, and an English label containing "pending" after `i18nextLng=en`.

## Implementation covered by those tests

- `offlineHydration.ts` overlay and tombstones
- current report and activities/labor/materials/machinery/structured section queries keep the local snapshot when the server request fails
- unit panel lists actor/project/unit drafts and opens them by date
- row status badges on activities, labor, materials, machinery, and structured sections
- FA/EN `offline.statusPending|Sending|Synced|Failed|Conflict`
