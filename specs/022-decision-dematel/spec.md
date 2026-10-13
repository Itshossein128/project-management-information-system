# Feature Specification: Independent DEMATEL Criterion Influence Analysis

**Feature Branch**: `develop` (unchanged; no branch-creation hook configured)

**Feature Directory**: `specs/022-decision-dematel`

**Created**: 2026-10-11

**Status**: Draft — quality validated, ready for planning

**Input**: User description: `docs/decision-support/06-dematel.md`

**Source requirements**: [DEMATEL](../../docs/decision-support/06-dematel.md), [method independence](../../docs/decision-support/01-module-scope.md), [input contract](../../docs/decision-support/02-decision-inputs.md), [execution records](../../docs/decision-support/08-execution-records.md), [acceptance checks](../../docs/decision-support/10-acceptance-checks.md), and [open decisions O07–O09](../../docs/decision-support/11-source-review.md).

This feature lets authorized project members analyze how their criteria influence one another, identify prominent criteria and net influencing or receiving roles, and inspect historical results. It extends the existing Decision Support case and history experience. Its working policies are explicit assumptions, rather than claims that the source document settled its open decisions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run an Independent Influence Analysis (Priority: P1)

As a project member, I select DEMATEL, define my criteria, enter their directed influence judgments, and see each criterion's prominence and net influence without entering alternatives or running another method.

**Why this priority**: This is the primary value of DEMATEL and fulfills independent criterion analysis.

**Independent Test**: Use a criteria-only case with A, B, C and the matrix below; execute DEMATEL alone and compare the displayed criterion results with the reference values.

**Acceptance Scenarios**:

1. **Given** a DEMATEL case containing only criteria and a valid direct-influence matrix, **When** an authorized member executes DEMATEL, **Then** a distinct successful DEMATEL result appears without requiring alternatives, ranking weights, criterion benefit/cost types, a performance matrix, AHP, ISM, SAW, or TOPSIS (AC02).
2. **Given** criteria A, B, C and direct influences `[[0,4,0],[0,0,2],[0,0,0]]`, **When** DEMATEL executes, **Then** the total relations are `[[0,1,0.5],[0,0,0.5],[0,0,0]]`; D is `[1.5,0.5,0]`, R is `[0,1,1]`, prominence is `[1.5,1.5,1]`, and relation is `[1.5,-0.5,-1]`, all associated with A, B, C in that order (AC19).
3. **Given** distinct judgments for A→B and B→A, **When** either judgment changes, **Then** the other remains unchanged; self-influence entries are zero and cannot be edited to a nonzero value.
4. **Given** a valid matrix containing decimal influences within 0–4 and some zero influences, **When** DEMATEL executes, **Then** the values are accepted without rounding them to integers or treating zero as missing.
5. **Given** a mixed-method case with existing ranking inputs and other method results, **When** DEMATEL executes, **Then** it creates only its own result and leaves ranking inputs and other results unchanged (AC03–AC04).

---

### User Story 2 - Correct Inputs Without Misleading Results (Priority: P1)

As a project member, I need to know which influence judgment is invalid or why my matrix cannot be evaluated so I can correct it without mistaking an undefined calculation for a valid conclusion.

**Why this priority**: Invalid or undefined results would undermine the decision analysis.

**Independent Test**: Submit missing, malformed, out-of-range, all-zero, and singular examples; verify actionable feedback and no new successful result, then correct the matrix and execute successfully.

**Acceptance Scenarios**:

1. **Given** an empty, nonnumeric, nonfinite, negative, or greater-than-four influence, **When** the user attempts execution, **Then** execution stops and feedback identifies its row and column criteria; an empty entry is never substituted with zero (AC08, AC26).
2. **Given** zero or more than ten criteria, duplicate or blank criterion names, mismatched dimensions, or a nonzero diagonal, **When** execution is requested, **Then** validation identifies the affected field or matrix location and no successful result is recorded (AC06–AC07, AC12, AC22).
3. **Given** an all-zero matrix, including a one-criterion matrix `[[0]]`, **When** execution is requested, **Then** the user sees that at least one nonzero influence is needed to normalize the matrix; no synthetic zero-valued analysis is returned (AC20).
4. **Given** `[[0,4],[4,0]]`, **When** execution is requested, **Then** the user sees that the influence network cannot produce a finite total-relation analysis and must revise the judgments; no successful result is recorded (AC20).
5. **Given** a valid sparse matrix with a criterion that neither influences nor receives influence, **When** execution succeeds, **Then** that criterion has D, R, prominence, and relation all zero and is labeled balanced; a zero row or column alone does not make the whole matrix invalid.
6. **Given** an interrupted or denied save/execution, **When** the operation fails, **Then** localized visible feedback explains the failure, preserves the entered judgments for correction or retry, and does not present a stale result as the failed request's outcome.

