# Feature Specification: Decision Support Case Shell (Phase 1)

**Feature Branch**: `018-decision-case-shell`

**Created**: 2026-10-10

**Status**: Draft

**Input**: User description: Implement Velora Decision Support (تصمیم‌یار) Phase 1 — project-scoped decision CASE shell, shared INPUT contract, and immutable EXECUTION RUN records — without SAW/TOPSIS/AHP/DEMATEL/ISM calculation engines yet.

**Authoritative sources** (do not contradict):
- [01-module-scope.md](../../docs/decision-support/01-module-scope.md) — method independence; multi-method = independent analyses on one case; no forced method chain
- [02-decision-inputs.md](../../docs/decision-support/02-decision-inputs.md) — criteria/alternatives naming, dims 1..10, weights/types/matrix rules, empty cell ≠ 0
- [08-execution-records.md](../../docs/decision-support/08-execution-records.md) — validate → run → store frozen input snapshot + method result; prior runs immutable
- [10-acceptance-checks.md](../../docs/decision-support/10-acceptance-checks.md) — AC05–AC12 structural validation; AC23–AC24 snapshot immutability shape; AC26 field/cell-located errors
- [decision-support-component-inventory.md](../../docs/decision-support-component-inventory.md) — reuse existing chrome; extract shared editors only as needed; no five method UIs yet
- [11-source-review.md](../../docs/decision-support/11-source-review.md) — leave unresolved open items open; do not hard-code undecided policies

**Phase**: 1 of 7 (see [decision-support-speckit-prompts.md](../../docs/decision-support-speckit-prompts.md))

## Gap Analysis (current vs Phase 1)

Velora has no Decision Support (تصمیم‌یار) domain yet. Project “decisions workflow” is a separate management-rationale concept and MUST NOT be overloaded as this UI. This phase introduces the case shell, shared input contract enforcement, and immutable run storage so later phases can attach independent method engines without reworking tenancy, permissions, or history.

| Concern | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| Case shell | Project-scoped decision case with title, method selection, criteria/alternatives | Absent | Create/edit case; store selected methods; list criteria & alternatives |
| Input contract | Shared validation (names, dims, numbers, types; empty ≠ 0) | Absent | Server-side validators with locatable errors (AC05–AC12, AC26) |
| Execution records | Frozen input snapshot + method result; prior runs immutable | Absent | Run entity + immutability (AC23–AC24 shape without engines) |
| Method engines | SAW / TOPSIS / AHP / DEMATEL / ISM | Out of scope | Placeholders only; no ranking or criteria-analysis calculation |
| Product surface | One project entry; bilingual; reuse chrome | Nav/forms exist elsewhere | Minimal case UI + history/empty placeholders |

**In scope**: Decision case lifecycle; method multi-select (store only); criteria/alternatives editors (max 10); shared structural validators; immutable execution-run model and create-only history behavior; project-scoped authorized access; minimal bilingual project UI; automated checks for AC05–AC12 and AC23–AC24 as applicable without engines.

**Out of scope**: Any ranking or criteria-analysis calculations; full square/rectangular matrix editors beyond stub/empty structures for later phases; Excel import; external compute services; merging or auto-chaining methods; using project-decisions-workflow as this UI; deciding open items O01–O10 as final product policy.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Create and edit a project decision case (Priority: P1)

As a project member with edit access, I create a decision case with a title, select one or more analysis methods (SAW, TOPSIS, AHP, DEMATEL, ISM), and define criteria and alternatives within contract limits so the case is ready for later method execution.

**Why this priority**: Without a case shell and method selection, no later engine phase can run or demonstrate method independence (docs 01, 02).

**Independent Test**: Create a case → set title → select methods → add up to 10 unique criteria and alternatives → reload and see persisted values; selecting multiple methods does not require any method to have been executed.

**Acceptance Scenarios**:

1. **Given** an authorized project member, **When** they create a decision case with a non-empty title, **Then** the case is stored under that project and appears in the project Decision Support area.
2. **Given** a case, **When** the user selects one or more methods from {SAW, TOPSIS, AHP, DEMATEL, ISM}, **Then** the selection is stored and selecting multiple methods means independent analyses on one case, not a forced execution chain (AC03 shape for selection; engines not required in this phase).
3. **Given** a case, **When** the user edits criteria and alternatives lists with 1–10 unique non-empty names each, **Then** the lists persist in order for that case.
4. **Given** a case with only criteria-analysis methods selected (AHP, DEMATEL, and/or ISM), **When** the user saves without alternatives, **Then** the case remains valid for later independent criteria analysis (AC02 readiness; alternatives not required until a ranking method needs them).

