# Research: Verifiable Decision Ranking Reference

Research uses the current repository and installed environments. No application tests ran during planning. All choices below resolve the design unknowns; package upgrades and external algorithm recommendations are not part of this feature.

## 1. Reference fidelity and trust

**Decision**: Extract the actual implementation fence (not the earlier signature fence) from document 09, and independently extract the DOCX paragraph containing the original `from math` sample. Pin the DOCX bytes and extracted text digests as reviewed constants in test fixtures. Require equality before executing the reference in a test-local namespace.

**Rationale**: Read-only extraction found 91 lines, 3,722 Unicode characters and exact equality when only the Markdown block's single terminal separator LF is removed. Mapping DOCX `w:t` to text, `w:br`/`w:cr` to LF and `w:tab` to tab preserves whitespace and messages. Ordinary `.strip()` would hide source drift.

Reviewed SHA-256 values:

| Identity | Digest |
| --- | --- |
| Original `docs/document (10).docx` bytes | `52946a0ff62205bebf007eda3a6c860d5f010311194c3740316d6a2a2369e282` |
| Extracted original/sample UTF-8, without separator LF | `ae0f35b52bb9231d06cc416d1972f248257ec34dbf07fcd8658948ac55b83e26` |
| Markdown implementation block including separator LF | `8304307300aba81d18c8669d1e5d2d3ce3578df03498359528ad8ab2e25328db` |

Check the AST shape: one math import of `isfinite` and `sqrt`, one undecorated five-argument `rank_options` definition, no additional executable top-level statements. Authentication is the trust boundary; this is not a sandbox for arbitrary user code. Wrong source identity fails closed before evaluation.

**Alternatives considered**: A copied reference module creates another editable implementation. Deriving the expected digest from the current file during every run is circular. Rewriting or reformatting the sample defeats preservation. A generic code execution endpoint is outside scope.

## 2. Keep arithmetic verification free of database writes

**Decision**: Put new tests in `decision_support/reference_tests/`, use core pytest configuration, and retain pytest-django's database blocker. Import only the independent engines/validators, not the execution dispatcher. Add an explicit blocker/no-write assertion.

**Rationale**: Existing `decision_support/tests/conftest.py` has a session-autouse fixture requesting `django_db_setup` and seeding RBAC, plus transaction catalog restoration. Core `conftest.py` has an autouse in-memory cache override but only explicit database fixtures. A sibling directory avoids changing the established product suite.

**Alternatives considered**: New tests inside existing `tests/` trigger DB work even without a DB marker. Modifying its catalog fixtures risks prior concurrency tests. A standalone non-Django reimplementation duplicates validators and production semantics.

## 3. Independent numerical expectations

**Decision**: Use literal ordered fixtures with analytical expected outcomes, not goldens generated from product results. Compare both implementations against expected values and each other; finite guards precede absolute `1e-9` comparisons with zero relative tolerance. Check membership/order exactly.

**Rationale**: Agreement between two implementations alone can share an error. Required fixtures cover published mixed inputs, 1×1, 2×3 with unequal/zero weights, 10×10 monotonic rows, cost-only, benefit-only/zero cell, positive constant columns, exact ties/reordered labels, proportional weights and genuine method disagreement. Fixture details are in the reference contract.

**Alternatives considered**: Default approximate comparison can allow relative tolerance. Random cases alone obscure reproducibility. Score tolerance cannot redefine ties; rounded scores cannot establish raw arithmetic agreement. Universal finite-number claims exceed the source and ordinary bounded cases.

## 4. Rejection and representation differences

**Decision**: Record reference `ValueError`/`TypeError` conversion rejection and product `CodedValidationError` issue codes/paths separately. Use ordinary numeric inputs for parity; representation probes document actual layer-specific behavior.

**Rationale**: Current product accepts numeric strings in weights and matrix cells too. Sample-only numeric text acceptance must not be assumed. Concrete differences: sample accepts boolean cells via conversion, product rejects boolean matrix cells; product weight conversion still accepts booleans. Sample checks raw name uniqueness, product trims first and treats `None` as empty. Sample requires exact criterion type strings while product trims/stringifies them. SAW all-zero benefit errors and TOPSIS denominator errors intentionally have different product codes.

**Alternatives considered**: Aligning exception messages or loosening validation to match the sample changes policy. Blanket numeric-string rejection contradicts actual code. Very large finite overflow is a documented limit, not authorization to choose a new numeric domain.

## 5. Product checks and evidence reuse

**Decision**: Reuse named existing tests mapped in the product-boundary contract. New reference evidence is feature-local. Review source hashes, observation scope and artifact presence before attributing feature-024 browser evidence; mismatches or insufficient provenance require fresh applicable checks.

**Rationale**: The existing validation report records prior backend/Node/browser results, but planning has not run those suites. Product arithmetic, persistence and real interaction are different proof levels. A historic fixture-driven browser disagreement shows presentation, not calculation; pair it with actual backend execution.

**Alternatives considered**: Duplicating endpoints/UI is unnecessary. Copying a previous pass count without provenance overstates current proof. Rerunning the entire records performance suite can rewrite earlier evidence and adds a timing scope this feature does not require.

## 6. TDD and implementation boundary

**Decision**: Apply test-first discrepancy tests to new extraction/comparison/reporting behavior; use controlled temporary inputs for drift and bad observations. Preserve meaningful red/green for new behavior and any reproduced product defect. Existing passing engine tests remain regressions.

**Rationale**: A verification feature must demonstrate that it rejects wrong values and incomplete evidence; merely asserting equality on happy inputs is insufficient. Import/setup errors do not demonstrate a behavioral failure, and correct production formulas need no manufactured defect.

**Alternatives considered**: Checkbox-only TDD has no behavioral evidence. Mutating authoritative source documents or temporarily breaking production engines is unnecessary and risks unrelated dirty work. Implementing a general mutation framework adds speculative scope.
