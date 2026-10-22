# Feature Specification: Specialty Unit Reporting Source of Truth

**Feature Branch**: `032-unit-report-source-truth`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Correct specialty-unit daily reporting so each unit authors its report only on its own Specialty Units page, retire the standalone `/sub-reports` experience, and make eligible unit reports the sole source of the read-only project daily summary."

**Reference artifacts**:

- `reports_gaps/02/speckit-specify-prompts/01-DEPARTMENT-DAILY-SOURCE-OF-TRUTH.md` — controlling product decisions
- `reports_gaps/02/GAP-SPEC-02-DAILY-SECTIONS-GRID.md` — verified gap analysis and target boundary
- `specs/028-auto-daily-report-summary/` — historical baseline; superseded wherever it conflicts with this specification

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Author a unit report on its unit page (Priority: P1)

An authorized Buildings, Electrical, Mechanical, Machinery, Warehouse, or Security/HSE user opens that unit under the top-level “Specialty Units” menu, selects a date, and opens the current report for that project, date, and unit. If none exists, the user creates a draft there. The user edits the draft, submits it, and can see its state and audit history without leaving the unit page.

**Why this priority**: This establishes the correct and only operational authoring surface. Without it, the project continues to depend on the obsolete standalone workflow.

**Independent Test**: On the Buildings page, create a report for a selected date, edit and submit it, and verify the page shows the submitted state, last-change time, preparer, and submitter while a second active report for the same project, date, and unit cannot be created.

**Acceptance Scenarios**:

1. **Given** an authorized Buildings user and no current Buildings report for project P on date D, **When** the user selects D and creates the report, **Then** one draft report opens on the Buildings page and is identified as the current version for P, D, and Buildings.
2. **Given** a current draft or rejected unit report, **When** an authorized unit user changes its content, **Then** the changes are accepted and the last-change time and actor are updated.
3. **Given** a submitted or approved unit report, **When** a user attempts to edit its report content, **Then** the change is refused and the report remains unchanged.
4. **Given** a rejected report with a recorded reason, **When** an authorized unit user corrects it and resubmits it, **Then** its state becomes submitted and the prior state transitions remain available in history.
5. **Given** a current report already exists for P, D, and a unit, **When** another create attempt is made for the same combination, **Then** the existing current report is opened or returned and no duplicate active report is created.

---

### User Story 2 - Review unit reports with project-safe permissions (Priority: P1)

Authorized reviewers submit, approve, or reject unit reports according to distinct project permissions and the project’s segregation-of-duties rules. Unauthorized users and users from other projects cannot discover or act on the reports.

**Why this priority**: The report contains project-sensitive operational and contractual information. Moving the workflow must not weaken authorization or allow a preparer to bypass required independent review.

**Independent Test**: Exercise view, create/edit, submit, approve, and reject actions with users who have each required permission, a user prohibited by the project’s segregation rule, a user without permission, and a member of another project; verify only the authorized in-project actions succeed.

**Acceptance Scenarios**:

1. **Given** a user lacks the required project permission, **When** the user tries to view, create, edit, submit, approve, or reject a unit report, **Then** the attempted action is denied without revealing report content.
2. **Given** a user belongs to a different project, **When** the user addresses a report or source identifier from project P, **Then** the report is not disclosed and no action is performed.
3. **Given** a submitted report and an authorized approver who satisfies the project’s segregation-of-duties policy, **When** the approver approves it, **Then** the report becomes approved and the approver and approval time are recorded.
4. **Given** an actor who would violate the project’s segregation-of-duties policy, **When** that actor attempts approval, **Then** approval is denied and the state remains submitted.
5. **Given** an authorized reviewer rejects a submitted report, **When** the reviewer supplies a reason, **Then** the report becomes rejected and the reason, reviewer, and decision time are visible on the unit page.
6. **Given** an authorized reviewer attempts to reject without a reason, **When** the decision is submitted, **Then** the rejection is refused with actionable localized feedback.