---

### User Story 2 - Reject invalid shared inputs with locatable errors (Priority: P1)

As a project member editing case inputs, when I submit structurally invalid criteria, alternatives, weights, types, or matrix shapes, the system stops acceptance, does not record a successful run for that invalid payload, and tells me which field or cell is wrong.

**Why this priority**: Shared input contract (doc 02) and AC05–AC12 / AC26 are the quality gate before any engine; bad data must never silently become zeros or succeed as a run.

**Independent Test**: Submit each invalid fixture below → receive a coded validation failure naming field/cell path → confirm no successful execution record was created for that payload.

**Acceptance Scenarios**:

1. **Given** ranking-oriented input dimensions of 1×1, 10×10, or a rectangular shape such as 2×3 (within 1..10 per dimension), **When** structural validation runs, **Then** valid dimensions are accepted and only real cells are considered (AC05).
2. **Given** zero criteria, zero alternatives (where alternatives are required for the validated ranking contract), or more than 10 in either dimension, **When** validation runs, **Then** acceptance stops (AC06).
3. **Given** a short matrix row, an extra row, or weights/types length mismatched to criteria count, **When** validation runs, **Then** acceptance stops and the problematic input is identified (AC07).
4. **Given** an empty matrix cell, non-numeric text, negative number, NaN, or infinity, **When** validation runs, **Then** acceptance stops; an empty cell is never treated as zero (AC08).
5. **Given** a cost-type criterion with a zero performance value, **When** validation runs, **Then** the input is rejected (AC09).
6. **Given** a negative weight or an all-zero weight vector, **When** validation runs, **Then** the input is rejected (AC10).
7. **Given** weight vectors `[2, 3]` and `[20, 30]` on otherwise identical ranking inputs, **When** weight normalization is applied for comparison of normalized weights (not scores — engines are out of scope), **Then** normalized weights match (AC11 structural/normalization portion only).
8. **Given** an empty name, a duplicate name, or a criterion type outside `benefit` | `cost`, **When** validation runs, **Then** the input is rejected (AC12); name equality is exact string match until open item O04 decides normalization.
9. **Given** any validation failure above, **When** the error is returned to the client, **Then** it includes a stable code and a field or cell path so the user can fix the location (AC26); no successful run is stored for that invalid input.

---

### User Story 3 - Immutable execution history shell (Priority: P1)

As a project member, after a successful method execution is recorded (or a Phase-1 stub run is created for history testing), changing case inputs and recording another run leaves the prior run’s frozen input snapshot and result unchanged.

**Why this priority**: Traceability (doc 08) and AC23–AC24 require immutable history before engines exist so Phase 2+ can append runs safely.

**Independent Test**: Create run A with snapshot S1 → mutate case weights/cells → create run B with snapshot S2 → re-read run A and confirm S1 and its result are unchanged; run B is a separate history entry.

**Acceptance Scenarios**:

1. **Given** a successful run recorded for named alternatives/criteria, **When** the run is inspected, **Then** alternative/criterion names and the frozen inputs for that run are preserved with the method identity, extraction time, and actor (AC23 shape).
2. **Given** an existing run, **When** the user changes a weight or a matrix cell on the live case and records a new run, **Then** a new independent history entry is created and the prior run’s input snapshot and result remain exactly as stored (AC24).
3. **Given** an existing run, **When** a client attempts to update or overwrite that run’s snapshot or result in place, **Then** the system rejects the mutation (create-only / immutable history).

---

### User Story 4 - Minimal bilingual project UI shell (Priority: P2)

As a project member, I open Decision Support from the project navigation, create or edit a case, edit criteria and alternatives (max 10), multi-select methods, and see empty/history placeholders — in Persian and English — without five method calculation UIs.

**Why this priority**: Delivers a usable Phase-1 surface and proves nav/i18n wiring; method panels wait for later phases per component inventory.

