# Feature Specification: Verifiable Decision Ranking Reference

**Feature Branch**: `develop` (unchanged; feature directory is `specs/025-decision-ranking-reference`)

**Created**: 2026-10-13

**Status**: Draft

**Input**: User description: `docs/decision-support/09-ranking-reference.md`

**Authoritative sources**: [ranking reference](../../docs/decision-support/09-ranking-reference.md), [independent method scope](../../docs/decision-support/01-module-scope.md), [ranking inputs](../../docs/decision-support/02-decision-inputs.md), [SAW](../../docs/decision-support/03-saw.md), [TOPSIS](../../docs/decision-support/04-topsis.md), [execution records](../../docs/decision-support/08-execution-records.md), [acceptance checks](../../docs/decision-support/10-acceptance-checks.md), and [source review and open decisions](../../docs/decision-support/11-source-review.md).

Reviewers need to establish what the preserved ranking sample demonstrates and whether the product's independent results agree with it. This feature supplies repeatable reference verification and records intentional differences. It preserves working calculations and the editable source sample; it does not introduce another calculation product or require both methods to run together.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inspect a Faithful, Usable Reference (Priority: P1)

As a decision-support reviewer, I can locate the original editable sample, understand its ordered inputs and method-specific outputs, and reproduce its published example without confusing it with the product workflow.

**Why this priority**: A comparison is useful only when the reference's identity and actual behavior are clear.

**Independent Test**: Inspect the reference and its attribution, evaluate the published example, and record both results without changing the sample.

**Acceptance Scenarios**:

1. **Given** the preserved document and original source, **When** a reviewer inspects the sample, **Then** its text, calculations and messages remain unchanged from the baseline, remain editable text, and retain source attribution.
2. **Given** ordered criteria, alternatives, weights, criterion types and a performance matrix, **When** the reference is reviewed, **Then** criterion order matches weights, types and columns, alternative order matches rows, and its two separately sorted results are described as containing both method scores per alternative and no numeric rank or returned distances.
3. **Given** the published experience/price example with alternatives A/B, equal weights and rows `[10, 100]` and `[5, 200]`, **When** the reference is evaluated, **Then** SAW scores are A=`1.0`, B=`0.5`, TOPSIS scores are A=`1.0`, B=`0.0`, and both orders are A then B.
4. **Given** the sample's limitations, **When** product readiness is reviewed, **Then** the review identifies that the sample supplies neither independent execution, other methods, a data-entry form, saved history, numeric ranks, returned TOPSIS distances, nor field/cell-located product errors; reproducing it alone is not recorded as product acceptance.

---

### User Story 2 - Compare Independent Ranking Results (Priority: P1)

As a reviewer, I compare each existing ranking method with the preserved sample on reproducible cases and identify numerical or ordering disagreements before accepting a change.

**Why this priority**: Reference agreement protects the meaning of existing decisions without duplicating working functionality.

**Independent Test**: Evaluate identical valid cases through the reference and each independent product method. Compare each alternative's score and each method's order, including mixed criteria and exact ties.

**Acceptance Scenarios**:

1. **Given** valid cases at `1 × 1`, `2 × 3` and `10 × 10`, **When** each method is compared with its reference result, **Then** all alternatives appear exactly once, names and order agree exactly, and corresponding scores meet FR-005's tolerance.
2. **Given** benefit-only, cost-only and mixed-criterion cases, unequal weights and a valid zero-weight criterion, **When** scores are compared, **Then** each method agrees with its reference result and criteria are not reordered or omitted.
3. **Given** weights `[2, 3]` and `[20, 30]` on otherwise identical valid data, **When** each method is evaluated, **Then** scores remain equal within the comparison tolerance and alternative order remains unchanged.
4. **Given** a single valid alternative or identical valid rows, **When** TOPSIS is evaluated, **Then** its score is `0.5`; exact score ties preserve input alternative order in both methods. Reordering tied alternatives changes their output order to the new input order without inventing a numerical preference.

---

### User Story 3 - Distinguish Invalid Inputs from Reference Limitations (Priority: P1)

As a reviewer, I see which inputs must be rejected and which behaviors intentionally differ, so sample conversion or arithmetic limitations are not mistaken for the product validation contract.

**Why this priority**: An incorrect successful result is more harmful than a clearly identified invalid input or bounded reference limitation.

**Independent Test**: Check the invalid categories below, compare rejection outcomes, and distinguish the sample's errors from product feedback without requiring identical wording.

**Acceptance Scenarios**:

