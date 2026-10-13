# Contract: History Navigation and Guarded Execution UI

**Covers**: FR-008–FR-019 | [API](execution-api.md) | [Stored review](result-review.md)

## Existing surfaces to extend

Keep the current project Decision Support route and case navigation. Extend `ExecutionHistoryList` and `InputSnapshotViewer`; reuse `RankingResultTable`, `CriteriaWeightTable`, ISM matrices/layers and common loading/error/empty controls. Add named ranking snapshot and completed DEMATEL indicator presentation only as needed. No new navigation product or independent method-workspace state store.

History rows remain accessible buttons identifying method/time/actor. A read-only viewer identifies the historical record explicitly. Empty history, no matches, loading, read failure and unavailable historical sections are localized and keyboard readable. Ten-by-ten tables support horizontal navigation and named axes in both reading directions. View-only members can review but no writable controls or bypass requests are allowed.

## History state and transitions

Use the existing query key `['decision-runs',projectId,caseId,methodOrEmpty,page]` and page size 10. Filter change selects page one; page navigation clears stale detail and invalidates its generation. Case change clears the previous case's selection/loading/error before loading the new one. An out-of-range page offers a return to first/valid page without another case's cached rows; a failed list query is not labeled empty.

At row selection, capture case, row ID and an incremented history generation. Clear/supersede the previous selection and show loading. Publish only a matching, safely classified detail if that generation and captured case/row still match. A later row selection, page/filter/case transition or permission loss invalidates older completions. Failure is a history-specific retryable read state, not an input-validation failure and not the previous row presented as the new selection. Retry is GET only.

The route's current case selection generation and per-case pending map remain authoritative. Remove historical ranking assignments into current panels. Opening details, paging, filtering or switching locale performs zero save, execution, weight-transfer or normalization operations.

## Save–execute operation ownership

Shared `useDecisionExecution` is a thin lifecycle helper. Panels keep their existing input validators, payload builders and output presenters. Hook/helper receives captured project/case/method, a cloned payload, `beginOperation`, guarded callbacks and the route's history-recovery transition. It has no calculation logic.

1. Clear stale current success when relevant inputs change or an attempt begins; reject local invalid input with locatable feedback before network mutation.
2. Acquire the synchronous existing case token. Capture immutable payload/IDs/release; same-case controls are protected through PATCH, POST and any recovery.
3. Await PATCH and validate a draft-compatible returned case before publishing saved metadata. Failure/unconfirmed save stops; zero POST occurs.
4. Mark POST started before dispatch. Await POST; accept only the expected completed method envelope/frozen input/output. Success can update current result only for its captured active panel/case.
5. Any failure/unconfirmed response after POST started awaits bounded history recovery. No mutation retry is configured. Clear current result and retain the draft; feedback cannot promise that nothing committed.
6. Release the captured token in `finally` only after response validation and recovery settlement. Old case release never releases a newer case token. Returning to a pending case keeps its protection and existing committed-row hydration behavior.

Global case create/PATCH uses the same metadata guard before its success callback; it never initiates a method run itself. Guard intentionally unfinished/raw draft fields without running numerical eligibility checks. Do not replace permission enforcement with UI disabled states.

## Shared bounded recovery

Use recovery key `['decision-execution-recovery',projectId,caseId]` (proposed replacement for method-specific ISM feedback; all adapters use one representation). Keep cached checking/refreshed/failed state across unmount/reselection. Beginning a new confirmed flow clears/supersedes old feedback; components render this state through shared localized messages.

Invalidate captured case history with `refetchType:'none'`, then await one `fetchQuery` for unfiltered page one, with `staleTime:0`, `retry:false`, validated count/rows and abort signal. Ten seconds is the total recovery wait; on deadline abort and classify unresolved. Late completion after deadline cannot flip failed feedback or change another case's visible history.

On successful lookup, route `showRecoveredHistory(caseId)` checks the current case ref before selecting all methods/page one. If this changes navigation, it invalidates old detail ownership; if already showing that view, valid frozen selected detail may remain. The displayed count/rows must use the exact fetched key. Messages describe the visible transition and advise reviewing saved runs before explicit retry. On another selected case, update only captured cache/feedback, leaving that case's filter/page/detail untouched.

On failed/malformed lookup or timeout, preserve explicit unresolved feedback and existing readable history; never mark old cache data refreshed. Release permits manual retry after settlement. Do not infer no commit from empty history. Existing count/detail browsing remains available while same-case mutation is blocked.

## Behavioral test matrix

- SAW/TOPSIS frozen ranking input/output after live rename/reorder/weight/cell edits; historical selection leaves draft and current output untouched; disagreement and tie fixtures keep stored ranks.
- Global save plus four live method panels: empty/HTML/truncated/null/object/wrong-identity or method/missing snapshot/invalid result 2xx. Verify zero POST after unconfirmed save, localized failure, cleared success, no callback crash and preserved draft.
- Four live methods: real server POST commits once, response alone lost/replaced; held history GET keeps gate; no automatic second POST; successful filtered/page-two recovery exposes ID/count; HTTP/malformed read failure and ten-second timeout explicitly unresolved.
- Pending A→B→A and reselect, recovery finishing on A while B filtered/pending, old detail after row/filter/page/case change, read failure after prior successful detail; verify ownership and correct next manual action.
- Historical partial/missing snapshots, stored missing normalized weights, old placeholders, legacy sorted AHP and signed DEMATEL fixture indicators; safe readable unavailable states, no derivation.
- Real viewer/no-view/foreign-project/case controls and direct requests, keyboard named axes, locale dates and switches, fixed 100-record pagination/selection timing.
