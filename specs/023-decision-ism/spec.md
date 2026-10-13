# Feature Specification: Independent ISM Criterion Layering

**Feature Branch**: `develop` (unchanged; no branch-creation hook configured)

**Feature Directory**: `specs/023-decision-ism`

**Created**: 2026-10-12

**Status**: Draft — quality validated, ready for planning

**Input**: User description: `docs/decision-support/07-ism.md`

**Source requirements**: [ISM](../../docs/decision-support/07-ism.md), [method independence](../../docs/decision-support/01-module-scope.md), [shared input contract](../../docs/decision-support/02-decision-inputs.md), [execution records](../../docs/decision-support/08-execution-records.md), [acceptance checks](../../docs/decision-support/10-acceptance-checks.md), and [open decision O10](../../docs/decision-support/11-source-review.md).

Authorized project members can describe directed relationships between criteria and inspect the resulting structural layers, including indirect relationships and cycles. ISM is independent of DEMATEL, weighting, and alternative ranking. The cycle-presentation policy below is a documented working assumption, not a claim that the source settled O10.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extract Layers from My Criterion Relationships (Priority: P1)

As a project member, I select ISM, define my criteria and their yes/no influence relationships, then see their structural layers without entering alternatives, weights, or another analysis result.

**Why this priority**: Independent structural layering is the main user value and the requested method's core outcome.

**Independent Test**: Use criteria A, B, C with only A→B and B→C present. Execute ISM alone and inspect indirect reachability A→C and layers 1:C, 2:B, 3:A.

**Acceptance Scenarios**:

1. **Given** an ISM-only case with criteria A, B, C and direct relations `[[0,1,0],[0,0,1],[0,0,0]]`, **When** an authorized member executes ISM, **Then** the reachability matrix is `[[1,1,1],[0,1,1],[0,0,1]]` and the layer list is 1:C, 2:B, 3:A, without requiring alternatives, ranking weights, DEMATEL, AHP, SAW, or TOPSIS (AC02, AC21).
2. **Given** A→B, A→C, B→D and C→D, **When** ISM executes, **Then** layers are 1:D, 2:B and C, 3:A, with B before C when that is their original criterion order; all four criteria appear exactly once.
3. **Given** a one-criterion case A with direct matrix `[[0]]` or `[[1]]`, **When** ISM executes, **Then** reachability is `[[1]]` and the result contains only A in layer 1, with the submitted direct value preserved in the execution's input.
4. **Given** a complete all-zero matrix for multiple criteria, **When** ISM executes, **Then** reachability contains only self-relations and all criteria appear in layer 1 in their original order; no relationships between different criteria or cycle groups are invented.
5. **Given** a mixed-method case with existing method inputs or results, **When** ISM executes, **Then** only a separate ISM result is appended; weights, alternative ranks, other inputs, and other results remain unchanged (AC03).

---

### User Story 2 - Enter and Correct Explicit Binary Judgments (Priority: P1)

As a project member, I can enter each directed relationship explicitly, save an unfinished draft, and correct errors before execution without an unanswered relationship being treated as absent.

**Why this priority**: Treating a blank as zero silently changes the network and can change its layers.

**Independent Test**: Save a draft with a blank off-diagonal relationship, reopen it, attempt execution, correct the named cell, and execute successfully. Repeat with invalid values and mismatched matrix dimensions.

**Acceptance Scenarios**:

1. **Given** an unanswered relationship, **When** the draft is saved and reopened, **Then** it remains unanswered; execution is blocked until all required relationships have valid judgments, and feedback identifies the influencing and receiving criteria (AC08, AC26).
2. **Given** an explicit zero relationship, **When** ISM executes, **Then** it is accepted as a deliberate absence of a direct relation rather than mistaken for missing input.
3. **Given** a relationship value other than numeric zero or one, including a fraction, negative value, value greater than one, text, boolean, or nonfinite number, **When** execution is requested, **Then** the affected cell is identified and no successful execution is recorded.
4. **Given** zero or more than ten criteria, blank/duplicate criterion names, or a matrix with non-row entries, missing/extra rows or wrong row lengths, **When** execution is requested, **Then** the invalid field or matrix location is identified before layering and no successful execution is recorded (AC06–AC07, AC12, AC22).
5. **Given** distinct A→B and B→A judgments, **When** the member edits one cell or renames/reorders criteria, **Then** the opposite judgment is not automatically changed and surviving relations stay associated with the same criterion pairs; newly added pairs are unanswered and removed pairs disappear.
6. **Given** a denied or interrupted save/execution, **When** the operation fails, **Then** visible localized feedback preserves recoverable user input, no successful result is added, and an older result is not presented as the failed request's outcome.

