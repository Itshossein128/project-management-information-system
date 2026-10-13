# Feature Specification: Traceable Decision Execution Records

**Feature Branch**: `develop` (unchanged; no branch-creation hook configured)

**Feature Directory**: `specs/024-decision-execution-records`

**Created**: 2026-10-13

**Status**: Draft — quality validated, ready for planning

**Input**: User description: `docs/decision-support/08-execution-records.md`

**Source requirements**: [execution lifecycle and records](../../docs/decision-support/08-execution-records.md), [method independence](../../docs/decision-support/01-module-scope.md), [method input boundaries](../../docs/decision-support/02-decision-inputs.md), [acceptance checks AC03 and AC23–AC26](../../docs/decision-support/10-acceptance-checks.md), and [open decisions O01/O02](../../docs/decision-support/11-source-review.md). Method-specific outputs follow the existing [SAW](../019-decision-saw/spec.md), [TOPSIS](../020-decision-topsis/spec.md), [AHP](../021-decision-ahp/spec.md), [DEMATEL](../022-decision-dematel/spec.md), and [ISM](../023-decision-ism/spec.md) specifications.

Project members need to explain which analysis produced a result, what data it used, and how that result differed from later analyses. This feature completes the shared execution-record and historical-review experience while preserving the method-specific calculations and working behavior already delivered.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record One Selected Method Reliably (Priority: P1)

As a member with edit access, I execute a selected method using its valid inputs and receive a distinct saved result that identifies the exact data analyzed.

**Why this priority**: A result cannot support a decision if its method or inputs are ambiguous.

**Independent Test**: Execute SAW alone on a prepared case, inspect the recorded raw and normalized weights and output, then repeat after changing one input. Verify two separate records and no execution of another method.

**Acceptance Scenarios**:

1. **Given** a selected, available method and valid required inputs, **When** a member executes it, **Then** exactly one record for that completed attempt contains that method's result and the fixed input used to produce it, together with its initiating member and execution time (AC23).
2. **Given** only TOPSIS, AHP or ISM is selected, **When** it executes with valid method-specific inputs, **Then** it succeeds without requiring another method's selection, execution or unrelated inputs; no other method's result or editable input changes.
3. **Given** an unanswered or invalid required field, **When** execution is requested, **Then** the affected field or named matrix cell is identified, no successful record is appended, and an older success is not displayed as the attempted execution's result (AC26).
4. **Given** an execution already saved, **When** a member explicitly executes again with unchanged or changed inputs, **Then** a separate record is appended and the previous record remains unchanged (AC24).
5. **Given** case inputs or method selection change while an execution is being processed, **When** that execution completes or is rejected, **Then** a saved result uses one consistent set of eligible method inputs; it never mixes names, ordering or values from different case states, and feedback identifies the actual completed attempt.

---

### User Story 2 - Reopen the Exact Analysis Behind a Decision (Priority: P1)

As a reviewing member, I find an earlier execution and read its inputs and method-specific output without substituting the case's current draft or recalculating the old result.

**Why this priority**: Historical traceability is the primary purpose of the source document.

**Independent Test**: Execute a ranking analysis, change names, order, weights and a performance value on the live case, execute again, then reopen the first record. Its names, values, normalized weights, result, member and time remain the original ones.

**Acceptance Scenarios**:

1. **Given** a case with recorded executions, **When** history opens, **Then** records are distinguishable by stable identity, method, execution time and initiating member, with newest records first; a member can filter by method and navigate all available records.
2. **Given** a historical SAW or TOPSIS record, **When** it is selected, **Then** readable review shows its ordered criteria and alternatives, criterion types, raw and normalized weights, performance matrix, and recorded alternative names, scores and ranks; TOPSIS also shows the recorded best/worst distances.
3. **Given** a historical AHP or ISM record, **When** it is selected, **Then** the original criterion order and method input matrix are shown with the stored weights and inconsistency report for AHP, or stored reachability, layers and mutual groups for ISM. A completed DEMATEL record, when available, shows its original influence inputs and recorded prominence and relation indicators.
4. **Given** an earlier execution, **When** the case title, criteria, alternatives, order, methods or input values change, or a later execution succeeds, **Then** the earlier record's stored input, output, method, initiating-member identity and time remain unchanged; review continues to use that record's own labels and ordering.
5. **Given** an old placeholder or incomplete record, **When** it is inspected, **Then** available provenance and inputs remain readable and missing or unusable results are explicitly marked unavailable; values are not reconstructed from the live case, invented, or silently recalculated.
6. **Given** an existing execution, **When** a member attempts to overwrite or delete that individual record, **Then** the attempt is denied and its recorded data remains unchanged.

