# Data Model: ISM Inputs and Frozen Analysis

**Feature**: [spec.md](spec.md) | **Contracts**: [inputs/API](contracts/ism-inputs-api.md), [result](contracts/ism-result.md), [UI](contracts/ism-ui.md)

## Existing persisted entities

### DecisionCase

Existing project-scoped soft-deletable workspace in `apps/api/core/decision_support/models.py`; no new fields.

| Field | ISM role | Validation/lifecycle |
| --- | --- | --- |
| `id`, `project_id` | Authorized identity | Existing UUID/project scope; active manager excludes deleted cases |
| `title` | Workspace label | Existing required/max-200 policy |
| `selected_methods` | May include stable `ism` | Existing method validation; run rechecks locked saved selection |
| `criteria` | Ordered matrix-axis names | Execution 1–10 trimmed, nonempty unique strings |
| `ism_matrix` | JSON direct judgments | Incomplete/finite-invalid drafts recoverable; execution exact n×n numeric 0/1 |
| Other method/ranking fields | Unrelated data | ISM does not consume or rewrite; matrix-only correction isolates validation |
| Existing audit fields | Creation/update provenance | Existing behavior preserved |

Cell `(i,j)` means i influences j; opposite cells are independent. Zero is deliberate absence, null unanswered. Both direct diagonal zero and one are valid; new diagonal zero, other cells null. Actual numeric nonfinite/overflow cannot enter JSON through supported saving paths. Finite nonbinary/text/bool or malformed persisted containers must remain visible/recoverable and cannot execute.

Rename/move/add/remove operation metadata aligns both axes and ordered names without persistent criterion IDs. Genuine shared criterion changes retain existing ranking validation boundaries; AHP retains its established independent reconciliation semantics.

### DecisionRun

Existing immutable run; one case has many runs, each also belongs to the case's project. Actor foreign key is protected.

| Field | Content |
| --- | --- |
| `id`, `case_id`, `project_id` | Distinct run and scoped parent |
| `method` | Stable `ism` |
| `input_snapshot` | Deep-copied saved ordered criteria/direct matrix and existing generic fields |
| `result` | Completed ISM shape and frozen policy from result contract |
| `extracted_at`, `extracted_by` | Server time/initiating member |

Compute/snapshot/append uses the same active authoritative case inside an ISM-only atomic locked path. No run on validation/derivation failure. Later successes append; old input/result/actor/time never updates. Run mutation rejection and pagination remain unchanged. Legacy stubs stay unavailable computations; no backfill.

## Derived objects stored in run JSON

| Object | Fields and invariants |
| --- | --- |
| Reachability matrix | n×n integer zero/one, frozen name order, self and complete direct/indirect paths; direct input unchanged |
| Structural layer | `{level,criteria:string[]}`; consecutive levels from one, every criterion once, original member order, levels≤n |
| Mutual group | `{level,criteria:string[]}`; maximal mutually reachable class with ≥2 members; disjoint classes, common layer, original member order |
| Derivation policy | Exact language-independent identifiers in result contract, version `ism-v1`; no localized scientific data |

Group ordering is layer then first original member index. Singletons/self-only/same-level criteria are not invented groups. First layer is top/result-oriented and later layers more foundational within the modeled network, not weights/ranks/deletion advice.

## Nonpersisted UI state

- Raw hydrated API data stays guarded unknown. Valid editable matrices use `(number|null)[][]`; invalid branch retains raw values and explicit correction/reset state.
- Optional criterion operations preserve ISM pairs without matching renamed strings or changing AHP behavior.
- Current result references a returned run and frozen input; relevant draft edits/new attempts/failure/selection changes clear it. Historical selection remains independent.
- One synchronous same-case mutation gate coordinates global save and every method PATCH→POST; captured project/case/draft/operation identity prevents overlap and late response attachment. No persistent revision/lock/status field is added.

## Transitions

| Action | Outcome |
| --- | --- |
| New/editable draft → save | Updated case, null retained, no run |
| Incomplete/finite invalid → execute | Locatable issues, retained input, zero run |
| Actual nonfinite → save | Rejected before JSON storage, recoverable client draft |
| Valid selected saved case → execute | Scoped lock/reload, compute/freeze, new completed run |
| Deselected/deleted/unauthorized → execute | Selection/scoped denial, zero run |
| Successful run → edit/rerun/locale switch | Old record unchanged; later run distinct |
| Pending mutation → conflicting local action | Gate rejects/controls disabled |
| Case switch → old response | New case unaffected; old case may retain its legitimate run |
| Legacy stub → review | Unavailable result plus stored snapshot, no upgrade |

## Compatibility

No schema/data migration is expected; implementation still runs migration dry-run and preserves existing data. Generic serializers continue exposing case JSON/run envelopes. Frontend guards/types and schema documentation add ISM result semantics only. Existing algorithms, DEMATEL placeholder behavior and permission identifiers remain unchanged.
