# Data Model: Traceable Decision Execution Records

**Spec**: [spec.md](spec.md) | **Research**: [research.md](research.md)

## Persistence design

Reuse the existing `DecisionCase` and `DecisionRun`; no schema migration is planned. History tie ordering is applied to its queryset, not model metadata. No existing stored run is backfilled, repaired or recalculated. A schema change discovered during implementation requires explicit design revision and preservation/rollback verification.

### DecisionCase — live editable source

| Existing field | Meaning / constraint |
| --- | --- |
| `id`, `project_id` | Stable case and authorized project scope |
| `title`, `selected_methods` | Current title and eligible method IDs |
| `criteria`, `alternatives` | Ordered named axes, each within existing method input limits |
| `weights`, `types`, `performance_matrix` | Raw ranking inputs; strict eligibility applies at ranking execution |
| `ahp_matrix`, `dematel_matrix`, `ism_matrix` | Method judgments, preserving existing draft policies |
| Audit/soft-delete fields | Existing user/time/deletion semantics; an inactive case cannot be executed |

Raw unfinished or finite-invalid method drafts remain recoverable under existing contracts. In particular, ISM root JSON null and unfinished null cells remain distinct from SQL NULL and zero. Targeted AHP/ISM matrix saves must not revalidate unrelated malformed ranking drafts. Existing general-save validation is preserved.

### DecisionRun — one persisted attempt

| Existing field | Meaning / invariant |
| --- | --- |
| `id` | UUID already supplied by the shared model; unchanged identity format |
| `case_id`, `project_id` | Parent case and its project; record queries check both |
| `method` | One stable existing method ID |
| `input_snapshot` | Deep-copied input/context actually used for that method |
| `result` | Stored method output; legacy placeholders/incomplete objects remain retained |
| `extracted_at` | Recorded execution time, never rewritten by live case changes |
| `extracted_by_id` | Initiating user identity with existing protected relationship |
| `created_at`, `updated_at` | Existing shared timestamps; no new user-facing revision semantics |

One explicit successful request appends one run. Repeated explicit requests can append identical analyses with different identities. Product routes forbid individual run PUT/PATCH/DELETE. Direct ORM fixture writes do not establish a user permission or change this route contract. Case/project deletion policy remains unchanged.

`extracted_by_name` is a serializer presentation field from the initiating user's current account; it is not a frozen member-name snapshot. Missing display name falls back to recorded identity. User deletion remains protected by the existing relationship.

### Frozen input / output payloads

| Method | Required completed input review | Recorded completed output |
| --- | --- | --- |
| SAW | Ordered criteria/alternatives, types, raw weights, `weights_normalized`, performance matrix | Stored option/score/rank rows |
| TOPSIS | Same ranking context | Stored option/score/rank, `d_best`, `d_worst`, `closeness` |
| AHP | Ordered criteria, submitted pairwise matrix | Stored named weights/ranks, lambda max, CI, CR, consistency flag |
| DEMATEL, when available | Ordered criteria, direct influence matrix | Stored prominence/relation rows and available matrices/policy per [022 contract](../022-decision-dematel/contracts/dematel-result.md) |
| ISM | Ordered criteria, direct binary matrix | Stored reachability, layers, mutual groups and policy per [023 contract](../023-decision-ism/contracts/ism-result.md) |

Preserve every context field already in `_snapshot_from_case`, even when unrelated to the executed method. New ranking runs retain computed normalized weights from the engine output. Historical missing normalized weights are unavailable, never recomputed. Stored output order/ranks are authoritative; named membership may be guarded without recalculation or re-sorting.

## Transient frontend state

- **History selection**: project/case, method filter (`''` means all), page, selected run identity, request generation, loading/error. Navigation invalidates pending detail ownership. A detail never writes current method-result or input state.
- **Current method result**: confirmed latest execution for that panel only; cleared on relevant input changes and a new/failed/unconfirmed attempt. Historical browsing does not replace it.
- **Pending operation map**: existing per-case token and captured selection version; one same-case save/run at a time. New unsaved draft uses its existing null key. Other cases remain independent.
- **Recovery state**: query-cache value keyed by project/case, holding `checking`, `refreshed`, `failed` or null and optional initiating-method context. Transient only; do not migrate old ISM cache data as persisted records. Preserve across panel unmount/reselection, clear/supersede on a confirmed new attempt, and clear project-local cached disclosure on access loss as appropriate to existing auth behavior.
- **Historical classification**: safe provenance, available named inputs and either completed method presentation or explicit unavailable sections. It can represent partial legacy content without pretending it is a newly confirmed successful execution.

## State transitions and consistency

### Authoritative backend execution

Request scoped and authorized → transaction starts → active parent row locked/reloaded → method ID/selection checked → required input validation → pure engine compute (or existing DEMATEL placeholder) → snapshot/output copied → one append → commit. Any failure before commit appends zero runs. A stale caller instance supplies lookup identity, never authoritative input/eligibility.

Case PATCH: authorize → lock active scoped parent → merge only submitted changes for validation → preserve matrix-only bypass rules → targeted fields plus audit update → commit. Soft delete: authorize → same parent lock → existing deletion/audit mutation → commit. Each uses the same row boundary; whichever operation acquires it first determines the valid sequence. Do not lock project/user joins unnecessarily.

### Client save–execute–recover

Idle → acquire case token → validate captured PATCH response → begin POST → validate completed response → publish confirmed current result → release. An unconfirmed save stops before POST. Any unconfirmed response/error after POST began enters checking → one bounded history GET → refreshed or failed/timeout → release; POST does not repeat. Local validation failure never acquires/sends a mutation. Callback publication additionally requires active captured-case ownership.

### Historical navigation

Select row → clear/supersede previous detail → capture case/row/request generation → read detail → publish only if still owned. Case/filter/page change invalidates the generation and clears stale detail; rapid row changes accept only the last requested row. Recovery selects its fetched unfiltered page one only for the still-selected captured case, using the same navigation invalidation rule.

## Query and compatibility invariants

- History order is `(-extracted_at, -id)`; method filter precedes pagination. Equal-time UUID ordering is deterministic, not an inferred execution chronology.
- Fixed-set page traversal is complete and duplicate-free. Concurrent insertion can shift offset pages; this design offers no multi-page snapshot guarantee.
- Strict new-response guards require valid method/provenance/snapshot/completed result. Historical classifiers accept partial inputs with explicit unavailable sections; response-envelope failure is a history read error, not a fabricated record.
- No engine math, weight normalization, ranking, reachability or derived indicator calculation occurs in serializers, routes, presenters or guards.