---

### User Story 3 - Review Independent Results from Multiple Methods (Priority: P2)

As a decision maker, I inspect SAW and TOPSIS analyses on the same case and understand each method's separate order and scores without interpreting them as a combined ranking.

**Why this priority**: Different methods can disagree; preserving that disagreement enables review rather than hiding it.

**Independent Test**: Use a fixture for which SAW and TOPSIS produce different orders, record each separately, and inspect both saved analyses. Each retains its own names, scores, ranks and inputs.

**Acceptance Scenarios**:

1. **Given** SAW and TOPSIS results with different alternative orders, **When** each is inspected from the same case's history, **Then** the method is clearly labeled, its own score and rank are shown, and neither order is replaced or blended with the other (AC25).
2. **Given** ranking results with equal scores, **When** recorded ranks are displayed, **Then** the existing interim ordinal ranks and stable original alternative order are preserved; no new shared-rank rule is applied to old records.
3. **Given** an AHP or DEMATEL analysis on the same case, **When** its history is reviewed or another method executes, **Then** ranking weights remain unchanged unless a separately authorized manual edit changes them; reviewing history does not initiate a weight transfer or another execution.
4. **Given** a historical result whose method is no longer selected on the live case, **When** history is filtered to that method, **Then** the old record remains inspectable and read-only; its existence does not reselect or execute that method.

---

### User Story 4 - Recover and Review Safely in Either Language (Priority: P2)

As an authorized Persian- or English-speaking member, I can review history with the keyboard, recover from interrupted requests, and distinguish current drafts from saved historical results.

**Why this priority**: Failures, permissions and language changes must not undermine trust in execution records.

**Independent Test**: Complete historical review in both languages with edit and view-only accounts; interrupt a completed execution's response while delaying or failing history recovery, then verify the saved result can be inspected before any explicit retry.

**Acceptance Scenarios**:

1. **Given** Persian or English is active, **When** history, a frozen input or a result is inspected, **Then** labels, empty/error/unavailable states and dates follow the active language, keyboard navigation remains usable, and changing language preserves stored names, numeric values, order, identities and time.
2. **Given** view-only project access, **When** a member opens records, **Then** authorized history and results are readable while edit, save and execution actions are unavailable; attempts to bypass those restrictions are denied.
3. **Given** no access to the target project or a record belonging to another project or case, **When** history or a record is requested, **Then** no protected input or result is disclosed or altered.
4. **Given** a failed or unconfirmed save or execution response, **When** the outcome cannot be established, **Then** recoverable input is retained, current success is cleared, no automatic execution retry occurs, and an unconfirmed save cannot initiate execution. If execution may have committed, the case remains protected from another attempt until bounded history recovery succeeds, fails or times out, with explicit localized feedback.
5. **Given** an execution may have committed while history shows a method filter or a later page, **When** recovery succeeds, **Then** the displayed filter/page identifies the authoritative recovered view and exposes the new record and accurate count before an explicit retry; failed recovery gives unresolved feedback without claiming fresh visible history.
6. **Given** a save, execution or historical detail is pending for case A, **When** a member selects case B or returns to A before completion, **Then** late responses do not replace B's draft, displayed result or history selection, and A cannot acquire a duplicate pending operation; authorized historical review remains available.

### Edge Cases