---

### User Story 3 - Review a Frozen Analysis Later (Priority: P2)

As a project member reviewing a decision, I can reopen a DEMATEL execution and see the exact criterion judgments, results, author, and time used then, even after the case changes.

**Why this priority**: Historical judgments and results must remain explainable and attributable.

**Independent Test**: Execute a valid case, change a judgment and criterion name, execute again, and inspect both records.

**Acceptance Scenarios**:

1. **Given** a successful DEMATEL execution, **When** it is opened in history, **Then** it shows the method, ordered criterion names, direct-influence matrix, criterion indicators, execution time, and initiating member from that execution (AC23).
2. **Given** a saved execution, **When** live criteria or influences change and DEMATEL is executed again, **Then** the new execution has its own record and the prior input and result remain unchanged (AC24).
3. **Given** a historical run whose criterion names differ from the current case, **When** the run is inspected, **Then** all labels and matrix positions come from its frozen input rather than the live case.
4. **Given** mixed-method history, **When** a DEMATEL result is selected, **Then** its criterion analysis remains separate from alternative ranks, AHP weights, and ISM layers.

---

### User Story 4 - Understand and Use the Analysis in Either Language (Priority: P2)

As an authorized Persian- or English-speaking member, I can enter judgments with the keyboard, read validation feedback, and distinguish net influencing, net receiving, and balanced criteria without interpreting prominence as proof of real-world causation.

**Why this priority**: Operational users need usable, accurately explained results and access boundaries.

**Independent Test**: Perform entry, correction, execution, and history review in both languages; repeat with view-only and unauthorized project accounts.

**Acceptance Scenarios**:

1. **Given** either supported language, **When** the workspace and history are opened, **Then** labels, errors, execution dates, and role descriptions are localized, and row/column criterion alignment is preserved in both reading directions.
2. **Given** a successful result, **When** the user reads it, **Then** each criterion shows D (influence given), R (influence received), prominence (D+R), relation (D−R), and a net influencing, net receiving, or balanced role; explanatory text says these reflect entered judgments rather than demonstrated real-world causation.
3. **Given** editable criteria and influence entries, **When** the user types multiple characters, navigates cells, changes a criterion name, or reorders criteria, **Then** focus remains usable and surviving judgments stay associated with the same ordered criterion pairs; new pairs start blank and removed pairs disappear.
4. **Given** view-only access, **When** the case and history are opened, **Then** existing analyses can be inspected but inputs cannot be changed and execution is unavailable.
5. **Given** no membership or no required permission for the target project, **When** a member tries to read, edit, or execute its cases or historical runs, **Then** access is denied without exposing or changing another project's data.

### Edge Cases