1. **Given** zero or over-limit dimensions, mismatched vector/row lengths, blank or duplicate names, or an unsupported criterion type, **When** reference and product validation are checked, **Then** neither yields an accepted ranking and evidence identifies the violated rule.
2. **Given** missing, nonnumeric, negative or non-finite values, negative or all-zero weights, a zero cost value, or an all-zero benefit column even with zero weight, **When** these cases are checked, **Then** no successful ranking is accepted; the product identifies the affected field or cell according to its existing contract.
3. **Given** sample conversions that accept numeric text or values outside the product's accepted representation, **When** the difference is reviewed, **Then** it is classified as a representation difference rather than a calculation mismatch, and product validation is not loosened to imitate it. Identical error text is not required.
4. **Given** very large finite values that can exceed safe sample arithmetic, **When** numerical claims are reviewed, **Then** the limitation and unresolved numeric-domain decision are explicit; no universal finite-number correctness or new numeric-domain policy is asserted.

---

### User Story 4 - Review Product Differences and Acceptance Evidence (Priority: P2)

As a decision maker, I distinguish verified arithmetic from the product's additional safeguards and outputs, and know which behavior has actually been checked.

**Why this priority**: Transparent evidence prevents the sample from justifying coupled execution or overstated completion.

**Independent Test**: Review the difference record and applicable existing evidence, then check SAW-only and TOPSIS-only execution and unchanged earlier history through the established product experience.

**Acceptance Scenarios**:

1. **Given** valid manual weights and only SAW or only TOPSIS requested, **When** that method executes, **Then** the other method is neither required nor executed and only the requested result is recorded. Separately requested methods retain distinct results even when their orders disagree.
2. **Given** normalized weights, interim ordinal ranks and TOPSIS best/worst distances in product results, **When** results are compared with the sample, **Then** these are identified as existing product additions; O01/O02 remain open as final policy, with existing display precision and tie behavior preserved.
3. **Given** saved records and established access restrictions, **When** reference verification runs, **Then** earlier inputs and results remain unchanged, reference-only checks create no project history, and no new access to protected data is introduced. Product checks use authorized prepared cases.
4. **Given** completed and outstanding checks, **When** evidence is reviewed, **Then** each names its input, expected and observed outcome, status and evidence level. Arithmetic, execution/record and English/Persian interaction checks are distinguished; unrun checks are not reported as passed. Any changed product feedback remains localized and keyboard-accessible.

### Edge Cases

- The sample calculates both methods and repeats both scores in each sorted list; compare a method's own score and order, not the other method or an assumed numeric rank.
- Zero-weight criteria still undergo validation. An all-zero benefit column remains invalid even with zero weight.
- Constant positive columns and identical valid rows differ from invalid all-zero columns.
- Stable ordering concerns exactly equal scores. Scores within the comparison tolerance are not automatically ties or assigned shared ranks.
- English and Persian alternative labels survive comparisons unchanged. Cases use unambiguous unique labels without deciding unresolved normalization rules.
- Independent SAW and TOPSIS can disagree; preserve both orders without assuming universal superiority of either method.
- Product ranks and TOPSIS distances have no sample counterparts. Score parity alone cannot prove those additional outputs correct.
- Very large or extremely small numbers and locale/text conversions are outside ordinary numeric parity cases; documented limitations and established product policy remain in force.
- A broken reference, missing case or unavailable product check is incomplete evidence, never a passing comparison.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The sample MUST remain unchanged, attributed and available as editable text in its existing document. Verification MUST detect a change rather than silently substituting product calculations (US1.1).
- **FR-002**: Its description MUST accurately identify the five ordered inputs, normalized weighting, two separately sorted results, repeated scores and absence of numeric ranks and returned distances (US1.2).
- **FR-003**: The published mixed benefit/cost example MUST reproduce US1.3's scores and orders for the sample and corresponding product methods (US1.3, US2.1).
- **FR-004**: Repeatable comparisons MUST cover all valid families in US2.1–US2.4 using identical inputs and compare each alternative's corresponding method score, completeness and exact method-specific order. Product-only fields MUST NOT be treated as missing sample fields.
- **FR-005**: Score comparisons MUST accept an absolute difference of at most `1 × 10^-9` for the bounded cases in Assumptions. Names, membership and ordered identity MUST match exactly. This verification tolerance MUST NOT change calculation, rounding, display precision or tie policy (US2.1–US2.4).
- **FR-006**: Positive proportional weight rescaling MUST preserve scores within the tolerance and preserve order; valid zero-weight criteria MUST remain validated (US2.2–US2.3, US3.2).
- **FR-007**: Exact ties MUST retain input alternative order, and zero-total-distance TOPSIS cases MUST yield `0.5`, consistent with existing interim behavior (US2.4).
- **FR-008**: Rejection evidence MUST cover every invalid category in US3.1–US3.2, including empty versus zero values and zero-weight all-zero columns. Product feedback MUST retain its existing field/cell location without requiring matching sample locations or messages.
- **FR-009**: Verification MUST distinguish calculation disagreements from intentional representation and error-presentation differences; sample conversions MUST NOT become a new product input contract (US3.3).
- **FR-010**: Evidence MUST identify arithmetic limitations and exclusions without implying correctness for all finite values or resolving open numeric-domain policy (US3.4).
- **FR-011**: Independent execution, separate results, explicit manual weights and saved-record immutability MUST remain intact. Combined sample behavior MUST NOT become a prerequisite, blended ranking or automatic weight transfer (US4.1, US4.3).
- **FR-012**: A difference record MUST identify six categories: normalized weights; interim numeric ranks; recorded TOPSIS distances; located/localized errors; independent execution; and saved history. It MUST keep O01/O02 open as final policy and preserve existing output/display behavior (US1.4, US4.2).
- **FR-013**: Reference-only verification MUST NOT mutate cases/history or expose protected data. Product checks MUST retain existing access controls; any changed user interaction MUST work in English and Persian with the keyboard (US4.3–US4.4).
- **FR-014**: Evidence MUST record each case's input, expected outcome, observed outcome or explicit unrun status, pass/fail status where run, and evidence level. Relevant existing evidence MAY be reused when its inputs and behavior still apply; arithmetic alone MUST NOT substitute for interaction or persistence acceptance (US4.4).

