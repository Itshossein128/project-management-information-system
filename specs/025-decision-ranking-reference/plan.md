# Implementation Plan: Verifiable Decision Ranking Reference

**Branch**: `develop` | **Date**: 2026-10-13 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/025-decision-ranking-reference/spec.md`

Setup resolved `FEATURE_SPEC`, `IMPL_PLAN` and `FEATURE_DIR` to this feature. Its JSON `BRANCH` was `025-decision-ranking-reference`: the installed script uses the feature identifier as its fallback, rather than inspecting Git. Actual Git branch is `develop`; no branch switch is required.

## Summary

Add test-only verification that extracts the preserved ranking sample, checks it against independently pinned original-source fingerprints, and compares it with the existing independent SAW/TOPSIS engines. Literal analytical cases cover scores, exact order, dimensions, ties, weight invariance and rejection rules. A structured evidence ledger and six-category difference record distinguish sample arithmetic from existing product execution, storage and interaction.

The existing engines, endpoints, models, validators and interface are reused. No production change is planned unless a new comparison reproduces a requirement violation. Preserve original source/reference documents, earlier feature artifacts, open final policies O01/O02 and unrelated dirty work. Use TDD for new verification behavior and any demonstrated defect; existing correct behavior is regression evidence, not artificially forced red.

## Technical Context

**Language/Version**: Existing API Python 3.12.3; pinned Django 4.2.11. Source inspection also verified DRF 3.17.1 and pytest 9.1.1 in the API environment. Existing web uses TypeScript/React Router; no web change planned.

**Primary Dependencies**: Existing pytest/pytest-django and independent `compute_saw`/`compute_topsis`; standard-library pathlib, hashlib, zipfile, XML parsing, ast and math. No dependency installation or upgrade. Source documents are repository fixtures, not external network inputs.

**Storage**: Test fixture literals and feature-local JSON/Markdown evidence. No application schema or migration. Pure reference checks must remain database-blocked; separate existing product tests use PostgreSQL test data. Redis is required for normal API/browser operation.

**Testing**: New sibling suite `apps/api/core/decision_support/reference_tests/`; existing core pytest configuration. Reuse selected engine, validator, method API, immutability and access tests. Reuse attributable unchanged EN/FA browser evidence or rerun applicable browser cases; fresh bilingual browser proof is mandatory for any changed interaction.

**Target Platform**: Existing local Linux development/test environment. API venv is `apps/api/.venv`; root `.venv` is Spec Kit. No Docker, RabbitMQ, MinIO, production mutation or network reference fetch is needed.

**Project Type**: Verification tooling inside the existing web/API monorepo; no new application, public callable or user-facing code runner.

**Performance Goals**: None added. Matrices remain at most ten alternatives by ten criteria. This feature verifies numerical meaning and traceability, not latency; prior performance results are outside its new acceptance claim.

**Constraints**: Preserve exact sample text/messages and DOCX; authenticated test-only extraction before execution; finite score checks; absolute tolerance `1e-9`, relative tolerance zero; exact names/membership/order; no approximate tie grouping; no new numeric-input or display policy. Rejection messages need not match between reference and product.

**Scale/Scope**: Four stories, 16 acceptance scenarios, 14 FRs and six SCs. Ordinary parity cases use numbers in `[0,1000]`, nonzero values at least 0.1. Required families include 1×1/2×3/10×10, criterion direction, zero/unequal/scaled weights, ties, degeneracy and disagreement; invalid categories and representation differences are separate.

## Constitution Check

*Pre-research gate: PASS. Post-design gate: PASS. No exception requested.*

| Principle | Design and verification gate |
| --- | --- |
| I: Authorization/isolation | No new external read/write surface. Pure suite blocks DB access; existing API access and project-scoping checks remain acceptance evidence. |
| II: Integrity | No models/schema change. Original records and source files preserved; existing API full-record equality and immutable-route checks reused. |
| III: Bilingual behavior | Unchanged EN/FA interfaces and identifiers remain; fixture labels cover both languages. Any changed feedback requires fresh actual EN/FA browser evidence. |
| IV: Safe mutations | Reference execution accepts only pinned repository text and performs no project writes. Product checks use prepared local/test cases; no resets or production acceptance actions. |
| V: Minimal changes | Add only test-side loader, fixtures, checks/reporting and feature-local evidence. Reuse engines and product contracts; defects require a failing behavioral check before a minimal fix. |
| VI: Evidence | Capture meaningful harness/fix red and green; reference, API, browser and reused evidence are distinct. Record dirty source hashes and unrun/failed statuses, not checkbox-only completion. |
| VII: Accessibility | No new UI. Existing keyboard checks are attributable regressions; changed interactions require fresh keyboard verification in both languages. |

Architecture and quality constraints: preserve Django 4.2, pnpm boundaries and existing fixture scope; no default dependency, schema or locale changes. If implementation discovers a necessary production change, trace affected surfaces and rerun appropriate final-tree checks. Source inspection is a planning baseline only.

## Project Structure

### Documentation (this feature)

```text
specs/025-decision-ranking-reference/
├── spec.md
├── checklists/requirements.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── reference-verification.md
│   └── existing-product-boundary.md
├── tasks.md                    # future speckit-tasks output
├── validation.md               # future implementation evidence/reconciliation
├── differences.md              # future six-category explanation
├── validation-reference.json   # future machine-readable reference evidence
└── evidence/                   # future commands, exits, red/green and reused provenance
```

### Source Code (repository root)

```text
apps/api/core/decision_support/
├── reference_tests/                     # proposed, database-blocked sibling suite
│   ├── conftest.py                       # reporting option and case observations
│   ├── ranking_reference_fixtures.py      # pinned identity, literal cases/expectations
│   ├── ranking_reference_support.py       # extract, authenticate, observe and compare
│   ├── test_ranking_reference.py          # fidelity, parity, rejection, differences
│   └── test_ranking_reference_harness.py  # discrepancy/failure detection tests
├── services/{saw_service,topsis_service,weights,validators}.py  # existing, reused
└── tests/                               # existing DB-backed product checks, preserved
apps/web/e2e/tests/decision-execution-records.spec.ts            # existing EN/FA evidence
```

**Structure Decision**: A sibling suite avoids `decision_support/tests/conftest.py`'s autouse DB catalog seeding. Core settings can initialize normally while pytest-django keeps connections blocked. Keep helper imports test-local, with no runtime dependency from services/views/browser code. The test reporter is an internal pytest interface; contracts below document it and unchanged product boundaries, not a new external API.

## Phase 0: Research decisions

[research.md](research.md) resolves extraction, source identity, no-DB placement, independent expectations, representation differences, evidence provenance and TDD approach. Two read-only research agents were dispatched as required by the planning skill. No unresolved design question or constitution failure remains.

## Phase 1: Design and implementation sequence

1. Pin source identity and literal comparison cases; define the observation/report contract before tests. Extract Markdown and DOCX independently and authenticate before compiling only the trusted sample.
2. Test new harness decisions first: changed text/source, missing/wrong implementation fence, altered callable shape, missing/duplicate result, wrong order, non-finite/out-of-tolerance score and failed/unrun report status. Use memory/temporary fixtures; authoritative files never become mutation targets. Reject expected assertion/import failures as acceptance evidence.
3. Add the valid/invalid/representation catalog checks, then the smallest loader/comparator/reporting implementation that makes the verification behavior pass. Existing engines may already pass parity; that is legitimate green regression, not a reason to alter formulas. Keep reference and product observations independent.
4. If a real product mismatch appears, retain input and observed red, establish expected behavior using source formulas and independent expectations, minimally fix only the violated contract, then rerun focused and affected product regressions. A failed check is never reclassified as intentional solely to reach green.
5. Reuse named product tests for independence, full-record immutability, access and error paths. Reuse old browser evidence only after scenario/source/artifact provenance review; otherwise run selected existing EN/FA cases. Avoid old SC004 timing tests that rewrite feature-024 artifacts.
6. Produce feature-local differences, structured observations and full FR/SC/acceptance reconciliation, preserving earlier evidence and all source documents. Unavailable checks remain explicit incomplete gates.

See [data-model.md](data-model.md), [reference contract](contracts/reference-verification.md), [product boundary](contracts/existing-product-boundary.md) and [quickstart.md](quickstart.md). Tasks and implementation are later commands.

## Complexity Tracking

No constitution violations or additional runtime architecture. Test-side extraction/reporting is necessary to verify preserved content and real observed comparisons without a duplicate production engine.