---

### User Story 3 - Build the project summary from eligible unit reports (Priority: P1)

An authorized project user opens a project daily report and sees a read-only summary derived only from the current submitted or approved unit reports for the same project and date. The summary identifies which template-required units were expected, which contributed, and which are missing.

**Why this priority**: A trustworthy project daily report requires a single source of truth, exact date and project isolation, complete provenance, and truthful completeness status.

**Independent Test**: Submit and approve a Buildings report on the Buildings page for date D, rebuild or reopen D’s project summary, and verify its eligible rows appear read-only with the Buildings report, Buildings unit, and original source-row identifiers while an ineligible unit remains missing.

**Acceptance Scenarios**:

1. **Given** a Buildings report for P and D is approved on the Buildings page, **When** the project daily summary for P and D is opened or refreshed, **Then** the corresponding data appears read-only with provenance identifying the source unit report, Buildings unit, and source row.
2. **Given** a unit’s current report is draft or rejected, **When** the summary is rebuilt, **Then** none of that report’s data contributes and the unit remains listed as missing when required by the effective project template.
3. **Given** a submitted or approved report belongs to a different project or date, **When** P and D are summarized, **Then** that report contributes nothing.
4. **Given** every unit required by the project template effective for D has an approved current report, **When** the summary is evaluated, **Then** the expected and contributing sets match, the missing set is empty, and the report is not marked partial.
5. **Given** at least one template-required unit has no eligible current report, **When** the summary is evaluated, **Then** that unit appears in the missing set and the report is marked partial.
6. **Given** a total combines rows from multiple unit reports, **When** a reviewer inspects its provenance, **Then** every contributing report and row is retained; no later source replaces an earlier source in the provenance set.
7. **Given** authorized project-level management opinion, site-status, or weather overrides already exist, **When** the summary is rebuilt, **Then** those overrides remain unchanged.

---

### User Story 4 - Correct and rebuild without duplicates or stale data (Priority: P1)

A unit user corrects a rejected or superseded report and resubmits it. The project summary is rebuilt deterministically so the current eligible version replaces the previous contribution, while historical versions remain traceable.

**Why this priority**: Daily-report corrections are routine and may support contractual claims. Duplicate or stale contributions would make totals and provenance unreliable.

**Independent Test**: Start with a contributing unit report, reject or supersede it, change one source row, resubmit it, and run the same summary rebuild more than once; verify exactly one current contribution remains, the obsolete row is absent, and history still identifies prior versions.

**Acceptance Scenarios**:

1. **Given** an eligible unit report already contributes to a summary, **When** its current version becomes rejected, deleted, or superseded by an ineligible version, **Then** its prior contribution is removed on rebuild and the unit is treated as missing if required.
2. **Given** a corrected current version is submitted or approved, **When** the summary is rebuilt, **Then** its current rows replace obsolete rows and no stale or duplicate contribution remains.
3. **Given** no source data or project-level overrides change, **When** the summary is rebuilt repeatedly, **Then** the resulting summary content, counts, provenance, and completeness metadata remain the same.
4. **Given** older versions exist, **When** an authorized user reviews report history, **Then** the versions, state transitions, actors, timestamps, and rejection reasons remain traceable but only the current eligible version can contribute.

---

### User Story 5 - Retire the parallel standalone workflow (Priority: P1)

Users reach specialty reporting only from the relevant Specialty Units page. Navigation, calls to action, empty states, and the project daily-report area no longer expose the standalone `/projects/{projectId}/sub-reports` page or any raw project daily-report creation flow.

**Why this priority**: Leaving the old route accessible would preserve two competing workflows for the same business concept and undermine the source-of-truth correction.

**Independent Test**: Search all user-visible navigation and report entry points, then directly open the legacy route; verify no link or form exposes the old workflow and the project daily-report page offers no “New Report” action.

**Acceptance Scenarios**:

1. **Given** a user navigates through the product in either supported language, **When** the user inspects menus, daily-report calls to action, and empty states, **Then** none links to `/sub-reports` and specialty authoring is offered only through the corresponding Specialty Units page.
2. **Given** a user directly opens `/projects/{projectId}/sub-reports`, **When** the route resolves, **Then** the product shows its standard not-found state and no specialty-report form or report data.
3. **Given** a user opens the project daily-report area, **When** the available actions are displayed, **Then** there is no “New Report” action and no way to create a raw project-level daily report.
4. **Given** an internal legacy storage or service contract remains temporarily, **When** a product user follows any supported workflow, **Then** it is not exposed as a second authoring path.

---

### User Story 6 - Migrate legacy reports without losing history (Priority: P2)

Existing specialty reports are normalized into the canonical unit taxonomy and remain readable and traceable. Collisions caused by several legacy disciplines mapping to the same unit are resolved deterministically before the one-current-version rule is enforced, and operators have a documented rollback path.

**Why this priority**: The architecture cannot be corrected safely if valid historical reports, links, workflow decisions, or provenance are discarded.

**Independent Test**: Migrate a representative legacy dataset containing each legacy discipline, duplicate candidates for one canonical unit/date, historical states, and existing daily-summary links; verify all source records remain traceable, exactly one current version is selected per canonical key, links resolve to the unit history where possible, and rollback restores the pre-migration relationships.

**Acceptance Scenarios**:

1. **Given** valid legacy `civil`, `plumbing`, `hvac`, or `finishing` reports, **When** migration completes, **Then** they are mapped to the declared canonical unit, retain their original identifier and legacy-category evidence, and are readable from that unit’s report history.
2. **Given** multiple non-identical legacy reports map to the same project, date, and canonical unit, **When** normalization runs, **Then** all are preserved as versions, one current version is selected by the documented deterministic rule, and the resolution is auditable.
3. **Given** inconsistent legacy data would violate a new uniqueness or taxonomy rule, **When** migration is prepared, **Then** the inconsistency is normalized or explicitly quarantined before the rule is enforced.
4. **Given** existing links between legacy unit reports and project daily reports, **When** migration completes, **Then** stable identifiers and links continue to resolve where possible and all changed relationships are recorded in the migration trace.
5. **Given** the migration must be rolled back, **When** the documented rollback procedure is applied, **Then** original categories, current-version relationships, and report links can be reconstructed from the migration trace without losing source records.

### Edge Cases

- A project has no template effective for the selected date: unit reports may remain accessible to authorized users, but the summary must show a configuration-incomplete state and must not claim that the day is complete.
- A project template requires only a subset of the six canonical units: non-required eligible units may contribute, but they are not counted as missing and do not prevent completion.
- The required-unit template changes after historical reports exist: completeness is evaluated against the template version effective for the report date, so historical completeness does not silently change with today’s template.
- A report is deleted after contributing: its rows and provenance are removed from the next summary result while deletion history remains auditable.
- An eligible report has no detail rows: the unit still counts as contributing, and the empty report remains traceable; validation of detailed specialty sections is outside this feature.
- Two rebuild requests occur concurrently: they must converge on one summary result with no duplicated contribution and no loss of project-level overrides.
- A source row referenced by historical provenance is later corrected or removed: the current summary uses only current eligible source rows, while historical report versions preserve the prior evidence.
- A legacy record has an unknown or malformed discipline: it is quarantined for explicit resolution, remains readable to authorized migration operators, and is never silently assigned to an unrelated unit.
- A user can view the project daily summary but lacks unit-report permission: the user may view the summary according to project permissions but cannot use provenance links to bypass unit-report authorization.

## Requirements *(mandatory)*

### Functional Requirements

#### Canonical unit taxonomy