---

### User Story 3 - Understand Cycles and Review Frozen Layers (Priority: P2)

As a project member reviewing a decision, I can see when criteria are mutually reachable, understand why they share a layer, and reopen the exact relationships and layers from a previous execution after the case changes.

**Why this priority**: Cyclic relationships are valid judgments, and later edits must not rewrite the explanation or provenance of an earlier analysis.

**Independent Test**: Execute A↔B with B→C, inspect layers 1:C and 2:A/B with a mutual-reachability group, then change the live case and verify the saved analysis stays unchanged.

**Acceptance Scenarios**:

1. **Given** direct relations `[[0,1,0],[1,0,1],[0,0,0]]`, **When** ISM executes, **Then** reachability is `[[1,1,1],[1,1,1],[0,0,1]]`, C is layer 1, A and B are layer 2, and A/B are labeled as a mutually reachable group; the cycle is accepted, not discarded.
2. **Given** A→B→C→A, **When** ISM executes, **Then** every criterion can reach every criterion, all three appear in layer 1, and one mutual-reachability group contains A, B and C even though no direct bidirectional pair is present.
3. **Given** two unrelated criteria in the same layer, **When** the result is inspected, **Then** sharing a layer alone does not label them as a mutual-reachability group. Automatically included self-relations alone do not create a multi-criterion cycle label.
4. **Given** a successful ISM execution, **When** history is opened, **Then** it shows ISM identity, frozen criterion names/order, submitted direct relations, derived reachability, layers and mutual groups, execution time and initiating member (AC23).
5. **Given** that execution, **When** the member renames/reorders criteria, changes a relation and executes again, **Then** a new record is appended and all prior input, derived relations, layer membership, group labels, actor and time remain unchanged (AC24).
6. **Given** a result with lower structural layers or cyclic criteria, **When** the member reads its explanation, **Then** it distinguishes upper/result-oriented layers from lower/more foundational layers and says the structure alone does not justify removing a criterion as irrelevant or redundant.

---

### User Story 4 - Use ISM Safely in Persian or English (Priority: P2)

As a Persian- or English-speaking member, I can use the relationship editor and layered result with the keyboard and only perform actions allowed by my project access.

**Why this priority**: Accessible localized presentation and project isolation are necessary for practical use and trusted history.

**Independent Test**: Complete entry, correction, execution and historical review in both languages, including language switching and view-only/unauthorized accounts.

**Acceptance Scenarios**:

1. **Given** Persian or English, **When** a member opens the editor or result/history, **Then** labels, yes/no/blank states, error explanations, layer numbers, group explanations and displayed dates use the active language, while relation direction and criterion pairing remain correct in both reading directions.
2. **Given** editable criterion names and relations, **When** a member types names, navigates and selects relationships with the keyboard, **Then** focus remains usable and rename/reorder/add/remove preserves the intended surviving directed pairs.
3. **Given** view-only project access, **When** the workspace is opened, **Then** existing cases and results can be inspected but creation, criterion/method/relation edits, save and execution are unavailable; attempts to bypass the controls remain denied.
4. **Given** no membership or no required access to the target project, **When** a person tries to inspect or alter its cases or historical analyses, **Then** access is denied without disclosure or mutation of another project's data.
5. **Given** a pending case save or method execution, **When** additional edits, a second save/run, or a case switch occurs, **Then** overlapping actions cannot silently substitute another draft or attach a late response to the newly selected case; any displayed result is associated with its own frozen input.
6. **Given** a historical execution, **When** the member switches language, **Then** presentation changes but stored relation values, criterion order, layer/group membership, actor and execution time remain unchanged.

### Edge Cases