**Independent Test**: Open project Decision Support in `fa` and `en` → create/edit case → edit named lists → see method multi-select and empty/history placeholders; no SAW/TOPSIS/AHP/DEMATEL/ISM calculation panels required.

**Acceptance Scenarios**:

1. **Given** project membership and view permission, **When** the user opens the project Decision Support entry, **Then** they see the case list or empty state using existing page chrome patterns.
2. **Given** edit permission, **When** the user creates or edits a case, **Then** they can edit title, method multi-select, and criteria/alternatives lists (max 10) and see validation issues with locations when save fails.
3. **Given** no runs yet, **When** the history area is shown, **Then** an empty-state placeholder appears; when runs exist, a history list placeholder shows method, time, and actor without in-place editing of past runs.
4. **Given** locale `fa` or `en`, **When** the Decision Support shell is shown, **Then** user-facing labels and validation messages are localized; permission/API codes remain language-independent.

---

### Edge Cases

- **Empty cell vs explicit zero**: Empty is invalid for ranking performance cells and is never coerced to 0; an explicit 0 is a distinct value (and is invalid for cost criteria per AC09).
- **Criteria-only methods selected**: Alternatives and performance matrix may be absent/empty stubs; ranking-contract validators apply when ranking inputs are submitted or when a ranking method is later executed.
- **Stub / null matrices**: Phase 1 may persist empty matrix structures for later phases; full matrix UX is out of scope.
- **Open naming policy (O04)**: Names compared as exact trimmed non-empty strings; Persian digit / fuzzy-name normalization remains undecided and MUST NOT be invented as final policy.
- **Open error envelope (O03)**: Phase 1 uses coded errors with field/cell paths sufficient for AC26; exact cross-cutting envelope may evolve without changing locatability.
- **Non-member or missing permission**: Reads and writes are denied; no cross-project case or run access (IDOR prevented).
- **AC13 (all-zero benefit column)**: Engine-level rejection in later phases; Phase 1 may validate when a full ranking matrix is present but MUST NOT claim SAW/TOPSIS score acceptance.
- **Rank tie / score display (O01–O02)**: Out of scope; not decided here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST support project-scoped decision cases with at least: title, selected methods list, ordered criteria names, ordered alternative names, and structured placeholders for weights, criterion types, and matrices needed by later phases.
- **FR-002**: Users MUST be able to select any non-empty subset of {SAW, TOPSIS, AHP, DEMATEL, ISM} on a case; selection MUST NOT imply a required execution order or automatic chaining between methods (doc 01).
- **FR-003**: Selecting multiple methods MUST mean independent analyses on the same case; the product MUST NOT merge outputs of different methods into a single combined rank in this or later phases without an explicit separate feature (doc 01; AC03).
- **FR-004**: Criteria and alternatives MUST each allow between 1 and 10 inclusive names when those lists are required for the operation being validated; names MUST be non-empty and unique within their list (doc 02; AC06, AC12).
- **FR-005**: Shared input validation MUST enforce, for ranking-contract payloads when present: weights length `n`, types length `n` with each value `benefit` or `cost`, matrix shape exactly `m` rows of `n` values, finite non-negative numbers, positive values for cost cells, and positive sum of weights (doc 02; AC05–AC12 applicable portions).
- **FR-006**: Empty matrix cells MUST NOT be converted to zero; incomplete or non-finite values MUST fail validation with the cell or field identified (doc 02; AC08, AC26).
- **FR-007**: Validation failures MUST be returned as coded errors that identify the field or cell path; invalid input MUST NOT create a successful execution record (AC26).
- **FR-008**: The system MUST store execution runs that include at least: method identity, frozen input snapshot for that run, result payload, extraction timestamp, and acting user (doc 08; AC23).
- **FR-009**: Editing a case MUST NOT mutate prior runs’ frozen inputs or results; a new successful execution MUST append a new run (doc 08; AC24).
- **FR-010**: The system MUST reject in-place update or delete-and-replace of an existing run’s snapshot/result for ordinary project users (immutability of history).
- **FR-011**: Phase 1 MUST NOT implement SAW, TOPSIS, AHP, DEMATEL, or ISM calculation engines or claim numeric ranking/criteria-analysis acceptance (AC14–AC22 deferred).
- **FR-012**: All case and run operations MUST require authenticated project membership and appropriate view or edit project permissions defined consistently with Velora’s project permission model (constitution I).
- **FR-013**: The product MUST expose a single project Decision Support navigation entry and a minimal case workspace for create/edit case, method multi-select, criteria/alternatives editors, validation issue display, and execution history / empty placeholders — reusing existing page chrome and extracting `NamedListEditor`, `ValidationIssueList`, `ExecutionHistoryList`, and `InputSnapshotViewer` only as needed (component inventory).
- **FR-014**: User-facing Decision Support shell text and validation messages MUST work in Persian and English (constitution III).
- **FR-015**: Decision Support MUST remain a separate product surface from the existing management “decisions workflow”; that workflow MUST NOT be overloaded with MCDM matrix editors (component inventory).
- **FR-016**: Open items O01–O10 in [11-source-review.md](../../docs/decision-support/11-source-review.md) MUST remain open; Phase 1 MUST NOT hard-code undecided ranking-tie, CR-block, DEMATEL/ISM display, or name-normalization policies as if they were finalized.