- **FR-001**: The product MUST use one canonical set of unit identifiers across Specialty Units navigation, unit-report ownership, permissions, project templates, completeness, provenance, and project daily summaries:

  | Canonical identifier | Display meaning |
  |---|---|
  | `buildings` | Buildings / ابنیه |
  | `electrical` | Electrical / برق |
  | `mechanical` | Mechanical / مکانیک |
  | `machinery` | Machinery / ماشین‌آلات |
  | `warehouse` | Warehouse / انبار |
  | `security` | Security/HSE / حراست و HSE |

- **FR-002**: Stable identifiers MUST remain language-independent, while unit names, states, validation feedback, and workflow actions MUST be presented correctly in Persian and English.
- **FR-003**: Project templates MUST declare which canonical units are required for dates on which that template is effective; required units MUST NOT be inferred from a hard-coded three-discipline default.
- **FR-004**: Legacy discipline values MUST map as follows for migration: `civil` and `finishing` to `buildings`; `plumbing` and `hvac` to `mechanical`; `electrical` to `electrical`; and legacy `mechanical` to `mechanical`. The remaining canonical units MUST be populated only from their matching unit data or an explicitly reviewed migration decision, never by guessing.
- **FR-005**: Legacy discipline labels MUST NOT remain selectable as additional product units after migration.

#### Unit report ownership and workflow

- **FR-006**: Each unit report MUST be owned by exactly one project, one report date, and one canonical unit.
- **FR-007**: For each project, date, and canonical unit, the product MUST expose at most one current active version while retaining all superseded versions and state history.
- **FR-008**: Unit report authoring and workflow actions MUST be available only on the corresponding unit page under the top-level Specialty Units menu.
- **FR-009**: An authorized user MUST be able to select a date on a unit page and open the current report or create a draft when no current version exists.
- **FR-010**: Unit reports MUST support `draft`, `submitted`, `approved`, and `rejected` states.
- **FR-011**: Only current reports in `draft` or `rejected` state MAY be edited; submitted and approved content MUST be immutable unless an authorized correction action establishes a new current editable version while preserving history.
- **FR-012**: Submission, approval, rejection, correction, and current-version replacement MUST record the acting user and time; rejection MUST additionally require and retain a reason.
- **FR-013**: The unit page MUST show current state, last-change time, preparer, submitter, approver when applicable, rejection actor and reason when applicable, and access to authorized version history.
- **FR-014**: View, create/edit, submit, approve, and reject actions MUST each enforce the corresponding project permission at the trusted authorization boundary.
- **FR-015**: Every unit-report lookup and mutation MUST enforce project membership and project scope; knowing a report or source identifier MUST NOT enable cross-project access.
- **FR-016**: Approval MUST enforce the project’s active segregation-of-duties policy and MUST NOT allow a prohibited preparer, submitter, or other conflicted actor to approve their own report.

#### Source of truth, aggregation, and completeness

- **FR-017**: Current unit-report data authored on Specialty Units pages MUST be the sole operational source for unit-derived content in the project daily summary.
- **FR-018**: A current unit report MAY contribute only when it belongs to the same project and date as the summary, has state `submitted` or `approved`, and is not deleted.
- **FR-019**: Draft, rejected, deleted, superseded, different-project, and different-date reports MUST contribute no rows, totals, narratives, or completeness credit.
- **FR-020**: The project daily summary MUST remain an automatically obtained, read-only consolidation for its date; product users MUST NOT create a raw project-level daily report or directly edit unit-derived rows there.
- **FR-021**: Every current derived row MUST retain the source unit-report identifier, canonical unit identifier, and source-row identifier.
- **FR-022**: Every derived total or combined value with more than one source MUST retain the complete set of contributing report and row references; source attribution MUST NOT use a last-source-wins rule.
- **FR-023**: Summary rebuilding MUST be deterministic, repeatable, and idempotent: the same current eligible sources and project-level overrides MUST produce the same derived content, provenance, and completeness result without duplicates.
- **FR-024**: A rebuild after rejection, deletion, correction, resubmission, approval, or current-version replacement MUST remove obsolete contributions before applying the current eligible contribution.
- **FR-025**: Rebuilding derived content MUST preserve authorized summary-owned information, including management opinion and explicit project-level site-status or weather overrides.
- **FR-026**: Each summary MUST report the canonical units expected by the template effective for its date, the units with current eligible contributions, the required units still missing, and whether the summary is partial.
- **FR-027**: A summary MUST be marked non-partial only when every unit required by the effective template has a current eligible report; non-required contributors MUST NOT be reported as missing.
- **FR-028**: If no effective project template can establish expected units, the summary MUST expose a configuration-incomplete state and MUST NOT claim completeness.

