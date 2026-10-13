# Research: Traceable Decision Execution Records

**Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

## Evidence boundary

Read-only backend and frontend research agents inspected current source, related contracts and tests. The existing graphify index located `execution_service.py`, `DecisionRun`, `InputSnapshotViewer` and history/ranking components; its query was truncated and its indexed line numbers differ from current source. Current files, not graph edges, establish the baseline below. No graph rebuild or package update was performed. No application suites or live mutations were run during planning. Runtime inspection confirmed Python 3.12.3, Django 4.2.11 and Node 25.2.1. Prior feature 023 retains 205 backend, 70 helper and 78 browser passes; these are earlier evidence, not acceptance of feature 024.

## R1 — Reuse the existing record envelope and storage

- **Decision**: Extend `DecisionRun` usage, existing scoped endpoints and existing history UI; keep the current JSON snapshot/result and actor/time envelope. No new table, revision field, engine-version field, deduplication key or dependency is required.
- **Rationale**: `models.py` and `serializers.py` already provide the required identity, frozen content, project/case relation and protected initiating user. Immutability is enforced by product routes, not a new database trigger. Current actor display name resolves the user account; the stable identity remains the protected foreign key.
- **Alternatives considered**: A second execution-record model or database trigger would expand scope and complicate legacy compatibility; storing screenshots would misread the source's fixed-input requirement.

## R2 — Lock the authoritative parent before all execution decisions

