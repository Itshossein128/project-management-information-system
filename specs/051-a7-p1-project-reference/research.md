# Research: A.7-P1 Reference Project

## Decision 1 — Staff cannot create organization units

**Decision**: Keep the current write rule. An organization unit, contract type, or measurement unit can be created by a superuser or by a member of `admin`, `hr`, or `business-setup`. The staff marker alone does not qualify.

**Rationale**: Constitution 1.1.0 says the staff marker must not grant organization administration. `IsHrOrAdmin` already documents that bare staff does not qualify. `IsOrgRefWriterOrReadOnly` already calls that check and does not grant staff. The failing historical test `test_create_organization_unit_as_staff` expects HTTP 201. That expectation disagrees with the policy. The permission docstring still says staff may write; that sentence is the inconsistent explanation.

**Alternatives considered**: Granting staff write access would make the test pass and would weaken the approved access policy. Rejected.

## Decision 2 — Project contract type uses the catalog

**Decision**: A blank project contract type stays allowed. A newly set or changed value must be the code of an active managed contract type. An update that sends the value already stored may keep a legacy code that is not in the catalog.

**Rationale**: The create wizard already offers catalog codes. The project field is still free text, so an unknown code can be stored. Existing seeded values such as `lump_sum` must remain readable and unchanged. Contract records in the contracts app use a different type field and are not retargeted here.

**Alternatives considered**: A required foreign key with a data migration of every legacy string. Rejected for this phase because it rewrites stored projects and is larger than the proven gap.

## Decision 3 — Measurement units gain the same steward path

**Decision**: Authenticated users can keep reading measurement units. Stewards who may write organization references can create a unit with a name and an optional symbol. A blank name or a name that matches an existing unit, ignoring letter case, is refused.

**Rationale**: The catalog is readable and the progress screen can select a unit, but creation exists only outside the product's steward path. The audit asked for a usable path for the authorized steward. No schema change is required.

**Alternatives considered**: Leaving creation in the Django admin. Rejected because an allowed steward using the organization-references screen cannot add a unit there.

## Decision 4 — Project status stays the life cycle

**Decision**: Do not add a manageable status catalog for project status. The governed values remain draft, pending approval, active, suspended, completed, and archived. `handed_over` stays a legacy read synonym. Transitions stay in the existing project life-cycle and undo behavior from specs 008 and 026.

**Rationale**: FR-DATA-003 asks for manageable status catalogs. FR-PRJ-002 and the approved life cycle require defined transitions, confirmation, and roles. The phase instruction says not to turn the status enum into an open list. The life cycle wins. Manageable catalogs in this phase are organization unit, contract type, and measurement unit.

**Alternatives considered**: A status table edited from the organization-references screen. Rejected because a new status would have no transition rule.

## Decision 5 — Dynamic tables stay out of this journey

**Decision**: Do not add a dynamic-table workbook step to the reference project, and do not merge that workbook import with work-breakdown import.

**Rationale**: The audit says to exercise dynamic tables only if this reference journey really uses them. It does not. Existing workbook behavior remains owned by its current feature.

## Decision 6 — Schedule contract without importer changes

**Decision**: Do not change the importer. Record the SHA-256 and size of `real-data/plan.mpp` without modifying it. Author small XML and XER examples whose row and link counts are hand-counted from the file text. Record the 2026-11-10 probe as historical evidence with identifiers and causes. Those counts are not pass/fail targets.

**Rationale**: The phase owns the data contract. Import fidelity is a later phase. The parser's own output is not an independent golden file. The historical probe reported 80 parsed tasks (6 summary and 74 leaves), 83 predecessor links in the parsed source, 79 relations created, four predecessor warnings on task پایان (8055, 8084, 8102, 8120), and two zero-duration warnings on شروع and پایان. A later read-only MSPDI conversion of the unchanged employer file found those four UIDs among the 80 tasks with Summary=1. They are present summary tasks. The import activity map contains only leaves, which is why the historical warning said they were not found. They are not dangling identifiers, and the 83/79 counts stay historical rather than approved targets.

**Alternatives considered**: Re-running the importer and storing its output as the expected golden file. Rejected.

## Decision 7 — Preserve existing project and work-breakdown behavior

**Decision**: Do not add a parallel archive, undo, or template design. Regression coverage is the existing registration, charter, change-request, life-cycle, archive, undo, and work-breakdown tests, plus one reference scenario that binds identity, catalog choices, charter, and a three-level breakdown on a project coded `A7P1-REF`.

**Rationale**: The audit marks those areas as locally present and tested. This phase corrects proven gaps only.
