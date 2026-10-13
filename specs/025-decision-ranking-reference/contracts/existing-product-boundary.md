# Contract: Existing Product Boundaries and Evidence

Feature 025 adds no endpoint, model, migration, permission, method-selection rule or UI. Existing project-scoped case/run routes continue to use established view/edit permissions, independent requested-method execution and immutable recorded input/output. Do not import the reference helper into a production path.

## Reusable named checks

| Boundary | Existing check(s) | Evidence limit |
| --- | --- | --- |
| SAW only | `test_saw_api.py::test_ac01_ac14_saw_only_run` | Real requested-method run; no TOPSIS prerequisite/run. |
| TOPSIS only | `test_topsis_api.py::test_ac01_ac15_topsis_only_run` | Real requested-method run; product score, rank and distances. |
| Independent records | `test_topsis_api.py::test_ac03_ac25_saw_and_topsis_independent` | Distinct method histories, not a blended result. |
| Disagreement/ties/no transfer | `test_execution_records.py::test_independent_disagreement_ties_and_deselection` | Actual computed disagreement, whole case equality, ordinal tie policy. |
| Old-record integrity | SAW/TOPSIS `test_ac23_ac24_*_immutability`; `test_runs_immutability.py::test_distinct_append_full_immutability_and_zero_rejection` | Stored snapshot/result/full-row equality; failed attempts append no success. |
| Access/isolation | `test_execution_records_access.py::test_real_access_nested_scope_immutable_and_revocation` | Viewer read/denied writes, nested foreign/revoked/anonymous/nonmember denial. |
| Located errors | `test_validators.py::test_ac26_api_empty_cell_path`; existing invalid method API cases | Product issue path; message/code identity across engines/reference is not required. |
| EN/FA keyboard/access | Browser `real viewer access keyboard ten axes dates and revoked read` | Actual localized viewer interaction, keyboard selection, revoked reads. |
| EN/FA historical review | Browser `frozen named ranking review leaves current result and live draft unchanged`; `independent disagreement ties and deselection retain stored results without writes` | Read-only presentation; fixture-created disagreement does not prove calculation. |
| EN/FA feedback | Browser `named ranking feedback and no-match history are distinct` | Named validation feedback in each language. |

Backend paths are under `apps/api/core/decision_support/tests/`; browser names are in `apps/web/e2e/tests/decision-execution-records.spec.ts`. Pair browser presentation with actual engine/API checks. Select tests by existing exact names; do not duplicate runtime orchestration or broaden to unrelated method implementation.

## Six-category difference record

| Category | Reference | Existing product behavior to preserve |
| --- | --- | --- |
| Normalized weights | Used internally, not returned separately | Recorded normalized weights alongside raw inputs. |
| Numeric ranks | Only sorted order | Interim one-based ordinal ranks; exact ties preserve input order. |
| TOPSIS distances | Computed internally, not returned | Recorded/displayed best and worst distances, method-specific result. |
| Errors | Plain exceptions/conversion errors | Located issues and established localized feedback; representation conversions may differ. |
| Execution | Calculates both methods per call | One requested method independently; other methods are not prerequisites. |
| History | No persistence/provenance | Authorized distinct saved records with frozen inputs/results, initiator and time. |

O01/O02 remain open as FINAL policy. Preserve current display precision, ordinal ranking and output shape; no shared ranks, rounded-score reordering, automatic transfer or old-record rewrite. Three other methods are not implemented by the sample and are outside feature 025's calculation work.

## Reuse acceptance

For old evidence, record artifact path, named scenario, actual date/environment/command and relevant source fingerprint comparison against its manifest. Check artifact exists and scenario really passed. A Git HEAD alone cannot identify this dirty workspace. If any relevant source changed, provenance is missing or scope differs, rerun the applicable check. Retain reused evidence references without rewriting earlier reports.

Existing feature-024 validation/evidence files are candidates, not new planning acceptance. Fresh API regressions are preferred during implementation. Existing browser evidence may be reused for unchanged interactions only with the checks above; any changed interaction requires fresh real EN/FA keyboard verification. Do not select old SC004 timing cases, which write earlier performance artifacts.

Reference-only checks must query/write zero protected project data. DB-backed regression tests use pytest-managed data; browser checks use prepared disposable local projects and unchanged authenticated setup. No development database reset or production mutation is part of validation.