- One criterion satisfies the shared size contract but its required zero diagonal makes normalization undefined; show the all-zero explanation rather than silently changing the minimum size.
- A valid ten-criterion sparse directed chain executes using exactly ten rows and columns; zero or eleven criteria are rejected.
- A scalar in place of a matrix, a non-row value, short/long rows, or extra rows produces a locatable shape error before calculation.
- Zero influences are deliberate judgments. Blank cells, invalid text, nonfinite numbers, and boolean values are not valid judgments.
- Direct influence is directional, not reciprocal or symmetric; diagonal values must be zero even when a malformed submission bypasses the editor.
- A nonzero network can still be singular; `[[0,4],[4,0]]` is rejected despite passing the scale and shape checks.
- Very small nonzero influences are not classified as an all-zero input. Undefined or numerically unreliable total relations must still fail visibly rather than produce misleading indicators.
- A criterion with no connections has zero indicators in an otherwise valid network; valid total relations may contain nonzero diagonal entries caused by indirect paths.
- Negative relation values are valid net receiving indicators, not invalid influence inputs. Display rounding must not reverse a criterion's role.
- Equal prominence values do not require a ranking or arbitrary tie-breaking; the result retains criterion order.
- Criteria added, removed, renamed, or reordered must not shift retained judgments onto different pairs or alter historical records.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Members with the required project access MUST be able to select and execute DEMATEL independently using only ordered criteria and their direct-influence matrix. Other methods and ranking-specific data MUST NOT be prerequisites (AC02).
- **FR-002**: DEMATEL MUST use 1–10 nonempty, unique criterion names and an exactly matching n×n matrix, with rows identifying influencing criteria and columns identifying receiving criteria. Invalid dimensions or names MUST stop execution (AC06–AC07, AC12, AC22).
- **FR-003**: Each off-diagonal influence MUST be a finite number in the inclusive range 0–4; fractional values are permitted. Blank, nonnumeric, nonfinite, boolean, negative, and greater-than-four values MUST be rejected. Explicit zero MUST remain distinct from missing input (AC08).
- **FR-004**: Direct self-influence MUST be zero. The editor MUST display a fixed zero diagonal, and a submitted nonzero diagonal MUST be rejected rather than silently repaired. Opposite-direction judgments MUST be independently editable.
- **FR-005**: Members MUST be able to save and reopen entered DEMATEL judgments without executing them. Incomplete drafts MAY retain blanks but MUST NOT become successful analyses until all execution requirements pass. Renaming and reordering criteria MUST preserve judgments by criterion pair; adding or removing criteria MUST update the live matrix accordingly.
- **FR-006**: Total relations MUST follow the source-defined calculation: normalize direct influences by their maximum row sum, then derive the total direct and indirect relationships as T = N × (I − N)⁻¹, where N is the normalized matrix and I is the identity matrix (AC19).
- **FR-007**: A maximum row sum of zero, singular total-relation calculation, or inability to produce reliable finite indicators MUST stop execution with an actionable matrix-level explanation and MUST NOT create a successful execution record. The system MUST NOT fabricate a zero result or silently substitute a different calculation (AC20, AC26).
- **FR-008**: Each successful analysis MUST provide D as the total-relation row sum, R as its column sum, prominence as D+R, and relation as D−R for every criterion, maintaining that run's criterion order and names (AC19, AC23).
- **FR-009**: Results MUST identify positive relation as net influencing, negative relation as net receiving, and zero relation as balanced, using the declared numerical neutrality tolerance before display rounding. Valid negative relation values MUST be retained.
- **FR-010**: Results MUST explain that prominence measures combined influence given and received and that role classifications reflect the user's judgments rather than prove real-world causation. Equal prominence MUST NOT imply a forced ranking.
- **FR-011**: A successful execution MUST append an independent immutable record containing the DEMATEL method identity, ordered criterion names, direct influences, normalization basis, total relations, criterion indicators, execution time, and initiating member (AC03, AC23).
- **FR-012**: Subsequent case edits, executions, and language changes MUST NOT overwrite a historical execution's judgments, criterion labels, numerical results, author, or time. Historical review MUST use its own frozen input (AC24).
- **FR-013**: Executing DEMATEL MUST leave ranking weights, criterion benefit/cost types, alternatives, performance matrices, and other method results unchanged. This feature MUST NOT automatically convert prominence into weights or feed another method (AC04).
- **FR-014**: Invalid entries MUST identify the affected field or row/column criteria; undefined numerical calculations MUST identify the matrix and explain the required correction. Save, permission, and execution failures MUST provide visible localized feedback and preserve recoverable user input (AC26).
- **FR-015**: Reading cases and historical runs, editing inputs, and initiating execution MUST each enforce the existing applicable project membership and Decision Support permissions. View-only members MUST be able to review existing runs without editing or executing; unauthorized requests MUST expose no other-project data.
- **FR-016**: All DEMATEL labels, validation feedback, result explanations, roles, and displayed dates MUST support Persian and English. Stable method identity MUST remain the same across languages, and changing language MUST preserve input and historical numerical values.
- **FR-017**: Criterion and matrix entry MUST support keyboard interaction and preserve focus during ordinary typing. In Persian and English, row/column labels MUST continue to identify the same directed pairs after edits and reordering.

