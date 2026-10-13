# Contract: Execution and History API

**Covers**: FR-001–FR-008, FR-013–FR-017, FR-019 | [Data model](../data-model.md)

## Existing routes and authorization

Base: `/api/v1/projects/{project_id}/decision-cases/{case_id}`.

| Request | Required access | Outcome |
| --- | --- | --- |
| `GET {base}/runs/` | Project membership + `view_decision_support` | Paginated scoped history |
| `GET {base}/runs/{run_id}/` | Same view access | One scoped immutable record |
| `POST {base}/runs/` | Membership + `edit_decision_support` | One recorded attempt under existing method behavior |
| `PUT/PATCH/DELETE {base}/runs/{run_id}/` | Existing edit check, then scoped resolution | Coded `run_immutable` rejection; no mutation |
| `PATCH {base}/` | Existing edit access | Targeted live-case save, serialized with execution |
| `DELETE {base}/` | Existing edit access | Existing soft-delete semantics serialized with execution; no new retention policy |

Case creation remains the existing project collection POST, returning the same case shape. Existing administrator policy remains applicable. Unauthorized requests disclose no content; nonexistent/foreign/deleted parents or nested run mismatches remain scoped not-found outcomes. Resolve parent and run through the URL project, including mutations against individual immutable runs.

## Execute request and authoritative state

POST body contains only the requested stable `method`, e.g. `{"method":"topsis"}`. No client-provided snapshot, output, actor/time, idempotency key or revision is trusted or introduced.

Inside one transaction, load the active parent by its identity and authorized project with a row lock before using selected methods or inputs. Validate only required method inputs, run the current pure engine, deep-copy snapshot/result and append. Return 201 only after a successful append. Invalid method or unselected method returns the existing coded validation issue at `method`; invalid input uses current field/cell paths. Rejection appends zero runs. New ranking snapshots contain raw and normalized weights. Criteria-only execution does not require valid unrelated ranking input.

SAW/TOPSIS/AHP/ISM retain their existing computed contracts. DEMATEL still returns its existing `status:stub, engine:null` record until feature 022 implements its engine; a 201 placeholder is not completed numerical acceptance and must not be displayed as completed analysis. This feature does not add a DEMATEL execute control or silently change this compatibility behavior.

An execution reads persisted state when it obtains the lock. Separate browser PATCH and POST requests are not a single server transaction and are not a revision guarantee. Concurrent edits/removal/deletion serialize against the case row; no result mixes input states. Same-case explicit concurrent POSTs may each append a record once eligible; the product's client token prevents overlapping attempts only for that client flow.

## Existing response envelope

`id`, `method`, `input_snapshot`, `result`, `extracted_at`, `extracted_by`, `extracted_by_name`, `created_at` remain the serialized fields. Method identifies one analysis. Parent/project binding comes from the scoped URL; the envelope currently does not expose `case_id` or `project_id`, and none is required by this design.

`input_snapshot` retains title, ordered criteria/alternatives, selected methods, raw weights/types/performance matrix and all method matrices already stored. Ranking executions add engine-produced `weights_normalized`. Keep raw unrelated draft values under existing contracts, including ISM root JSON null. `result` follows [result review](result-review.md). Actor display name may change with the account; recorded actor identity and extraction time do not.

Client mutation parsing must reject empty/non-JSON/truncated bodies. A newly completed response must also have nonempty ID, expected method, readable execution time and actor identity, required frozen method input, and a valid completed output before callbacks or release. Capture the expected existing case ID for save validation; create accepts a new nonempty returned ID. Case guards validate consumed metadata without treating unfinished/raw drafts as executable inputs. An unconfirmed save returns a recoverable request failure and sends zero POSTs.

## List and detail read contract

History parameters: optional `method` in `{saw,topsis,ahp,dematel,ism}`, `page` and `page_size` (existing `per_page` alias retained). Omit `method` for all methods. Unknown method is rejected before pagination. Default size 50, maximum 100; frontend asks for 10. Preserve the existing page-number envelope `{count,next,previous,results}` and invalid-page behavior.

Apply `order_by('-extracted_at','-id')` before pagination. `count` reflects the scoped filtered set, including old placeholder records. Stable order is guaranteed for a fixed record set only. Resolve initiating user efficiently using the existing `select_related`; no new per-row lookup is intended.

Read response guards are local to Decision Support: count is a nonnegative integer; next/previous have existing null/string shapes; results is an array of rows with usable stable IDs, recognized methods and readable provenance. Result/input content may be partial historical data and is classified, not presumed complete. Detail ID must match the selected row; unusable top-level envelope is a read failure, not a fabricated analysis. Partial/missing snapshot or output within a usable record is handled by unavailable sections and safe provenance. Invalid reads never trigger execution.

## Ambiguous execution outcomes and recovery

After POST starts, network loss or an unusable success response may follow a commit. No automatic POST retry is permitted. Keep the captured-case token until one validated history lookup settles, or ten seconds expires and its request is aborted. Recovery reads unfiltered page one with `page_size=10`, explicit no retries and forced fresh data. Success selects this cached view only for the still-selected case and exposes rows/count; other cases remain unaffected. Failed/malformed GET or timeout gives explicit unresolved feedback before manual retry is available.

Recovered page one is inspectable history, not an idempotency certificate. A missing row does not prove no commit; late completions or concurrently appended rows may require normal browsing. Controlled acceptance scenarios must verify the committed ID appears in the recovered view before retry. A manual retry is another request and can append another record.

## Required backend acceptance slices

- All live engines: stale caller after inputs/selection change, deleted parent, independent output, zero append on invalid input, repeated valid append, raw/normalized snapshot equality and old-run full equality.
- Actual PostgreSQL contention: separate connections, synchronized lock holder/waiter, observed lock wait, authoritative released state; include targeted PATCH and soft-delete races. No elapsed-sleep-only lock proof.
- Fixed UUID/time fixtures across multiple pages and methods: exact order, correct count, every ID once; unknown method and invalid page cases.
- Existing membership/view/edit/admin and cross-project/case reads/mutations; immutable PUT/PATCH/DELETE; preserve corrupt-parent scoping regressions and matrix-only unrelated draft compatibility.
