# Contract: Test-Only Reference Verification

## Boundary and invocation

No public endpoint, library function or UI is added. Implemented internal invocation, from `apps/api/core`, is:

```text
../.venv/bin/python -m pytest decision_support/reference_tests -q --ranking-reference-report=/absolute/path/to/validation-reference.json
```

The sibling `conftest.py` registers this optional report path and records observations/test results. Ordinary pytest exit semantics remain authoritative: failures or incomplete selection cannot be converted to success by report writing. Existing test configuration/settings apply; tests request no database fixture/marker or unblocking. A no-write/blocker assertion must make unintended DB access fail.

## Authenticated extraction

1. Read the repository's implementation Python fence, identified by the original import and function, not the signature-only fence. Missing/duplicate eligible fences fail.
2. Independently read original DOCX XML with zipfile/XML facilities; identify the unique source paragraph, preserve text, LF breaks and tabs. Permit only one fence separator LF difference.
3. Require reviewed identities from research.md and exact source equality. Verify expected top-level import and five-argument callable shape before test-local evaluation.
4. Evaluation uses the authenticated reference only, never dynamic external text or an import of product calculations. Production code cannot import this helper. AST checks supplement pinned identity, not a general execution sandbox.

Reference signature is `rank_options(criteria, alternatives, weights, types, matrix)`. Its result has exactly method keys `SAW` and `TOPSIS`, each with ordered rows containing `option`, `SAW`, `TOPSIS`. Validate both scores per row against the corresponding alternative expectations, including repeated scores across lists. It has no numeric rank or returned distances.

## Required valid catalog

| Case/family | Ordered inputs and independent expected outcome |
| --- | --- |
| Published mixed | Equal weights, benefit/cost, A `[10,100]`, B `[5,200]`: SAW 1/.5 and TOPSIS 1/0, both A→B. Preserve original Persian labels from the acceptance example. |
| 1×1 | Positive criterion/cell/weight: SAW 1, TOPSIS .5. |
| 2×3 | Weights `[2,3,0]`, benefit/cost/benefit, A `[10,100,5]`, B `[5,200,10]`: SAW 1/.5, TOPSIS 1/0. |
| 10×10 | Benefit columns, weights 1–10, input row i repeats value i for i=1…10: SAW i/10, TOPSIS (i−1)/9, both reverse input order. |
| Cost-only | One cost column A=10/B=20: SAW 1/.5, TOPSIS 1/0, A→B. |
| Benefit-only with zero | One benefit column A=0/B=10: SAW and TOPSIS 0/1, B→A; legitimate zero differs from missing. |
| Exact ties/constant columns | Identical positive rows, distinct EN/FA labels: SAW 1, TOPSIS .5; input order. Permute alternatives/rows consistently and expect the permuted tie order. |
| Proportional weights | `[2,3]` and `[20,30]` on the same mixed example retain its literal outcomes and order. |
| Genuine disagreement | Weights `[21,10]`, benefit/benefit, A `[10,1]`, B `[6,5]`: SAW A=23/31, B=113/155 (A→B). TOPSIS A=`21√26/(21√26+10√136)`, B=its complement (B→A). This analytical expression is independent of engine output. |

Every valid case compares reference and both independent methods against expectations, then against each other. Require finite scores, `abs(actual-expected) <= 1e-9` with relative tolerance zero, exact labels/membership/order, no duplicate/missing rows and unchanged input. Tolerance never groups near-equal scores into ties. Product score/closeness aliases, normalized weights, ordinal ranks and TOPSIS distances are product-specific assertions, not reference fields.

## Rejection and representation catalog

Cover zero and >10 criteria AND alternatives, short/long weights/types, short/long row count and width, blank/duplicate criteria AND alternatives, invalid type, empty/null/nonnumeric/negative/non-finite weight or cell, all-zero weights, zero cost and all-zero benefit columns (including zero-weight column). Supply separate cases rather than letting an earlier error hide each category. Product checks require expected code/path from the current validators and method mapping, not exact messages. Reference rejection can be ValueError or TypeError; unexpected programming errors fail the harness.

Representation probes are separately classified: numeric text accepted by both current layers; boolean matrix cell accepted by sample but rejected by product; boolean weight currently converted by both; raw-versus-trimmed duplicate names; None name; trimmed criterion type. Characterize established behavior without declaring a new policy. Huge finite arithmetic and extreme tiny values are documented excluded-domain limitations, not ordinary score parity or grounds to repair the preserved sample.

## Reporting and falsification

`validation-reference.json` uses schema version 1 and the EvidenceRun/VerificationCheck fields in data-model.md. Serialize finite observations normally and tagged non-finite inputs; use strict JSON without NaN literals. Record source identity, dirty hashes, command/exits, expected and observed outcomes, status and evidence level. The required_check_ids manifest must exactly match checks; explicit file selection cannot omit registered falsification requirements. Strict reading rejects missing/duplicate IDs and invalid passing phase records. Tests/helpers can register required cases and capture observations before assertions; final pytest report status must downgrade failures including setup/teardown errors. Reports do not change exit status and missing observations remain unrun.

Pytest phase bookkeeping is stored separately from observations. Passing phases alone, empty helper events and phase-only observation objects cannot produce a passing check: actual helper outcomes or explicitly recorded behavior are required. Fixture invariants, the database blocker and the uncollected-check registry record their inputs, expectations and actual outcomes explicitly. Failures remain failed even when observations are unavailable.

The reader requires a timezone-aware UTC generation time, a hexadecimal Git SHA, a nonempty map of repository-relative source paths to SHA-256 values, all three pinned reference identities, nonempty Python/Django/DRF/pytest versions, command arguments and the `apps/api/core` working directory. Run/check evidence levels must be `arithmetic` and `product_browser_acceptance` must be false. Missing or malformed required provenance/levels are rejected. Schema and exit values must be actual integers, not JSON booleans. These checks validate report structure and attribution; verifying reuse still requires comparing recorded hashes with the applicable current sources/artifacts. Legitimate partial reports remain readable with explicit unrun observations and complete=false.

Falsification tests use temporary/in-memory inputs to reject changed source text (including messages/comments), source/fence/shape drift, duplicate/missing identities, wrong exact tie order, score error above tolerance, non-finite output, and failed/unrun checks misreported as passing. A malformed report cannot count as acceptance. No mutation of authoritative DOCX/Markdown is permitted.
