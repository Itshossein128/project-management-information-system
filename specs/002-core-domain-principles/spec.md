# Feature Specification: Core Domain Principles & Glossary

**Feature Branch**: `002-core-domain-principles`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "Implement shared Velora core domain principles and glossary from `docs/.../01-دامنه، اصول و واژه‌نامه.md` (FR-CORE). Implementation MUST be TDD. Do not start implementation in this Spec Kit pass — produce specify, plan, and tasks only."

**Source**: [01-دامنه، اصول و واژه‌نامه.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/01-دامنه،%20اصول%20و%20واژه‌نامه.md) (`FR-CORE`)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Shared glossary in product labels (Priority: P1)

As a product analyst or project manager, I see consistent Persian/English terms for core construction concepts (especially WBS, financial commitment vs actual cost, and payment certificate / صورت‌وضعیت) so business and software teams share one vocabulary.

**Why this priority**: Misnamed fields cause wrong data entry and double-counting; glossary alignment is the cheapest high-impact control.

**Independent Test**: Review WBS, cost, and contract/IPC screens and locale keys; confirm labels match the approved glossary definitions without inventing conflicting synonyms.

**Acceptance Scenarios**:

1. **Given** a WBS-related field or help text, **When** a user views it in Persian or English, **Then** it uses “WBS / ساختار شکست کار” consistently with the glossary (not a conflicting synonym for the same concept).
2. **Given** financial commitment and actual cost amounts, **When** a financial summary is shown, **Then** the two values remain separate and are not summed as if they were the same measure.
3. **Given** IPC / payment certificate UI, **When** a user views labels, **Then** “صورت‌وضعیت” is used for the certificate and is not presented as if cash had already been received.

---

### User Story 2 - Universal project record hygiene (Priority: P1)

As a product owner, every project-scoped record I create has a unique id, project link, creator, create/update timestamps, and soft-delete (or corrective document) behavior so approved history cannot be silently destroyed.

**Why this priority**: FR-CORE shared rules are prerequisites for every later module; without them, audits and tenancy fail.

**Independent Test**: Create a sample project-scoped record on a representative model; verify id, project binding, audit fields, and that delete of an approved/final record does not hard-delete.

**Acceptance Scenarios**:

1. **Given** a new project-scoped record, **When** it is saved, **Then** it has a unique identifier and is bound to its project.
2. **Given** an approved or finalized record, **When** a user attempts delete, **Then** the system uses soft-delete or a corrective/reversal path and does not physically remove the approved row.
3. **Given** a user without project membership or required permission, **When** they request another project’s record, **Then** access is denied in 100% of tested cases.

---

### User Story 3 - Currency unit safety (Priority: P1)

As a finance or project controls user, every money amount I see is labeled with its currency unit, and rial and toman cannot be added together without an explicit conversion step.

**Why this priority**: Mixed-unit totals corrupt budgets, IPCs, and cash reports; FR-CORE-006 and SC-CORE-003 are explicit.

**Independent Test**: Open financial displays that show amounts; verify unit labels; attempt or simulate mixed-unit aggregation and confirm the system blocks or requires explicit conversion.

**Acceptance Scenarios**:

1. **Given** any displayed monetary amount, **When** the user views it, **Then** the currency unit is shown next to the number.
2. **Given** two amounts in different units (rial vs toman), **When** aggregation is requested without conversion, **Then** the system refuses silent mixing and requires an explicit conversion.
3. **Given** a project with a declared base currency, **When** amounts are stored or reported for that project, **Then** they use that project currency unless an explicit conversion rate is recorded.

---

### User Story 4 - Distinguish unset, zero, and approval states (Priority: P2)

As a site or planning user, forms and reports let me tell “not recorded” from zero, and “unapproved” from “approved,” so missing progress is not treated as zero progress.

**Why this priority**: Silent zeros distort physical progress and EVM; FR-CORE-010 is a cross-module data-quality rule.

**Independent Test**: On a representative numeric form field and status field, leave unset vs enter zero vs leave unapproved; confirm UI and API preserve the distinction.

**Acceptance Scenarios**:

1. **Given** an optional numeric quantity, **When** the user leaves it blank, **Then** the system stores/presents it as unset/not recorded, not as zero.
2. **Given** the same field with value `0`, **When** saved, **Then** it is distinct from unset.
3. **Given** an unapproved vs approved record, **When** shown in lists or reports, **Then** approval state is visually and programmatically distinct.

---

### User Story 5 - Actionable notifications (Priority: P2)

As a responsible user, notifications tell me who owns the action, when it is due, and give a direct link to the record so I can act without searching.

**Why this priority**: FR-CORE-011 turns alerts into actionable work; current notifications often lack owner and deadline.

**Independent Test**: Trigger a sample notification; verify owner (responsible party), deadline (when applicable), and deep link are present and usable.

**Acceptance Scenarios**:

1. **Given** a notification about a project record, **When** the user opens it, **Then** they see the responsible party and a direct link to the record.
2. **Given** a notification that represents a time-bound action, **When** it is created, **Then** a deadline is present.
3. **Given** a user opens the link, **When** navigation completes, **Then** they land on the related record (or a clear not-found/unauthorized message).

---

### User Story 6 - Optional capability toggles per project (Priority: P2)

As a system administrator, I can disable or mark optional a capability that does not apply to a project without breaking the rest of the project structure or hiding historical data.

**Why this priority**: FR-CORE-012 prevents forcing unused modules; edge case requires preserving history while blocking new entry.

**Independent Test**: Disable one optional capability on a sample project; confirm other flows still work and historical data remains readable while new entry is blocked.

**Acceptance Scenarios**:

1. **Given** a project with an optional capability enabled, **When** an admin disables it, **Then** navigation/entry for new work in that capability is blocked or hidden.
2. **Given** historical data already exists for that capability, **When** it is disabled, **Then** historical records remain readable and are not deleted.
3. **Given** other project capabilities, **When** one optional capability is disabled, **Then** unrelated workflows continue to function.

---

### User Story 7 - Fiscal period lock and duplicate transaction warning (Priority: P3)

As a finance controller, after a fiscal period is closed I can only correct data through an audited allowed path, and entering a transaction with a duplicate document/contract number warns me before save.

**Why this priority**: FR-CORE-013/015 protect closed books and reduce duplicate postings; lower than P1 hygiene but required for financial trust.

**Independent Test**: Close a sample period and attempt an ordinary edit (must fail or force corrective path); attempt create with a duplicate document number and observe a warning.

**Acceptance Scenarios**:

1. **Given** a closed fiscal period, **When** a user tries a normal in-period edit, **Then** the system blocks it unless an allowed corrective path with audit trail is used.
2. **Given** an existing transaction document/contract number, **When** a user enters the same number again, **Then** the system warns about the duplicate before finalizing.
3. **Given** a corrective path after lock, **When** the correction is saved, **Then** actor, time, and reason are recorded.

---

### Edge Cases

