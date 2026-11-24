# B02 implementation evidence

## Stage 4.2

- **Scope.** B02 implements and verifies the local technical requirements for A.1.03. Employer final acceptance remains pending independent B06 review.
- **B01 dependency.** Verified the [specification](../057-a1-b01-data-contract/spec.md) and [B01 QA handoff](../../output/a1-b01-stage5-qa-verification-2026-11-19.md). Django reported 4.2.11. The configured PostgreSQL database contained 40 of 40 blueprint tables and 25 extension tables, with zero unapplied migrations. The field-reports migration dry run detected no model changes requiring a migration.
- **Lifecycle and provenance.** The B02 regression tests exercise the actual correction, submission, approval, provenance, and cancellation API routes. The two source references survive cloning onto the new row UUID and remain independently queryable inside each approved revision. The correction can be cancelled without changing the restored revision's snapshot, rows, or provenance.
- **Rebuild.** The tests exercise FA/EN responses for explicitly ineligible rebuild targets, editable rebuild with saved opinion and overrides, and approved snapshot preservation during unit submission. Rebuild regenerates a shared activity row into its eligible source rows where the activity aggregation rule calls for one row per source. This prevents one source from overwriting another.
- **Activity log and export.** The API and the generated FILE 1 workbook each expose one official row with quantity 5 and headcount 4 across two approved revisions. The tests warm the cache before opening a correction and verify immediate draft exclusion and restoration after cancellation.
- **Authorization and concurrency.** The test suite covers the direct, batch, legacy, and offline mutation boundaries, active membership, separation of duties, short reasons, concurrent correction requests, date-effective six-unit settings, and source eligibility.
- **Browser.** Two authenticated Chromium walkthroughs passed in FA and EN against local React Router, Django and an isolated synthetic PostgreSQL database. The single-process browser API used a local-memory cache. The walkthrough verified the localized report editor and reading direction, two-source disclosure, metadata save and reload, and activity-log exclusion and restoration across correction opening and cancellation. A live API call in each language confirmed the localized approved rebuild rejection. See the [walkthrough](quickstart.md#4-live-bilingual-walkthrough).
- **Pytest.** The 12 B02 quickstart suites and the B01 data-contract suite passed together on the final code. Pytest reported 140 passes, zero failures, and zero expected failures. The B02 quickstart contributed 129 cases and the B01 suite contributed 11.
- **Frontend.** `pnpm typecheck` passed.
- **Code graph.** `graphify update .` completed after the final source changes.
- **Knowledge retrieval.** The configured hybrid index was stale and its authorized semantic refresh returned HTTP 502. Implementation used the primary B02 artifacts, the B01 handoff, source, and tests.

See the [task record](tasks.md) and [API contract](contracts/version-integrity-api.md) for requirement traceability.