#### Retirement and compatibility

- **FR-029**: The product MUST remove the standalone `/projects/{projectId}/sub-reports` authoring experience from routes, navigation, calls to action, empty states, translations, and user-workflow tests.
- **FR-030**: Direct navigation to the legacy `/sub-reports` route MUST show the standard not-found experience and MUST NOT disclose reports or render any data-entry form.
- **FR-031**: The project daily-report experience MUST contain neither a “New Report” control nor a link to the legacy specialty-report route.
- **FR-032**: A temporarily retained legacy service or data structure MAY exist only as an internal compatibility detail, MUST NOT provide a parallel user authoring workflow, and MUST have an explicit retirement milestone recorded during planning.
- **FR-033**: Migration MUST preserve every valid legacy report, its stable identifier where possible, content, state and workflow history, original discipline evidence, actors, timestamps, rejection reason, source-row identity, and existing summary relationships.
- **FR-034**: Migration MUST normalize legacy taxonomy and duplicate-current inconsistencies before enforcing canonical taxonomy or one-current-version rules.
- **FR-035**: When multiple non-identical legacy reports map to the same canonical project/date/unit key, migration MUST preserve all as history and select the current version by latest business change time, using the stable legacy identifier as the deterministic tie-breaker; the choice and all displaced current markers MUST be recorded in an auditable migration trace.
- **FR-036**: Exact duplicate legacy records MAY be consolidated for current-state purposes only if every original identifier remains resolvable through the migration trace and no content or workflow evidence is lost.
- **FR-037**: Unknown or invalid legacy categories MUST be quarantined for explicit review rather than silently mapped or discarded.
- **FR-038**: Migration MUST define and verify a rollback that reconstructs original category values, current-version relationships, and summary links from the migration trace before irreversible cleanup occurs.

### Key Entities *(include if feature involves data)*