### Key Entities

- **Decision Case**: A project-scoped decision dossier. Attributes: title; selected methods; ordered criteria; ordered alternatives; live (editable) weights, types, and matrix stubs for later phases. Does not itself store historical execution results as mutable fields.
- **Decision Run (Execution Record)**: An immutable record of one method execution attempt’s successful outcome. Attributes: method id; frozen input snapshot (criteria order, alternatives, weights, types, matrices as applicable); result payload (may be empty/stub until engines exist); extracted_at; actor. Prior runs are never overwritten when the live case changes.
- **Shared Input Contract**: The validation rules from doc 02 applied to case edits and to payloads used when creating runs; empty ≠ zero; dimensions 1..10; benefit|cost; locatable errors.
- **Method Selection**: Subset of five method identifiers stored on the case; independence semantics only — no execution in Phase 1.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An authorized project member can create a decision case, select methods, and define criteria and alternatives within contract limits in under 5 minutes without leaving the project Decision Support area.
- **SC-002**: For each of AC05–AC12 structural fixtures applicable without engines, invalid inputs are rejected 100% of the time in automated checks, and valid dimensional cases (1×1, 10×10, rectangular within limits) are accepted.
- **SC-003**: In 100% of tested re-run scenarios, changing a weight or cell and recording a new run leaves the prior run’s frozen input and result byte-for-byte unchanged (AC24).
- **SC-004**: 100% of validation failures returned in tested cases include a field or cell location usable to highlight the problem in the UI (AC26).
- **SC-005**: Users with view permission can open the Decision Support shell in both Persian and English and complete the create/edit named-list flow without untranslated critical labels on that shell.
- **SC-006**: No Phase-1 acceptance claim requires running SAW, TOPSIS, AHP, DEMATEL, or ISM calculations; method independence is demonstrated at selection and history-model level only.

## Assumptions

- Project tenancy, authentication, and project membership checks follow existing Velora patterns; new permission codes follow the established `view_*` / `edit_*` pairing (e.g. view/edit decision support) and are enforced server-side.
- Phase 1 may create runs via a controlled stub/test path or “record run shell” that stores a frozen snapshot and empty/placeholder result so AC23–AC24 can be proven before engines exist; production “Run method” buttons for real engines arrive in later phases.
- Weight normalization (`w[j] = weights[j] / sum(weights)`) is available as a shared pure helper for AC11; score computation is out of scope.
- Matrix UX beyond empty/stub persistence is deferred to Phase 2+; validators still enforce contract rules when matrix data is supplied.
- Name uniqueness uses exact string equality after rejecting empty names; trimming leading/trailing whitespace is allowed as a safe default; Persian-digit conversion and fuzzy deduplication remain open (O04).
- Coded validation errors with field/cell paths satisfy AC26 for Phase 1; a single cross-app error envelope (O03) may be refined later without removing locatability.
- Open items O01, O02, O05–O10 do not block Phase 1; they stay documented as open.
- Reuse of existing layout/form/nav components is preferred over new chrome; new shared Decision Support components are introduced only when inventory items are needed for this phase’s UI stories.
- Automated verification uses the project’s existing pytest-oriented API/domain test style for validators and run immutability; full UI E2E is not required to close Phase 1 structural ACs.