- Empty history, an empty method filter result, and a page made empty by a changed filter have distinct recoverable presentation; no unrelated case's rows appear.
- Equal execution times still allow distinct records to be reached; browsing a fixed set of records does not omit or duplicate records between pages.
- Criteria-only analyses do not require alternatives, ranking weights or a performance matrix. Invalid unused drafts do not become prerequisites for another method.
- A saved ranking record may use alternative or criterion names that no longer exist on the live case; those original labels and axis associations remain authoritative.
- Explicit zero, unanswered input, and missing legacy information remain distinct; the viewer does not convert missing values into valid zeros.
- Normalized ranking weights may be absent in an older record; review labels them unavailable and retains recorded raw weights without deriving replacement values.
- AHP inconsistency warnings remain recorded outcomes under its existing contract; this feature does not retrospectively convert them to failed records.
- ISM cycle groups are valid structural output and do not become rankings, weights or suggestions to remove criteria.
- DEMATEL placeholder records are not numerical analyses. Availability of a method selection or history entry does not establish that its calculation engine has been delivered.
- Empty, non-readable or structurally incomplete responses do not establish success. Loss of a response may follow a committed execution, so failure feedback cannot promise that no record exists.
- An explicit retry after an uncertain outcome may append another record; history distinguishes attempts and no automatic duplicate-prevention guarantee is introduced.
- A deleted or inaccessible case, revoked access, unavailable initiating-member display name, or failed detail load produces understandable feedback without retaining another case's detail or fabricating provenance.
- Locale formatting or score rounding must not change stored numeric results, ordering or ranks, or turn an unavailable result into a zero score.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A member with edit access MUST be able to execute each selected, available method independently using its required inputs, without executing or supplying unrelated data for another method.
- **FR-002**: Required inputs MUST be validated before recording a successful result; failures MUST identify the affected field or named cell and append zero successful records (AC26).
- **FR-003**: Each successful execution attempt MUST append exactly one distinct record linking its case, project, method, fixed input, method output, execution time and initiating-member identity (AC23).
- **FR-004**: The recorded input and output MUST represent one consistent eligible case state used for that method's calculation; concurrent edits MUST NOT create mixed-state inputs or a result disconnected from its fixed input.
- **FR-005**: Fixed inputs MUST retain criterion names and order plus the inputs required by the executed method. New ranking records MUST additionally retain alternative names and order, criterion types, raw weights, normalized computational weights and performance values. Extra context already stored MUST remain preserved.
- **FR-006**: Recorded input, output, method, initiating-member identity and execution time MUST remain unchanged after live-case edits, subsequent executions, language changes or attempted individual-record updates/deletions (AC24).
- **FR-007**: Repeated explicit successful executions, including identical inputs, MUST create independently identifiable records rather than overwrite an earlier one.
- **FR-008**: Authorized members MUST be able to browse newest-first case history, filter by any recorded method and navigate all records with accurate counts. For a fixed record set, page traversal MUST include every matching record exactly once, including records with equal times.
- **FR-009**: Selecting a record MUST show its method, stable identity, initiating member and execution time with a clearly labeled read-only historical view distinct from the editable case and current attempt.
- **FR-010**: Historical inputs and outputs MUST use the selected record's own names, order and values; review MUST NOT recalculate an old analysis, substitute current case fields or write to the live case.
- **FR-011**: SAW review MUST show recorded alternative names, scores and ranks. TOPSIS review MUST also show recorded best/worst distances. AHP review MUST show recorded criterion weights and inconsistency information; DEMATEL review MUST show recorded prominence and relation indicators when a completed result exists; ISM review MUST show recorded direct relations, reachability, layers and mutual groups.
- **FR-012**: Multiple methods' results MUST remain independently labeled and inspectable with their own scores and ranks; no combined score, merged rank, compulsory order or automatic weight transfer is introduced (AC03, AC25).
- **FR-013**: Old placeholder, incomplete or unusable records MUST retain readable available provenance/input and explicitly identify unavailable information; review MUST NOT invent missing numeric output or normalized weights.
- **FR-014**: Unknown or unconfirmed save/execution responses MUST preserve recoverable drafts, clear current success and provide localized feedback. Execution MUST NOT follow an unconfirmed save or be retried automatically.
- **FR-015**: When an execution may have committed, bounded authoritative history recovery MUST settle before another same-case attempt is enabled. Success MUST expose an accurate visible history view containing the recoverable committed record; lookup failure/timeout MUST be explicit and MUST NOT claim that no record was saved. Subsequent retry MUST require an explicit user action.
- **FR-016**: Pending operations MUST remain associated with their captured case across reselection and navigation; late responses MUST NOT replace another case's draft, result, history detail or filter/page, or release its pending protection. Same-case overlapping saves/executions MUST be prevented while authorized history remains readable.
- **FR-017**: Viewing case history and record details MUST require the existing project view access; saving or executing MUST require edit access. Every record read or mutation attempt MUST respect both project and parent-case boundaries.
- **FR-018**: Persian and English historical review MUST provide localized labels, statuses, validation/recovery messages and dates with keyboard-accessible selection and readable named matrix axes; presentation changes MUST NOT change stored identities, names or values.
- **FR-019**: Existing valid historical records and method output policies MUST remain compatible. This feature MUST preserve interim ranking order/rank behavior and existing AHP/DEMATEL/ISM interpretation without claiming the source's unresolved final ranking/display policies are settled.

### Key Entities *(include if feature involves data)*

