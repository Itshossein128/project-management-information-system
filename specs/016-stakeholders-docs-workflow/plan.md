# Implementation Plan: Stakeholders, Documents, Decisions & Workflow

**Branch**: `016-stakeholders-docs-workflow` | **Date**: 2026-10-09 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/016-stakeholders-docs-workflow/spec.md` (FR-COL gap closure)

## Summary

Close FR-COL gaps on existing collaboration surfaces: complete the **stakeholder** register (relationship owner, sensitive-contact gating, influence–interest matrix), add a **communication plan**, turn meeting minutes into **structured actions** with an open-actions report, finish **document** identity/status/approver and non-destructive versioning, extend **correspondence** with contract links, introduce first-class **management decisions** with mandatory rationale, and ship a **shared configurable workflow engine** (definition → instance → action log) that other domains can consume—starting with one end-to-end sample (budget-change approval)—without building separate per-domain engines.

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2), TypeScript (React Router 7)  
**Primary Dependencies**: DRF, drf-spectacular, TanStack Query; apps `projects`, `documents`, new `workflow`; consumers later from `cost_control` / `contracts` / `procurement` / `risk` (read-only wiring of one sample in v1); project tenancy + existing document/correspondence permissions  
**Storage**: PostgreSQL (UUID PKs); extend `Stakeholder`, `ProjectDocument` / `DocumentRevision`, `Correspondence`, `MeetingMinutes`; new tables for communication plan, meeting actions, management decision, workflow definition/stage/instance/log; soft-delete via existing audit base where applicable  
**Testing**: pytest + pytest-django per gap (stakeholder contacts ACL, open actions, revision retention, decision rationale, workflow activate/reject/approve/log); UI smoke on stakeholders, documents, decisions/workflow panels  
**Target Platform**: Velora monorepo (`apps/api/core`, `apps/web`)  
**Project Type**: Web + API monorepo  
**Performance Goals**: List/filter O(project rows) with indexed project FKs; open-actions and overdue-stage queries filterable by status/due date; workflow action log append-only  
**Constraints**: Project tenancy + server-side membership; bilingual labels; never physically delete prior document file content on revise; decision rationale required; workflow activation blocked if any stage lacks approver; sensitive contact fields redacted without permission  
**Scale/Scope**: Extend `projects` + `documents`; add `workflow` app for engine + decisions; deepen existing stakeholder/documents UI; add decisions/workflow + open-actions surfaces; wire one sample workflow type end-to-end

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status |
|-----------|--------|
| I. Server-enforced authz / project isolation | Pass — all routes under `/projects/{uuid}/` (plus project-scoped workflow definitions); reuse `IsProjectMember` + `HasProjectPermission`; redact contacts server-side; FK targets same-project |
| II. Data integrity end-to-end | Pass — migrations for new fields/entities; revisions append-only; free-text meeting actions dual-kept until structured rows exist; workflow log immutable append |
| III. Bilingual UX | Pass — new status/type/empty-state strings in `en.json` / `fa.json` |
| IV. Explicit safe mutations | Pass — soft-delete retained; document revise does not wipe prior versions; workflow reject/return recorded; no silent delete of audit history |
| V. Minimal coherent changes | Pass — extend `projects`/`documents`; one new `workflow` app only for the shared motor + decisions (not a second documents stack) |
| VI. Evidence-based verification | Pass — pytest suites named in quickstart; UI smoke after API green |
| VII. Accessible practical UX | Pass — open-actions report, clear validation on rationale/activate, matrix grouping without fake data |

**Post-Phase 1 re-check**: Pass — design is additive on existing collab surfaces plus one bounded `workflow` context; sample budget-change uses generic subject binding so cost/budget domains remain owners of their content; no parallel per-domain engines.

## Project Structure

### Documentation (this feature)

```text
specs/016-stakeholders-docs-workflow/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── stakeholders-meetings.md
│   ├── documents-correspondence.md
│   └── decisions-workflow.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source Code (touched)

```text
apps/api/core/projects/
  models.py                         # Stakeholder.relationship_owner; CommunicationPlan
  stakeholder_views.py / serializers
  services/communication_plan_service.py   # NEW (optional thin)
  migrations/00xx_fr_col_stakeholders.py
  tests/test_stakeholder_contacts_acl.py
  tests/test_communication_plan.py

apps/api/core/documents/
  models.py                         # MeetingAction; document status/approver; corr.contract
  serializers.py / views.py / urls.py
  services/document_service.py      # non-destructive revise guarantees
  services/meeting_action_service.py
  migrations/00xx_fr_col_docs.py
  tests/test_document_revision_retention.py
  tests/test_meeting_open_actions.py
  tests/test_correspondence_contract_link.py
  ENDPOINTS.md

apps/api/core/workflow/            # NEW Django app
  models.py                         # Definition, Stage, Instance, ActionLog, ManagementDecision
  serializers.py / views.py / urls.py
  services/definition_service.py    # activate validation
  services/instance_service.py      # approve / reject / return / advance
  services/decision_service.py      # rationale required
  migrations/0001_initial.py
  tests/test_decision_rationale.py
  tests/test_workflow_activate_gate.py
  tests/test_workflow_reject_approve_log.py
  apps.py / ENDPOINTS.md

apps/api/core/config/               # register workflow app + urls
apps/api/core/permissions/constants.py  # view_sensitive_contacts (or document reuse)

apps/web/src/
  app/lib/api/documents.ts          # extend filters, status, revisions
  app/lib/api/stakeholders.ts       # owner, matrix, contacts shaping
  app/lib/api/workflow.ts           # NEW: decisions + definitions + instances
  app/routes/project-stakeholders.tsx
  app/routes/project-documents.tsx
  app/routes/project-meetings.tsx          # or tab: structured actions + open report
  app/routes/project-decisions-workflow.tsx # NEW
  components/collab/... / workflow/...
  locales en.json / fa.json
  app/routes.ts / routeVars.ts / project-navigation.config.ts
```

**Structure Decision**: Keep stakeholders in `projects` and documents/meetings/correspondence in `documents` (Principle V). Put the **shared workflow engine and management decisions** in a new `workflow` app so cost/contracts/procurement/risk can depend on one motor without importing `documents`. UI: deepen existing stakeholder/documents routes; add open-actions + decisions/workflow project surfaces. Phase-1 delivery may land collab registers before wiring every sample subject type; engine + budget-change sample remain in scope for SC-003.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| New `workflow` Django app | Shared motor must be importable by multiple domains without circular deps on `documents` | Putting engine inside `documents` couples procurement/cost to document models; one-off approve endpoints fail FR-COL-008–010 |

## Implementation Phases

1. **P1 Stakeholders & meeting actions** — relationship owner, contact ACL, communication plan + matrix read, structured `MeetingAction`, open-actions report, UI (FR-001–003, 013; SC-001, SC-005).
2. **P1 Documents & correspondence gaps** — doc status/approver/filters, revision retention tests, contract link on correspondence (FR-004–005, 014; SC-004).
3. **P1 Decisions + workflow engine** — ManagementDecision (rationale required), definition/stage/instance/log, activate gate, reject→return then approve sample, budget-change subject binding (FR-006–011, 015; SC-002–003, SC-006).
4. **P2 Polish & consumer readiness** — locales, ENDPOINTS.md, nav, overdue-stage notification hook into alerts if available; document how other domains attach subject types (no full IPC/payment wiring in this feature).
