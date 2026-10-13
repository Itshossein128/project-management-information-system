# Contract: Stored Result Review and Compatibility

**Covers**: FR-005–FR-006, FR-009–FR-013, FR-018–FR-019 | [Spec](../spec.md)

## Classification boundaries

Treat wire input as unknown. Distinguish strict newly completed execution acceptance from safe historical presentation. A usable historical provenance envelope may contain missing/null/non-object snapshot or unavailable output; it must not crash. If even provenance is unusable, show a history read error and no invented record. Keep raw snapshot details as supplemental evidence, not the primary named review.

Validate shapes, finite numbers, named membership, recorded dimensions and required policy identifiers where defined. These guards must not derive scores, ranks, normalization, inconsistency, closure, layers or influence indicators. Preserve every valid stored row's ordering and rank. Do not require a legacy result to satisfy a newly invented numerical or version policy.

## Named historical inputs

For every available method snapshot, display original criterion names in original order and its direct judgments with named row/column axes. Ranking review additionally displays alternatives in original order, criterion type, raw weight, stored normalized weight and performance matrix. Labels and table axes use frozen values even if live names/order/method selection differ.

Display missing or unusable sections as unavailable. An explicit numeric zero stays zero; blank/null/missing stays distinguishable, never a substituted zero. Partially available inputs can be reviewed independently of unavailable output. Missing historical normalized weights stay unavailable; do not calculate them from raw weights. User-supplied names remain user text, not translated or injected markup.

## Method result presentation

| Method | Required stored presentation / existing contract |
| --- | --- |
| SAW | `status:ok`, `engine:saw`, ranking rows `option,score,rank`; reuse ranking table and stored order/ranks |
| TOPSIS | `status:ok`, `engine:topsis`, rows additionally `d_best,d_worst,closeness`; reuse current extra columns/precision |
| AHP | Existing `weights` rows with criterion/weight/rank, `lambda_max,ci,cr,is_consistent`; reuse named weight/inconsistency presentation |
| ISM | Existing `reachability_matrix,layers,mutual_groups,derivation_policy`; reuse structural viewer and input matrix |
| DEMATEL, completed records only | `criteria_results` with criterion/d/r/prominence/relation/role, direct frozen matrix, available normalized/total-relation matrices and numerical policy from [022](../../022-decision-dematel/contracts/dematel-result.md) |

Ranking output membership matches frozen alternative names; required numbers are finite, ranks positive integers and names unique. Do not sort result rows again. If a TOPSIS legacy row lacks its distance data, show that information unavailable rather than invent it; independently usable recorded ranking data can still be displayed as partial historical output. Strict new TOPSIS acceptance requires its complete output.

AHP historical sorted rows are valid when unique names/ranks/finite values reference the frozen criteria; they need not be in input order. Preserve the existing reversed-row compatibility fixture. AHP `CR > 0.1` remains a stored inconsistency warning under its current policy, not a new failed-execution classification. Harden null/missing shape handling before invoking the existing table.

ISM uses existing structural guards and v1 policy without recomputation. Its mutually reachable groups are not rankings or weights. Raw malformed direct input can still be presented safely beside unavailable computed output.

For completed DEMATEL fixtures, match criterion row names/dimensions to frozen order, preserve signed relation and role IDs (`influencing`, `receiving`, `balanced`), and localize only labels. Reuse feature 022 shape/policy; do not run a solve, infer role from displayed rounded numbers, invent a rank or feed ranking weights. A fixture verifies review only, not live engine delivery.

## Legacy and failure examples

| Stored/returned content | Expected behavior |
| --- | --- |
| `result:{status:'stub',engine:null}` | Readable provenance/input and explicit unavailable calculation |
| Missing/null snapshot | Provenance retained; named input unavailable; no callback/render crash |
| Snapshot has raw weights but no normalized weights | Raw weight table retained; normalized section unavailable |
| Wrong engine, unknown/duplicate names, nonfinite result or broken dimensions | Unusable computed sections unavailable; no fabricated replacement |
| Usable ranking rows, older missing TOPSIS distances | Stored ranking retained with unavailable distance information, never synthesis |
| Current method deselected or live names reordered | Old record remains readable using its own labels |
| Actor display name missing | Recorded actor identity fallback; current reviewer is never substituted |
| Malformed new mutation response | Reject current success within acquired guard; use recovery if POST began |

## Separation from current result

Selecting history writes only selected historical detail. It must not inject old rows into `latestSawRanking`, `latestTopsisRanking` or any current method result, mutate draft fields or invoke save/execute. Current confirmed results and read-only history have explicit separate labels. A method panel clears stale current output on relevant input change/new failed attempt under the [UI state contract](history-ui.md).

Existing interim ordinal ranks, tie stability and score/distance display precision are preserved; O01/O02 remain open. Language switching formats presentation only, leaving stored names, order, numbers, identities and times unchanged.