- **Decision**: In `services/execution_service.py`, move all supported dispatch through one `transaction.atomic` boundary that loads the active, project-scoped `DecisionCase` with `select_for_update`, then checks method selection, validates, computes, deep-copies inputs and appends. Preserve current engine calls and method result shapes. Remove redundant ISM-only transaction orchestration once the common boundary owns it.
- **Rationale**: Current `create_run` uses the supplied instance for SAW/TOPSIS/AHP/DEMATEL-placeholder; only `_create_ism_run` reloads and locks. This proves a stale-instance eligibility/input/deletion gap, not that every current output necessarily mixes states. Django locks evaluated rows through transaction completion; PostgreSQL transaction-capable tests are needed to verify contention. [Django 4.2 locking documentation](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#select-for-update).
- **Alternatives considered**: `atomic` without reload/lock cannot establish authoritative eligibility. Optimistic revisions and cross-request PATCH→POST atomicity exceed this spec. A POST uses one persisted case state at lock acquisition; it does not promise the exact earlier browser draft if another user edited between requests.

## R3 — Serialize case mutation with the same parent

- **Decision**: Lock/reload inside `update_case` before merge, validation and targeted update. Add a narrowly scoped locked soft-delete path to `DecisionCaseViewSet`; preserve current deletion/audit semantics and do not modify the shared base viewset.
- **Rationale**: General PATCH refreshes before merging but has no lock through validation/write; matrix-only PATCH intentionally avoids unrelated ranking validation. Soft deletion currently resolves a row then writes deletion fields without sharing the execution lock. Serializing these paths permits consistent execution eligibility and prevents stale merged validation.
- **Alternatives considered**: Locking only execution leaves a read/merge/validate/write race in PATCH. Full-field writes could overwrite unrelated drafts. Changing project/case retention or bulk deletion is outside scope.

## R4 — Deterministic fixed-set pagination without a migration

- **Decision**: Apply `order_by('-extracted_at', '-id')` explicitly to the scoped history queryset before pagination. Retain existing method filtering and page-number envelope; UI uses ten rows per page.
- **Rationale**: Current model ordering has only extraction time. UUID order is a deterministic tie breaker, not a claim of creation chronology among equal times. Query-level ordering avoids a model metadata migration. Default API page size is 50, maximum 100; retain both and current `page_size`/`per_page` parameters.
- **Alternatives considered**: Cursor pagination or new sequence columns are unnecessary for the 100-record fixed-set acceptance target. Offset pagination while new rows are appended is not guaranteed to represent a frozen multi-page snapshot.

## R5 — Separate new-response validation from historical compatibility

- **Decision**: Add pure unknown-safe guards/classifiers in `execution-record-rules.ts`: draft-compatible case response; list/detail provenance envelope; strict completed method response; partial historical input/output availability. Reuse ISM guards and strengthen AHP null/membership handling without removing legacy sorted AHP rows. Keep transport changes local to Decision Support.
- **Rationale**: `decision-support.ts` rejects malformed mutation JSON already; valid JSON null/empty objects still reach most callbacks. `InputSnapshotViewer` dereferences missing snapshot; shared `apiJson` can return an empty object on malformed reads. Strict completed-response acceptance and safe partial historical review need different policies.
- **Alternatives considered**: Rejecting every old partial record loses readable provenance. Casting types does not validate wire data. Recomputing weights/results to repair missing history violates the spec.

## R6 — Generalize the existing save–execute–recover boundary

- **Decision**: Extract a bounded recovery helper and thin `useDecisionExecution` hook from ISM's established orchestration for SAW/TOPSIS/AHP/ISM. Keep method-specific draft validation, payload construction and presentation in their panels. Use the route's existing per-case `beginOperation`; captured IDs and release callback remain authoritative. Guard global create/PATCH save responses before route callbacks too.
- **Rationale**: ISM validates responses before release and awaits history recovery. Other panels release immediately after PATCH/POST, may retain stale output, and lack awaited recovery. A shared four-panel operation boundary is a small coherent reuse, not a second state framework.
- **Alternatives considered**: Four duplicated recovery flows would drift. A global busy flag would block unrelated cases. Automatic POST retries, idempotency keys and revisions are outside scope.

## R7 — Recover the displayed history, not only an unused cache key

- **Decision**: Persist recovery state by project/case, use one validated unfiltered page-one fetch with `retry:false`, `staleTime:0`, AbortController and a ten-second maximum; invalidate the prefix without automatic active refetch. On success select that fetched view only if the captured case is still selected. On failure/timeout retain explicit uncertainty and release for manual retry.
- **Rationale**: Existing ISM already fixes visible filtered/page-two recovery. Invalidation alone does not establish displayed fresh data; `fetchQuery` provides an awaited read and cache result. Query defaults and options must be checked against installed v5 during implementation. [TanStack Query client reference](https://tanstack.com/query/latest/docs/framework/react/reference/classes/QueryClient).
- **Alternatives considered**: Fire-and-forget invalidation releases too early. Fetching every filtered page adds unbounded work. Page one supports the specified controlled recovery scenarios; other concurrently appended rows may require normal navigation, and absence never proves no commit.

## R8 — Historical review belongs in its read-only viewer

- **Decision**: Extend `InputSnapshotViewer` with named ranking input review and stored SAW/TOPSIS tables, keeping AHP/ISM presenters. Add a small completed-DEMATEL indicator presenter using feature 022's contract, without enabling its engine. Remove route assignments that put selected historical ranking into current panel state. Reuse matrix/table presentation and existing locale keys where applicable.
- **Rationale**: Current viewer presents AHP/ISM but only raw snapshot JSON for rankings. Named criteria/alternatives, types and raw/recorded normalized weights are required for review. TOPSIS retains `d_best`, `d_worst`, `closeness`, score and rank. AHP legacy rows preserve stored names/ranks/order. DEMATEL keeps signed relation and recorded role; no formulas or ranks are derived on the client.
- **Alternatives considered**: Rendering historical values through editable panels blurs historical/current state. JSON alone does not provide the specified readable business review. Building the DEMATEL engine in this feature violates scope.

## R9 — One history-navigation invalidation rule

- **Decision**: Increment historical request generation on case, filter or page transition and new detail selection; clear previous detail/loading/error on navigation, clear or visibly supersede old detail at selection start, and accept detail only if case, selected row ID and generation still match. Read errors belong to history, not input-validation issues. Recovery page changes follow this same rule when navigation actually changes.
- **Rationale**: Route detail requests already protect case and request sequence. Filters reset their generation; page buttons currently do not. Failed selections can retain previous detail. Preserve valid frozen detail when recovery already uses the same history view; never alter the editable draft.
- **Alternatives considered**: Abort alone is insufficient against delivered responses; generations protect even when cancellation races. Loading every detail on page load is unnecessary.

## R10 — Preserve working policies and legacy data

- **Decision**: Keep stored ranking ranks/order and display precision; O01/O02 remain open. Preserve AHP warning semantics, ISM policy and raw unrelated context. Missing historical normalized weights remain unavailable. Placeholder DEMATEL stays a placeholder; completed fixtures test presentation only.
- **Rationale**: Existing method specs already define interim outputs. Source snapshots deep-copy context; no backfill or historical recalculation is justified.
- **Alternatives considered**: Re-ranking equal scores, deriving missing values, or rewriting old snapshots would violate FR-006/010/019.

## R11 — TDD and evidence separated by layer

- **Decision**: Reproduce source-backed gaps with failing tests before fixes; record already-correct behavior as regression. Use PostgreSQL lock observation, exact fixed-set pagination, pure structural guards, actual committed POST with lost response, EN/FA UI and final-tree timing. No mocks alone prove persistence, authorization or numerical independence.
- **Rationale**: Constitution VI and the user's TDD workflow require behavioral evidence. Existing `test_ism_api.py` lock-wait and browser recovery scenarios provide patterns. Tests must use independent connections and synchronization; elapsed sleep is not lock proof.
- **Alternatives considered**: Checkbox-only acceptance or fabricated reds for already-correct math do not verify this feature. Re-running old suites during planning would not validate unbuilt behavior.

All technical uncertainties are resolved for planning. No constitution exception is required. Research identifies proposed work; it does not certify the future implementation.