- One criterion and complete all-zero matrices are valid ISM networks; they must not inherit DEMATEL's all-zero rejection.
- A direct diagonal zero or one both produce reachable self-relations of one. Combining self-relations must never produce a value of two or modify the saved direct input.
- Ten criteria are supported with their actual ten-by-ten matrix; zero or eleven criteria stop execution.
- Complete absence of cross-criterion relationships produces one layer containing all criteria, with no invented mutual group.
- Fractions such as 0.5, negative values, numbers greater than one, nonfinite values, text and booleans are not valid executable judgments. An explicit zero is valid and a blank remains missing.
- A directed pair is independent of its reverse; a one-way relationship must not be mirrored automatically.
- Indirect chains must be completed before layering; a direct relation need not exist for derived reachability to exist.
- Both direct two-way relations and longer cycles form mutually reachable groups. A full-cycle network must finish with one layer, not fail or loop indefinitely.
- At every layer-extraction round, reachability/antecedent/intersection membership is restricted to criteria still active in that round. Previously removed criteria must not block later layers.
- Disconnected groups and criteria can share a layer without being mutually reachable. Original criterion order remains stable inside each layer and group.
- Adding, removing, renaming or moving criteria updates both axes consistently; historical relations and labels stay frozen.
- A failed rerun or late response cannot replace the current case's draft or masquerade as a newly successful analysis. Previously successful history remains inspectable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Authorized members MUST be able to select and execute ISM independently from ordered criteria and their direct binary relations, without requiring alternatives, weights, ranking data, DEMATEL or another method's output (AC02).
- **FR-002**: Execution MUST require 1–10 nonempty unique criterion names and an exactly corresponding n×n matrix; rows identify influencing criteria and columns identify receiving criteria. Invalid names/counts/shapes MUST stop execution (AC06–AC07, AC12, AC22).
- **FR-003**: Every executable relation, including each diagonal entry, MUST be a finite numeric value exactly equal to zero or one. Blank, text, boolean, nonfinite and other numeric values MUST be rejected without rounding or coercing a missing judgment to zero (AC08).
- **FR-004**: Members MUST be able to edit opposite-direction relationships independently, save an incomplete draft and reopen its unanswered entries. Renaming/reordering MUST preserve surviving criterion-pair judgments; adding/removing criteria MUST update the live matrix without inventing new cross-criterion judgments.
- **FR-005**: Derived reachability MUST include each criterion's self-relation through binary inclusion of identity, regardless of its direct diagonal judgment. Derivation MUST retain binary zero/one values and MUST NOT overwrite the submitted direct matrix.
- **FR-006**: Reachability MUST include all direct and indirect paths until full transitive closure is reached; if A reaches B and B reaches C, A MUST reach C in the final derived matrix (AC21).
- **FR-007**: For each active criterion in each extraction round, the reachable set MUST contain active criteria it can reach, the antecedent set MUST contain active criteria that can reach it, and their intersection MUST be determined from those sets. The active criterion itself MUST belong to both sets.
- **FR-008**: The next layer MUST contain all active criteria whose reachable set equals its intersection with the antecedent set. Those criteria MUST then leave the active set, with the process continuing until every criterion receives exactly one layer. Equality of complete reachable and antecedent sets MUST NOT replace this rule (AC21).
- **FR-009**: Result layers MUST be numbered consecutively starting at one for the first/top extracted layer, with later/lower layers explained as more foundational in the entered network. Criteria within each layer MUST retain their original relative order; layer membership MUST NOT be presented as a criterion weight or alternative ranking.
- **FR-010**: Valid cyclic networks MUST be accepted. Results MUST identify maximal groups of two or more criteria that can each reach every other member, assign each group to its shared layer and list its members in original criterion order. Criteria merely sharing a layer and automatic self-relations alone MUST NOT be labeled as such a group.
- **FR-011**: Members MUST be able to inspect the ordered layer list, mutually reachable groups and derived reachability alongside the submitted direct judgments. Explanations MUST make clear that this modeled structure alone is not a reason to remove a criterion as irrelevant or redundant.
- **FR-012**: A successful ISM execution MUST append a distinct immutable record containing method identity, ordered criterion names, submitted direct relations, derived reachability, layers/groups, execution time and initiating member (AC03, AC23).
- **FR-013**: Live case edits, later runs and language changes MUST NOT alter an earlier execution's input, labels, reachability, layer/group membership, actor or time. Historical review MUST use that execution's frozen names and data rather than the current case (AC24).
- **FR-014**: ISM execution MUST leave weights, alternatives, performance data, other method inputs and existing results unchanged. It MUST NOT automatically execute another method, produce ranking weights or delete criteria based on structural position.
- **FR-015**: Invalid entries MUST produce feedback locating the affected field or directed criterion pair. Failed validation, unsuccessful derivation or failed save/execution MUST NOT record or display a partial analysis as a successful result; recoverable draft input MUST remain available for correction (AC26).
- **FR-016**: Reading cases/results, creating/editing inputs and initiating execution MUST enforce the existing appropriate project membership and Decision Support access. View-only members MUST be able to review existing results without writable controls; unauthorized requests MUST expose or alter no other-project data.
- **FR-017**: All ISM labels, relation states, validation feedback, layer/group explanations and displayed dates MUST work in Persian and English. Language switching MUST preserve stable method identity and stored judgment/result values.
- **FR-018**: Criterion and relation editing MUST support keyboard use with stable typing focus and correct row-to-column associations in both reading directions. Pending or late operations MUST NOT cause overlapping saves, lost recoverable judgments or results attached to another selected case.

### Key Entities *(include if feature involves data)*