### Key Entities *(include if feature involves data)*

- **Decision Case**: Existing project-scoped analysis workspace containing a title, selected methods, ordered criteria, and editable method-specific inputs. A DEMATEL-only case can omit alternatives and ranking inputs.
- **Direct-Influence Judgments**: One ordered n×n matrix for a case, describing how strongly each criterion influences each other criterion on a 0–4 scale, with a zero diagonal. It represents one entered judgment set, not aggregated individual votes.
- **DEMATEL Criterion Result**: A criterion's frozen name and position, influence given D, influence received R, prominence, signed relation, and interpreted role.
- **DEMATEL Execution Record**: One successful immutable analysis linking its frozen judgments and calculation context to its criterion results, project case, initiating member, and execution time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid DEMATEL-only acceptance cases complete with criterion results and no requirement to supply alternatives, ranking inputs, or execute another method.
- **SC-002**: For all agreed valid numerical reference cases, D, R, prominence, and relation match independently calculated expectations within an absolute-or-relative tolerance of 10⁻⁶ × max(1, |expected|), with every result associated with the correct criterion.
- **SC-003**: 100% of the specified invalid, all-zero, singular, and unrepresentable-result cases produce actionable feedback and zero successful execution records; zero valid sparse reference cases are rejected solely because a row or column is all zero.
- **SC-004**: Across all edit-and-rerun acceptance cases, 100% of prior DEMATEL input snapshots and results remain unchanged, and 100% of unrelated method inputs and results remain unchanged by DEMATEL execution.
- **SC-005**: In both supported languages, members can complete keyboard entry, correction, execution, and historical review without missing translations or lost criterion-pair alignment; all reference results display the expected influencing, receiving, or balanced roles.
- **SC-006**: At least 95% of valid analyses with up to ten criteria show the result within two seconds of the execution request under normal supported operating conditions, excluding judgment-entry time.
- **SC-007**: 100% of the defined unauthorized cross-project, view-only mutation, and execution-permission acceptance attempts are denied without data disclosure or successful execution.

## Assumptions

- **Working policy for O07**: Use a fixed zero diagonal and allow finite decimal influences within 0–4. Each run uses one entered matrix. Multi-user judgment collection, weighting, and aggregation are outside this feature. These defaults are feature policy for planning, not a claim that the source resolved O07.
- **Working policy for O08**: Block all-zero, singular, or numerically unreliable analyses with explicit feedback and no successful run. A one-criterion zero matrix is therefore structurally valid but not executable. There is no special zero-result outcome. Numerical techniques and stability thresholds must be documented during planning against this policy and the reference accuracy criterion.
- **Role neutrality**: Treat an absolute relation of at most 10⁻⁹ as balanced to avoid presenting insignificant arithmetic residue as directional influence. Use the unrounded result for this classification. Retain the original signed numerical result in history; presentation rounding does not change it.
- **Working boundary for O09**: Converting prominence into ranking weights, combining it with survey results, and a dedicated weight-transfer action are deferred because the source specifies no conversion formula. Members may independently enter ranking weights through existing ranking forms; DEMATEL execution does not populate those fields.
- **Existing dependencies**: The project Decision Support case lifecycle, ordered-criterion editor, method selection, project permissions, localization, and immutable execution history are the host capabilities. This specification defines their required DEMATEL behavior and does not claim they already satisfy every scenario.
- **Input conventions**: Reuse the existing shared conventions for criterion-name uniqueness and localized numeric entry where compatible with the DEMATEL scale. No new global naming or numeric-input policy is introduced by this feature.
- **Scope boundary**: This feature covers independent DEMATEL input, execution, feedback, and historical review. ISM integration, causal diagrams, survey workflows, spreadsheet imports, external calculation services, cross-method score merging, and changes to other calculation methods are outside scope.
- **Calculation provenance**: The maximum-row-sum normalization and total-relation formula come from the requested source. Their domain interpretation was also checked against [Chen's DEMATEL discussion](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254694). That paper's DEMATEL–ISM integration workflow is not imported into this feature.
- **Acceptance evidence**: A completed requirements checklist confirms specification quality only. It is not numerical, usability, timing, authorization, or implementation evidence; those outcomes require their corresponding later checks.
