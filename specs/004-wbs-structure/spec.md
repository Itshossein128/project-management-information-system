# Feature Specification: WBS Structure

**Feature Branch**: `004-wbs-structure`

**Created**: 2026-10-08

**Status**: Draft

**Input**: User description: "Run specify, plan, and tasks for Velora Implementation Spec `04-ساختار شکست کار WBS.md` (FR-WBS). Do not implement."

**Source**: [04-ساختار شکست کار WBS.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/04-ساختار%20شکست%20کار%20WBS.md) (`FR-WBS`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [003-central-data-model](../003-central-data-model/spec.md), Implementation Specs 01–03

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Build a multi-level WBS tree (Priority: P1)

As a project manager or project controls engineer, I build a multi-level WBS from project root down to work packages, and I assign a responsible person and acceptance criteria on work-package nodes.

**Why this priority**: FR-WBS-001/002/004/005 and SC-WBS-001; without a controllable tree and work-package metadata, schedule, budget, and progress have no stable scope anchor.

**Independent Test**: Create at least three levels under an active project; set responsible and acceptance criteria on a leaf work package; confirm the tree shows parent/child and rejects a cycle.

**Acceptance Scenarios**:

1. **Given** an active project, **When** a node is created with display code, title, optional parent, description, responsible, acceptance criteria, and status, **Then** it appears in the project WBS tree at the correct depth.
2. **Given** an attempt to set a parent that would create a cycle, **When** the user saves or moves the node, **Then** the system rejects the change with a clear reason.
3. **Given** a work-package (leaf or designated control level), **When** responsible and acceptance criteria are set, **Then** they persist and are visible when viewing that node.

---

### User Story 2 - Protect nodes with dependencies (Priority: P1)

As a project controls engineer, I cannot delete a WBS node that already has cost, progress, or document dependencies; the system tells me why.

**Why this priority**: FR-WBS-006 / SC-WBS-002; silent or allowed deletes corrupt history for budget, progress, and documents.

**Independent Test**: Attach progress (or cost or document) to a node; attempt delete; assert rejection and that the node remains.

**Acceptance Scenarios**:

1. **Given** a node with recorded progress, cost, or a linked document, **When** delete is requested, **Then** the operation is rejected and the reason is stated.
2. **Given** a node with active children or attached schedule activities, **When** delete is requested, **Then** the operation is rejected (existing child/activity guards remain).
3. **Given** a leaf node with no dependencies, **When** delete is requested by an authorized user, **Then** the node is soft-deleted and codes are renormalized for remaining siblings.

---

### User Story 3 - Reusable WBS templates without silent rewrite (Priority: P2)

As a system administrator, I define reusable WBS templates for project types. After a template is applied to a project, later edits to the template do not silently rewrite that project’s WBS.

**Why this priority**: FR-WBS-007 / SC-WBS-003; templates speed setup but must not mutate live project scope without an explicit re-apply action.

**Independent Test**: Apply a template to Project A; change the template; confirm Project A’s WBS is unchanged unless the user explicitly re-applies.

**Acceptance Scenarios**:

1. **Given** a WBS template, **When** it is applied to a new project, **Then** a project-owned copy of the tree is created (codes, titles, hierarchy).
2. **Given** a project already populated from a template, **When** the template definition is edited, **Then** that project’s WBS does not change automatically.
3. **Given** an explicit re-apply (if offered), **When** the user confirms, **Then** the outcome is intentional and auditable (not a silent background rewrite).

---

### Edge Cases

- Moving a node under a new parent recalculates depth/path and display codes; cycles remain forbidden.
- Project with zero work packages: warn when opening dependent capabilities (schedule/progress) that expect WBS packages.
- Soft-deleted codes must not collide with active unique codes within the project.
- Empty acceptance criteria or unset responsible are allowed on non–work-package levels; work packages SHOULD prompt for them when used for progress/budget (warning, not hard block in v1 unless already enforced elsewhere).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: WBS MUST be a multi-level tree; highest level represents project scope breakdown and lower levels may represent phase, deliverable, and work package (semantic levels may be inferred from depth or an optional level label).
- **FR-002**: A work package MUST be the controllable level where responsible person, duration/budget linkage (by later modules), and completion criteria can be attached.
- **FR-003**: WBS MUST NOT be treated as a daily activity list or as a cost-only classification (CBS remains separate per FR-DATA / glossary).
- **FR-004**: Each node MUST support identity, display code, title, description, parent, depth/level, responsible, acceptance criteria, and status.
- **FR-005**: The system MUST enforce unique display codes within a project, valid parent/child links, and cycle prevention on create/move.
- **FR-006**: Deleting a node that has cost, progress, or document dependencies MUST be forbidden; children and attached activities MUST also block delete.
- **FR-007**: Reusable templates are allowed; after application to a project, template edits MUST NOT silently change that project’s WBS.
- **FR-008**: Soft-delete and audit patterns from core principles MUST apply to WBS mutations (who/when; recoverable tombstone where already used).

### Key Entities

- **WBS Node**: Hierarchical scope element with code, name, parent, depth, optional weights, responsible, acceptance criteria, status.
- **Work Package**: Controllable leaf (or designated) node used for ownership and completion criteria; later linked to activities/budget/progress.
- **WBS Template**: Reusable hierarchical definition copied into a project on apply; project tree is owned by the project after copy.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A project controls user can create a ≥3-level WBS and set responsible plus acceptance criteria on a work package in one uninterrupted session.
- **SC-002**: In 100% of test cases, delete of a node with progress, cost, or document dependency is rejected with an explicit reason.
- **SC-003**: After template apply, editing the template leaves the previously applied project WBS unchanged in 100% of automated checks (unless explicit re-apply is performed).
- **SC-004**: Cycle create/move attempts are rejected in 100% of automated checks.

## Assumptions

- Detailed schedule activities, baselines, and network logic belong to Implementation Spec 05 (out of scope here except activity FK delete guard).
- Budget line creation belongs to Spec 09; this feature only blocks WBS delete when cost rows already reference the node.
- Document linkage uses the existing project documents model/app when present; if no document↔WBS FK exists yet, define a minimal check path or attachment metadata hook in plan.
- Existing `project_templates` copy-on-apply is the intended template mechanism; this feature verifies and closes any silent-rewrite gaps.
- Display codes may be user-supplied on create and/or renormalized after structural moves (current product behavior); uniqueness within project is mandatory either way.
- Soft-delete (not hard delete) remains the default destructive path for WBS nodes.
- CBS is not part of this feature’s tree (already in 003).