- **Decision Case**: The project-owned editable context, selected methods and live input that prepare future executions; it is distinct from a completed record's fixed input.
- **Execution Record**: One identifiable method attempt successfully recorded for a case, containing its fixed input, stored output, initiating-member identity and execution time; independently retained from later attempts.
- **Fixed Input**: The ordered named criteria, relevant method judgments and, for ranking, ordered alternatives, types, raw/normalized weights and performance values used by that execution. It is data, not a screenshot requirement.
- **Method Output**: The recorded method-specific scores/ranks/distances, weights/inconsistency, influence indicators or structural relations/layers/groups. Different methods' outputs remain separate.
- **History View**: The member's current case, method filter, page and selected historical record; it controls presentation without changing saved analyses.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In reference executions for every available method, 100% of successful attempts produce one separately identifiable record with matching method input/output, initiating member and time; single-method execution produces zero other-method records.
- **SC-002**: Across edits to names, order, weights, matrix values and selected methods followed by repeated execution, 100% of earlier recorded inputs, outputs, method identities, initiating-member identities and times remain unchanged (AC24).
- **SC-003**: A reviewer can identify the method, named inputs, applicable raw/normalized weights, stored output and provenance from each supported completed record without consulting or changing the live case; unavailable legacy values are explicitly identified in every incomplete-record scenario.
- **SC-004**: In a case with 100 fixed mixed-method records, browsing all pages and each method filter reaches every matching record exactly once with correct counts, including equal-time records. Under normal local conditions, at least 95% of history-page and record-detail selections become visible within two seconds, measured from selection to completed readable display.
- **SC-005**: In all invalid-input, denied-access and unconfirmed-save scenarios, zero successful executions are added by the rejected attempt; all reported input failures are locatable and recoverable input remains available.
- **SC-006**: In all committed-but-unconfirmed execution scenarios, no automatic repeat occurs, same-case retry remains protected until bounded recovery settles, and successful recovery makes the committed record inspectable with accurate visible filter/page/count. Failure and timeout scenarios always show unresolved feedback.
- **SC-007**: Both English and Persian complete keyboard-driven history selection, frozen-input review, result review, language switching and failure recovery without untranslated critical labels or changes to recorded values. View-only and unauthorized scenarios permit zero prohibited writes or protected disclosures.
- **SC-008**: SAW/TOPSIS disagreement fixtures retain 100% of each method's original scores, ranks and alternative names, display results independently, and produce zero blended ranks or automatic weight changes (AC25).

## Assumptions

- This is a shared execution-record completion feature based on document 08, not the broader Phase 7 manual-transfer and whole-module acceptance project. Existing case/history and method-specific functionality is extended only where these requirements require it; working calculations are preserved.
- Source inspection at specification time shows independent SAW, TOPSIS, AHP and ISM execution, stored history and method filtering already exist. AHP/ISM have readable historical output, while ranking history lacks equivalent method-specific review. This is a planning baseline, not a new behavioral acceptance claim; planning must verify it against the current workspace.
- DEMATEL execution is currently a placeholder despite its existing specification. Implementing that engine belongs to feature 022. This feature must safely review placeholders and completed DEMATEL records when available; history-presentation checks can use fixed completed-record examples without claiming live DEMATEL calculation acceptance.
- Existing project membership, view/edit access and administrator policy apply. Record-level edit/delete is forbidden; changing project/case deletion or retention policy is outside this feature.
- O01/O02 remain open as final product policy. Preserve the existing interim score-descending ranking, original-order tie stability and one-based ordinal ranks; show the stored result and existing display precision without introducing shared ranks or rewriting historical numbers. TOPSIS retains its already specified recorded distances. No new engine-version or identifier-format requirement is inferred from the source.
- Existing method specifications govern validation, AHP inconsistency outcomes, DEMATEL input/indicator interpretation and ISM groups/layers. This feature does not alter mathematical formulas, close their open product decisions or require another method to run first.
- Historical provenance requires stable initiating-member identity and recorded time. If a readable member name is unavailable, an identifiable fallback is sufficient; it does not justify substituting the current reviewer as the initiating member.
- Recovery uses the existing ten-second waiting limit as the cross-method user-facing default. It does not promise exactly-once execution after network uncertainty, idempotency, protection against all concurrent users' repeated attempts, or that a late server completion cannot appear later.
- The performance acceptance sample is a prepared local case with 100 saved records, at most ten criteria/alternatives and no artificial network delay. It is a history-review target, distinct from method calculation timing; production-scale and all-network guarantees are outside this feature.
- Excel import/export, screenshots, external computation, automatic weight transfer, combined rankings, new methods, audit-log products, full-module usability sign-off and changes to the source documents are outside scope.