- **Canonical Specialty Unit**: One of the six stable unit identities used consistently by navigation, authorization, project templates, reporting, completeness, and provenance. Display labels are localized independently of the identifier.
- **Project Report Template**: The dated project configuration that declares which canonical units are required. It determines expected and missing units for each daily summary.
- **Unit Daily Report**: A project-, date-, and unit-scoped report with a current version, workflow state, audit actors and times, rejection information, and specialty-owned content. It is authored only from its unit page.
- **Unit Report Version**: An immutable historical view of a unit report’s content and workflow history. Exactly one version may be current for a project/date/unit key.
- **Unit Source Row**: A structured item within a unit report. Detailed contracts for labor, equipment, materials, concrete, and other specialty sections are intentionally deferred, but every item requires a stable source-row identity for provenance.
- **Project Daily Summary**: The automatically maintained, date-scoped, read-only project consolidation of current eligible unit reports plus separately authorized project-level information.
- **Derived Summary Item**: A row, narrative, or total copied or calculated from unit source rows. It carries complete provenance and is not directly authored on the project summary.
- **Completeness Snapshot**: The expected, contributing, and missing unit sets plus partial/configuration-incomplete state, evaluated from the project template effective for the report date.
- **Migration Trace**: An auditable relationship between every legacy identifier/category/current marker/link and its normalized canonical unit, version, and post-migration relationship; it supports traceability and rollback.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In end-to-end acceptance checks, all six canonical unit pages allow an authorized user to open or create that unit’s report for a date, and zero supported product flows offer a second specialty-report authoring location.
- **SC-002**: Across the mandatory permission matrix, 100% of unauthorized and cross-project attempts to view, create, edit, submit, approve, or reject unit reports are denied without report-content disclosure.
- **SC-003**: For representative dates containing eligible, draft, rejected, deleted, superseded, cross-project, and cross-date reports, 100% of summary contributions come only from current submitted or approved reports for the matching project and date.
- **SC-004**: Rebuilding the same summary at least three consecutive times with unchanged inputs produces identical content, row counts, provenance sets, completeness metadata, and project-level overrides, with zero duplicate derived items.
- **SC-005**: In correction tests, 100% of obsolete source contributions disappear after rebuild and 100% of current resubmitted contributions appear exactly once with correct provenance.
- **SC-006**: For projects with different required-unit templates, expected, contributing, and missing unit sets match the effective template in every acceptance case; a date is never reported complete while any required unit lacks an eligible report.
- **SC-007**: Product-wide navigation and direct-route checks in Persian and English find zero links, calls to action, empty-state prompts, or forms that expose `/sub-reports`; direct access displays the standard not-found state.
- **SC-008**: A migration rehearsal over representative legacy and inconsistent data accounts for 100% of source reports and source rows as migrated, historically retained, or explicitly quarantined; no valid record is silently dropped.
- **SC-009**: After migration, 100% of sampled legacy identifiers and existing summary links remain directly resolvable or traceable through the migration record, and the rehearsed rollback reconstructs their prior categories and relationships.
- **SC-010**: In usability checks, at least 90% of representative unit users can select a date, locate report status, submit a draft, and find rejection feedback on their first attempt without visiting the project daily-report page.

## Assumptions

- The existing top-level Specialty Units pages are the intended product locations for the six canonical units; this feature adds the unit daily-report framework there rather than creating another menu or page family.
- The display name “Security/HSE” uses the stable identifier `security` because that identifier already represents the combined organizational surface; this does not create a seventh HSE unit.
- A submitted report is operationally visible and may contribute before approval; an approved report remains eligible. This preserves the established daily visibility rule while still distinguishing approval state.
- The project’s segregation-of-duties policy already defines which actor combinations are prohibited. This feature requires that policy to be enforced consistently rather than defining a new organization-wide role model.
- If an approved report requires correction, the correction process preserves the approved version in history and establishes a current editable version; only the current version’s eligibility determines its contribution.
- Non-required canonical units may still submit reports and contribute when relevant, but completeness is determined only by the units required by the effective project template.
- Existing project-level management opinion, site-status override, and weather override remain summary-owned. Their detailed editing experience is outside this feature.
- Detailed data contracts and ownership rules for equipment, materials, concrete, labor, activities, issues, and visits are deferred to the next feature in this prompt series.
- Full project daily-report layout, spreadsheet parity, and printable output are deferred to the third feature in this prompt series.
- Implementation planning and tasks will encode each acceptance scenario as a failing behavioral test before the smallest production change that makes it pass.

## Dependencies

- Project membership, project-scoped report permissions, and segregation-of-duties policy must remain available as the authorization source.
- Project templates must support effective dating or equivalent historical resolution of required units.
- Existing project daily-summary creation/rebuild behavior and project-level overrides must remain available for integration.
- Migration rehearsal requires a representative copy or fixture set covering all legacy discipline values, duplicates, historical states, source rows, and summary links.

## Out of Scope

- Defining the complete fields, calculations, and validation rules for equipment, materials, concrete, labor, executed activities, general activities, issues, or visits.
- Completing the full project daily-report screen, Excel-equivalent layout, report numbering, approval footer, or printable/PDF output.
- Introducing a new raw project-level daily-report authoring workflow.
- Removing internal legacy storage immediately when it is still required for safe compatibility; its product exposure and parallel authoring workflow are in scope for removal.
