# Research: Stakeholders, Documents, Decisions & Workflow

**Date**: 2026-10-09

## Findings

### Existing coverage (keep)

- `projects.Stakeholder`: name, organization, role, email, phone, influence/interest (1–5), communication_need, status; CRUD under `/projects/{id}/stakeholders/` with `view_project` / `edit_project`.
- `documents.ProjectDocument` + `DocumentRevision`: upload, revision upload, access_level (public/project/restricted), filters (type, discipline, activity, wbs, search); permissions `view_documents` / `upload_documents`.
- `documents.Correspondence`: number, type, parties, dates, status, file, optional related document/activity; `view_correspondence` / `edit_correspondence`.
- `documents.MeetingMinutes`: date, type, attendees, agenda, free-text `decisions` + `action_items`.
- Web: `project-stakeholders.tsx`, `project-documents.tsx`, `lib/api/documents.ts`.
- Domain-specific approvals elsewhere (project change request, daily-report approve, IPC approve, etc.) — **not** a shared configurable engine.
- `common.WorkflowViewSetMixin` only exposes submit/approve/reject hooks for ViewSets; not a definition/instance engine.
- Alerts app includes correspondence response-due style codes — reusable for overdue workflow stages.

### Gaps to close

1. Stakeholder missing **relationship owner**; no **communication plan**; no matrix read API; contact fields always returned.
2. Meeting actions are free text — no owner/due/status, no open-actions report.
3. Documents lack first-class **status** / **approver**; filters missing date/status; revision retention not explicitly guaranteed/tested as FR.
4. Correspondence missing **contract** link.
5. No **management decision** entity with mandatory rationale and impact links.
6. No configurable **workflow definition / instance / action log**.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bounded contexts | Extend **`projects`** (stakeholders, communication plan) + **`documents`** (docs, corr, meetings/actions); new **`workflow`** app for engine + management decisions | Principle V for collab surfaces; shared motor must be importable by cost/contracts/procurement/risk without depending on `documents` |
| Relationship owner | FK `relationship_owner` → User (nullable allowed for draft; recommended) | FR-001 |
| Sensitive contacts | Server-side redact `email`/`phone` unless caller has `view_sensitive_contacts` **or** `edit_project`; add `view_sensitive_contacts` to PM + document_controller defaults | FR-013; constitution I; hide rather than 403 entire stakeholder list |
| Communication plan | New `CommunicationPlan` model on project (audience, message, channel/type, frequency, owner) | FR-002 |
| Influence–interest matrix | Read-only `GET .../stakeholders/matrix/` grouping by influence×interest buckets (1–5); no separate table | FR-002 |
| Meeting actions | New child `MeetingAction` (description, owner, due_date, status open/done); keep free-text `action_items` for backward compat; open-actions report reads child rows only | FR-003, SC-005 |
| Document versioning | On revise: append `DocumentRevision`, update current pointer fields; **never** delete prior revision row or its `file_url`; pytest asserts retention | FR-005, SC-004 |
| Document FR fields | Add `status` enum + `approver` FK (User, nullable); ensure `doc_code` uniqueness per project when set; filters `status`, `revision_date`/`date_from`/`date_to` | FR-005, FR-014 |
| Correspondence contract | Optional FK `related_contract` → contracts model, same-project validation | FR-004 |
| Management decision | Model in `workflow` app: required `rationale`, project FK required, optional risk/activity/contract FKs, impact flags, execution owner/due/status | FR-006–007, SC-002 |
| Workflow definition | Project-scoped `WorkflowDefinition` + ordered `WorkflowStage`s; `workflow_type` enum covering sample kinds; `status` draft/active/retired | FR-008–010 |
| Approver binding | Stage `approver_user` **or** `approver_role` (project role codename); at least one required to activate | FR-008, FR-015 |
| Multi-approver | Stage `approval_mode`: `all` \| `any`; concurrent assignees resolved from role members when role set | FR-009 |
| Reject / return | Stage `on_reject`: `stop` \| `return_previous` \| `return_to` (stage index); instance status + log every transition | FR-008, SC-003 |
| Instance subject | Generic `subject_type` + `subject_id` (UUID) + optional `subject_app_label`; v1 sample `budget_change` may point at `ProjectChangeRequest` or a lightweight demo subject created in tests | FR-010 without rewriting cost module |
| Action log | Append-only `WorkflowActionLog` (actor, at, action, from_status, to_status, comment, stage) | FR-011 |
| Overdue stages | Instance stage `due_at`; list filter `overdue=true`; emit alert via existing alerts patterns when due passes (best-effort if Celery eager) | Edge case |
| Permissions | Documents/corr/meetings keep existing codes; decisions/workflow use `view_documents`+`upload_documents` for v1 **or** `edit_project` for definition activate — prefer: `view_documents` read decisions/instances; `edit_project` manage definitions + decide; document_controller can upload docs but not activate workflows | Minimal new codes (`view_sensitive_contacts` only) |
| Consumer domains | Document attachment contract in `contracts/decisions-workflow.md`; do **not** fully rewire IPC/payment/inspection in this feature | Spec assumption phase-1 |
| UI | Extend stakeholders + documents; meetings actions + open report; new Decisions & Workflow project route | Matches user stories |

## Alternatives considered

- **Single new `collaboration` Django app** migrating documents/stakeholders — cleaner long-term name; rejected for v1 migration cost and Principle V.
- **Engine inside `documents`** — rejected (circular / wrong dependency for cost & procurement).
- **Engine only as mixin on each ViewSet** — fails configurable multi-stage + concurrent approvers (FR-008–009).
- **Hard 403 on stakeholder retrieve without contact permission** — worse UX for matrix/list; rejected for field-level redact.
- **Org-global workflow templates only** — weaker project isolation; rejected; v1 project-scoped definitions (templates can be copied later).
- **Require wiring all six sample subject types in this feature** — exceeds phase-1 assumption; rejected in favor of engine + one budget-change sample.

## NEEDS CLARIFICATION

None remaining — Technical Context unknowns resolved above.