### Key Entities *(include if feature involves data)*

- **Preserved Ranking Reference**: The attributed, editable original sample, its input/output description and documented limitations; distinct from product execution.
- **Comparison Case**: Named ordered inputs, valid-case family or invalid rule, expected scores/orders or rejection, and any intentional difference. Examples do not become fixed alternatives in user cases.
- **Verification Evidence**: Observed reference/product outcomes, per-method comparison status and evidence level, linked to the case and requirement.
- **Difference Record**: Distinctions between sample behavior, existing interim product behavior and unresolved final decisions; creates no new final policy.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Review confirms zero changes to the sample's text, calculations and messages and verifies all five inputs and both output descriptions against actual behavior (FR-001–FR-002).
- **SC-002**: The published example and 100% of required valid families match corresponding scores within `1 × 10^-9`, with exact membership, names and method-specific order; exact-tie and TOPSIS `0.5` cases pass (FR-003–FR-007).
- **SC-003**: Every invalid category in US3.1–US3.2 has a rejection check, zero accepted rankings, and locatable product feedback where applicable. Representation differences and arithmetic limitations are explicitly classified (FR-008–FR-010).
- **SC-004**: SAW-only and TOPSIS-only checks create zero unrequested-method runs; separate-method checks produce zero blended ranks or automatic weight changes. Reference-only checks change zero cases or records (FR-011, FR-013).
- **SC-005**: A reviewer can account for all six FR-012 difference categories without attributing product-only fields to the sample or treating O01/O02 as closed; existing interim ranking/display behavior remains unchanged (FR-012).
- **SC-006**: 100% of required checks identify the case, expected outcome, observed outcome or unrun status, and evidence level. Any changed product interaction passes both English and Persian keyboard checks, with zero protected disclosures or prohibited writes; outstanding checks remain explicitly incomplete (FR-013–FR-014).

## Assumptions

- Document 09 selects the reference responsibility. It requests no end-user code editor, second ranking engine, combined execution interface or downloadable calculation service. The existing editable document is the reference surface.
- Source inspection shows independent SAW/TOPSIS calculations, method checks and shared records already exist. This is a planning baseline, not fresh behavioral acceptance. Planning must identify missing reference verification and reuse working capabilities and applicable evidence before proposing changes.
- Dependencies are the [case shell](../018-decision-case-shell/spec.md), [SAW](../019-decision-saw/spec.md), [TOPSIS](../020-decision-topsis/spec.md), [execution records](../024-decision-execution-records/spec.md) and source documents above. An unavailable check does not authorize rebuilding earlier features.
- Ordinary valid parity cases use numeric weights and performance values from zero to 1,000, nonzero values at least 0.1, positive cost values and a positive weight sum. Required dimensions and criterion/weight families are covered; one case may cover several families. These bounds and the comparison tolerance define verification examples, not new user-input limits or a universal precision guarantee.
- Blank, duplicate and unambiguous names are tested without altering existing normalization or localized numeric-input policies. O03/O04 remain with the owning input specification and source review; sample conversions do not override the accepted product contract.
- O01/O02 remain open as final policy. Preserve score-descending order, exact-tie input stability, one-based ordinal product ranks, recorded TOPSIS distances and current display precision; do not introduce shared ranks or rewrite historical values.
- Numerical checks need no project mutation; product checks use authorized prepared cases and existing permissions/record protections. No new public access is inferred. Evidence categories remain distinct, and unchanged interactions can use applicable prior evidence.
- The original source, preserved reference, related documents and earlier specifications are not rewritten by this feature. Difference explanations may accompany verification evidence. Other method implementation, new numeric-domain policy, automatic weight transfer, import/export, diagrams, full-module usability sign-off and new performance guarantees are excluded.