- **Decision Case**: Existing project-scoped workspace containing a title, selected methods, ordered criteria and editable method-specific judgments. An ISM-only case can omit alternatives and ranking inputs.
- **Direct Binary Relations**: The ordered n×n judgments indicating whether each criterion directly influences each other criterion; numeric zero means absent, one means present and an unfinished draft may contain unanswered entries.
- **Derived Reachability**: The frozen binary relation set for one execution, including identity and every indirect path, aligned to that execution's ordered criteria and distinguishable from direct judgments.
- **Structural Layer**: A consecutively numbered top-to-bottom level containing ordered criterion members. Every criterion belongs to exactly one layer in a completed result.
- **Mutually Reachable Group**: A maximal set of at least two criteria with reachability in both directions between all members; it remains visible within one layer and is distinct from unrelated criteria sharing the layer.
- **ISM Execution Record**: One immutable successful analysis associating its frozen direct/derived relationships, layers/groups and criterion names with its decision case, initiating member and execution time.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of valid ISM-only acceptance cases produce layers without alternatives, ranking inputs or any other method execution.
- **SC-002**: For every agreed chain, branching, disconnected, all-zero, single-criterion and cyclic reference network up to ten criteria, reachability and layer membership exactly match independently established binary expectations; every criterion appears exactly once and no completed result has more layers than criteria.
- **SC-003**: 100% of specified incomplete, nonbinary, invalid-name and wrong-shape cases stop with locatable feedback and zero successful execution records; 100% of valid all-zero and cyclic reference cases are accepted.
- **SC-004**: Every specified two-way and longer-cycle reference is labeled with the correct maximal mutual group and layer, with zero isolated or merely same-layer criteria falsely grouped. Layer explanations distinguish foundational position from ranking or criterion-removal advice.
- **SC-005**: Across all edit/rerun/language-switch acceptance cases, 100% of earlier input/result/actor/time records remain unchanged and 100% of unrelated method inputs/results remain unchanged by ISM execution.
- **SC-006**: In both languages, members can complete keyboard entry, correction, execution and history review without untranslated critical labels, lost focus or changed criterion-pair associations, including rename/reorder/add/remove and delayed-response scenarios.
- **SC-007**: 100% of defined unauthorized cross-project and view-only mutation/execution attempts are denied without data disclosure or successful execution.
- **SC-008**: At least 95% of valid analyses with up to ten criteria show the completed layer result within two seconds of the execution request under documented normal supported conditions, excluding relationship-entry time.

## Assumptions

- **Working policy for O10**: Present a numbered layer list with explicit mutual-reachability group labels; accept cycles without deleting or splitting their members into artificial levels. An interactive layer diagram, layout rules and graph editing are deferred. This feature policy bounds the source's open presentation question without claiming O10 was resolved in the source documents.
- **Direct diagonal policy**: Both binary zero and one are valid direct self-judgments. New drafts initialize the diagonal to explicit zero and leave off-diagonal judgments unanswered; users may change a direct diagonal to one. Derived self-reachability is always one and does not rewrite direct input or produce a multi-criterion cycle label by itself.
- **Binary value policy**: Numeric zero and one, including numerically identical 0.0 and 1.0, are accepted. Text and booleans are not executable numeric judgments. Supported localized entry follows the existing shared input conventions and results in explicit binary judgments; no new global numeric/name normalization policy is introduced.
- **Live identity preservation**: Criterion rename/move/add/remove must preserve surviving ISM relations without changing established AHP or other method editing semantics. No requirement is made here about how identities are stored.
- **Existing dependencies**: Project-scoped Decision Support cases, method selection, ordered-criterion editing, project access controls, localization and execution history are the host capabilities. ISM does not depend on DEMATEL implementation or completion of its task list; this specification does not claim the host already satisfies every ISM scenario.
- **Scope boundary**: Independent binary relation entry, derivation, layer/group presentation, failure feedback and immutable history are in scope. DEMATEL threshold conversion, forced method chaining, weight generation/transfer, ranking changes, causal proof, automated criterion deletion, survey aggregation, spreadsheet import and external computation services are outside this feature.
- **Method provenance**: The requested source defines binary self-inclusion, transitive completion and active-set layer extraction. Its reachable/intersection equality condition was checked against [Chen's ISM level-partitioning discussion](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0254694). That paper's DEMATEL–ISM integration and threshold workflow are not imported into this independent ISM feature.
- **Acceptance evidence**: Specification quality review confirms requirements readiness only. Numerical/structural reference checks, permissions, keyboard/localization, persistence and user-visible timing each require their own later behavioral evidence; no implementation acceptance is claimed here.