- Optional capability disabled but historical data exists → preserve data; block only new entry/mutation as configured.
- Dates on Jalali/Gregorian day boundaries → reports for the same logical day produce consistent, explainable results.
- Zero vs unset on required numeric fields → validation messages distinguish “required / not recorded” from “must be greater than zero” where applicable.
- Soft-delete of drafts vs approved records → drafts may soft-delete freely; approved records never hard-delete.
- Mixed currency aggregation with missing conversion rate → refuse the aggregation rather than inventing a rate.
- Notification without a natural deadline (informational only) → owner and link still required; deadline may be omitted only when the notification is explicitly non-actionable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST limit its base scope to recording and managing information inside Velora; ERP/legal accounting/Excel integrations are not base requirements of this feature.
- **FR-002**: Every managed project-management concept introduced by this work MUST map to data, an owner, a status, a business rule, a report surface, and an acceptance check where applicable.
- **FR-003**: Every durable record MUST have a unique identifier, created/updated timestamps, creator, last editor (when known), status (where the domain has status), and change history or equivalent audit trail.
- **FR-004**: Project-scoped records MUST be bound to their project unless they are intentionally organization-wide reference data.
- **FR-005**: Dates MUST be stored in a sortable standard form and presented with Jalali calendar in the UI; day boundaries MUST be consistent across reports.
- **FR-006**: Monetary amounts MUST display their currency unit; rial and toman MUST NOT be summed without an explicit conversion.
- **FR-007**: Final/approved records MUST NOT be physically deleted; soft-delete or corrective/reversal documents MUST be used.
- **FR-008**: Validation MUST apply on both client and server for fields touched by this feature.
- **FR-009**: Access MUST combine role and project scope; sensitive fields MUST be hidden from unauthorized users.
- **FR-010**: Forms and APIs MUST distinguish unset/not-recorded from zero, and unapproved from approved.
- **FR-011**: Notifications MUST include responsible party, deadline when actionable, and a direct record link.
- **FR-012**: A system administrator MUST be able to disable or mark optional a project capability without breaking overall project structure; historical data for disabled capabilities MUST remain.
- **FR-013**: Entering a transaction with a document/contract number that already exists MUST produce a warning before finalization.
- **FR-014**: Login, change, approval, and sensitive export events MUST continue to be auditable for surfaces touched by this feature.
- **FR-015**: After a fiscal period is closed, corrections MUST only proceed through an allowed, recorded path.
- **FR-016**: Product glossary terms for WBS, commitment, actual cost, IPC/صورت‌وضعیت, EV/PV/AC, risk vs issue, baseline, CBS, and OBS MUST be applied consistently in user-facing labels covered by this feature’s scope.
- **FR-017**: Implementation MUST follow TDD: failing automated tests first, then minimal code to pass, for each user story.

### Key Entities

- **Base system record**: Any durable entity with id, status (when applicable), creator/editor, timestamps, and soft-delete or corrective history.
- **Managed reference**: Units, statuses, cost codes, and similar catalogs read from manageable tables rather than scattered free text.
- **Project currency context**: Declared money unit for a project used when presenting and validating amounts.
- **Project capability setting**: Per-project enable/disable (or optional) flag for a named capability, preserving historical data when disabled.
- **Fiscal period lock**: Project- or organization-scoped closed period that restricts ordinary edits.
- **Actionable notification**: User-directed notice with responsible party, optional deadline, and deep link.
- **Glossary term binding**: Mapping from canonical term keys to localized labels used in UI/help text.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of glossary terms in the source vocabulary table that have a related UI surface in this feature’s scope use consistent labels (spot-check pass rate 100% on the agreed checklist).
- **SC-002**: In sampling of approved records covered by this feature, 0% physical deletes are observed after delete attempts.
- **SC-003**: In sample financial views covered by this feature, 0% unlabeled money amounts and 0% silent rial+toman mixes appear.
- **SC-004**: Unauthorized users fail to access out-of-project or out-of-role data in 100% of automated authorization tests for touched endpoints.
- **SC-005**: For representative numeric fields in scope, unset vs zero round-trips correctly in API and UI in 100% of automated cases.
- **SC-006**: 100% of actionable notifications created by this feature include responsible party and deep link; time-bound ones include deadline.
- **SC-007**: Disabling one optional capability on a sample project leaves unrelated flows operational and historical records readable.
- **SC-008**: All user-story acceptance scenarios have automated failing-then-passing tests before the story is marked done.

## Assumptions

- Existing JWT auth, project tenancy middleware, permission engine, audit middleware, and Jalali helpers are reused rather than reinvented.
- “Capability” for FR-012 means a named module/feature already present in Velora navigation (e.g., risk, economic, procurement), not inventing new domain modules in this feature.
- Project base currency defaults to IRR (rial) when unset historically; toman is treated as a distinct unit requiring explicit conversion (factor documented in plan/research).
- Fiscal period lock is project-scoped for v1 (not full multi-company accounting calendar).
- Duplicate-document warning is advisory (warn + confirm) unless an existing module already hard-blocks; this feature does not replace legal accounting uniqueness rules.
- ERP, formal accounting, tax, and Excel interchange remain out of scope.
- Specs 03–16 continue to own their domain entities; this feature only establishes shared cross-cutting rules and the minimum models/APIs needed to enforce them.
- No application code or migrations are written in the Spec Kit specify/plan/tasks pass; implementation starts only when `/speckit-implement` (or equivalent) is explicitly requested.
