# Contract: DEMATEL Workspace and History

**Requirements**: FR-001–FR-005, FR-009–FR-017

## Input and permission experience

Add a DEMATEL panel alongside existing methods. Extend `SquareMatrixEditor` with explicit `dematel` behavior: directed independent cells, fixed read-only zero diagonal, 0–4 decimal scale, null off-diagonal defaults, localized row-to-column influence wording and `dematel_matrix.j.k` validation targets. No reciprocal presets or AHP consistency text in this mode. Retain AHP's existing pairwise behavior unchanged.

Use optional named-list edit operation/index metadata to preserve DEMATEL pairs during rename/move/add/remove. Existing AHP rename-clearing rules remain independent. Changes to criteria save both names and their remapped DEMATEL matrix. Keyboard typing/caret and axis alignment must work in LTR and RTL.

Read permission enables viewing cases and history. Existing edit permission enables create, input changes, save and run. Use existing `usePermission(projectId)` for controls, retaining server authorization. A view-only member must not receive writable matrix/method/criterion controls.

## Save/run lifecycle

One route-owned coordinator serializes global case save and every method panel's save/run for the current case. Existing AHP/SAW/TOPSIS panels require minimal permission/pending/coordinator adapters because they currently issue independent PATCH→POST requests; keep their calculations and input semantics unchanged. Deep-copy the submitted draft; save before running. On save failure, do not submit run. Disable relevant same-case edit/save/run controls while pending, prevent accidental duplicate clicks, and ignore late responses after selection/unmount. View-only mixed-method cases must not expose writable controls in any visible method panel.

Invalidate current DEMATEL result after input edits, at new run start and on failure. History remains available. Render each successful result using the returned run's frozen criteria, never labels from a newer live draft. Do not imply that a separately saved-and-run result matches an intervening edit by another client; the snapshot is its provenance.

Errors are visible and localized; preserve recoverable entries. Reuse the generic request issue helper for 403/404/429/non-JSON failure and network error. Cell issues identify both criterion names and focus the matching editable cell. Matrix-level all-zero/singular/reliability feedback explains why no result exists.

## Result and history presentation

`DematelResultTable` displays criterion, D, R, prominence, signed relation and server-assigned role in snapshot order. Show that judgments express modeled influence, not established real-world causation. No derived client calculation, prominence ranking, weight-transfer button or causal diagram.

`InputSnapshotViewer` renders the frozen directed matrix, result and calculation policy/context for DEMATEL. Reuse locale-aware `ExecutionHistoryList` and existing filtering/pagination. Active-language dates and actor/time use the historical record. Stub/unrecognized output is unavailable, not a numerical success.

Add API `DematelRunResult`/row types and a structural finite-result guard before rendering. Extend static and dynamic i18n coverage for roles/error keys; a source audit checks the client math boundary but does not replace behavioral tests.

## Required browser acceptance

Both EN and FA: valid chain without ranking inputs; decimal and explicit-zero entry; blank/error focus; all-zero/singular rejection; incomplete draft save/reload; keyboard focus and criterion rename/reorder/add/remove; unchanged ranking inputs; frozen history after edits; language switch with mismatched browser locale; view-only mixed-method controls and denied mutations; request failures/retry recovery; delayed saves, an already-pending other-method save followed by attempted DEMATEL/global save, duplicate clicks and case-switch response isolation; no stale current result after changed/failed analysis.
