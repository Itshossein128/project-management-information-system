# Contract: ISM Editor, Layers and History

**Requirements**: FR-004, FR-009–FR-018 | **API**: [ism-inputs-api.md](ism-inputs-api.md) | **Result**: [ism-result.md](ism-result.md)

## Entry and criterion operations

- Dedicated binary relation editor: semantic labeled table, row=influencing criterion, column=receiving criterion. Native selects offer localized Unanswered, No/0 and Yes/1. Map exact tokens only: empty→null, `0`→0, `1`→1. All diagonals remain editable; new diagonal zero, new cross-pair null. No reciprocal edits or truthiness conversion.
- Each accessible label and clickable issue identifies both ordered criterion names. Keep logical row/column pairing stable under RTL; do not transpose data based on direction. Tab/arrow selection, rename typing/caret and visible focus work in EN and FA.
- Optional operation metadata from `NamedListEditor` specifies rename index, move source/destination, add index or remove index. ISM remaps both axes by operation; rename keeps all existing pairs, move permutes them, removal retains survivors, insertion creates unanswered cross-pairs. No new persisted identity schema. AHP retains established rename clearing and reciprocal behavior.
- API wire data remains guarded `unknown`; a valid editable matrix may use `(number|null)[][]`. Invalid persisted values/containers use a visible invalid/recovery state retaining raw input; do not cast, silently drop or coerce them. A user explicitly correcting/resetting invalid input is a deliberate edit. Empty legacy matrix initializes a new aligned draft, not a fabricated completed result.
- Global save sends aligned criteria/ISM matrix; method-specific ISM save updates only its required fields and does not clear other methods. Genuine shared criterion changes follow existing case validation.

## Permission and operation state

Use existing `usePermission(projectId)` for presentation and existing server enforcement. View-only members can inspect cases, history, direct/derived inputs and layers; creation, selected-method/criterion/relation/ranking edits, all saves and all method runs are unavailable. Add only permission/pending adapters to existing AHP/SAW/TOPSIS panels, preserving their inputs and algorithms.

One route-owned synchronous busy gate covers global save plus every same-case method PATCH→POST. Capture immutable operation variables at acquisition; disable writable controls and reject duplicate/conflicting acquisition before requests. A failed PATCH prevents POST. Release in `finally`, including denial/network errors. History reading remains available.

Key panels by project/case and maintain selection/operation identity. Case switching may navigate to another case; late callbacks from the old case cannot replace the new draft/result or release another operation's gate. Disable edits to the captured case while its mutation is pending. Returned results use their own frozen input even if another client saved between PATCH and POST.

## Current result and failure

Clear current ISM result presentation on a relevant criterion/relation edit, new execution attempt or failure; earlier successes remain inspectable in history. Selection/unmount invalidates late result callbacks. Successful output is associated with the returned run and `input_snapshot`, not the current live names/matrix.

Show precise localized field/cell feedback and focus targets for `ism_matrix.i.j`. Reuse generic 403/404/429, malformed-response and network feedback. Preserve recoverable draft values; no partial analysis, stale result or legacy stub appears as a new successful analysis. If completion is ambiguous after a lost response, inspect/refetch history before an explicit retry; no automatic retry of POST is promised.

## Presentation and frozen review

Render server-supplied ordered numbered layers, explicit maximal mutual groups and read-only reachability beside submitted direct relations. Top/first layers are result-oriented and later/lower layers more foundational within the entered network. Explain that structural position does not establish causal proof, importance, a weight, alternative rank or grounds to remove a criterion as redundant/irrelevant. Same-level criteria need not be mutually reachable.

Historical review always uses frozen criterion names/order, direct matrix, derived matrix, layers/groups, actor and time. Reuse existing history method filter and active-language dates. Switching EN/FA changes labels, number/date formatting and direction only; stored names/judgments/membership/actor/time stay unchanged. Legacy stubs are clearly unavailable analyses.

No interactive diagram, graph editing, DEMATEL conversion, weight transfer, ranking or auto-removal control is introduced. All closure, layer extraction and mutual-group calculation occurs on the server; frontend code performs only entry/remap/validation/structural guarding and presentation.
