# Quickstart: Stakeholders, Documents, Decisions & Workflow

## Prerequisites

- Postgres + Redis running; API venv ready; root `.env` sourced
- Migrated DB after `projects` / `documents` / `workflow` FR-COL migrations
- Seeded project with at least two member users (different roles helpful), optional contract / activity / risk for link tests

## Backend verify

```bash
cd apps/api/core
set -a && source ../../../.env && set +a
../.venv/bin/python -m pytest \
  projects/tests/test_central_data_stakeholders.py \
  projects/tests/test_stakeholder_contacts_acl.py \
  projects/tests/test_communication_plan.py \
  documents/tests/test_documents.py \
  documents/tests/test_document_revision_retention.py \
  documents/tests/test_meeting_open_actions.py \
  documents/tests/test_correspondence_contract_link.py \
  workflow/tests/test_decision_rationale.py \
  workflow/tests/test_workflow_activate_gate.py \
  workflow/tests/test_workflow_reject_approve_log.py \
  -q
```

## Manual API smoke

1. `POST .../stakeholders/` with relationship_owner → appears in list; as viewer without contact permission → `email`/`phone` redacted.
2. `GET .../stakeholders/matrix/` → cells by influence×interest.
3. `POST .../communication-plans/` → listed for project.
4. `POST .../meetings/` then two `.../actions/` → `GET .../meeting-actions/open/` returns both.
5. Upload document v1 → revise to v2 → both revisions present with distinct `file_url`s (SC-004).
6. Document list `?status=&date_from=&date_to=` filters correctly.
7. Correspondence with `related_contract` same project → 201; foreign contract → 400.
8. `POST .../decisions/` without rationale → 400; with rationale + execution_owner → 201.
9. Create workflow definition with empty-approver stage → activate → 400 `incomplete_stages`.
10. Activate valid budget_change definition → start instance → reject → approve → `GET .../log/` shows full history (SC-003).

## UI

- Project → Stakeholders: owner field, redacted contacts, matrix view, communication plan.
- Project → Documents / Meetings: status/approver, revision history, structured actions, open-actions report.
- Project → Decisions & Workflow: decision form (rationale required), definition editor, instance actions + log (fa/en).

## Expected outcomes

| Check | Pass criteria |
|-------|----------------|
| SC-001 | Stakeholder, meeting actions, correspondence, versioned doc, decision creatable in-app |
| SC-002 | 100% pytest: blank rationale rejected; valid decision saved |
| SC-003 | Auditor can reconstruct reject then approve from action log |
| SC-004 | 100% pytest: prior revision row + file_url retained after revise |
| SC-005 | Stakeholder + meeting + two open actions visible on open report in &lt; 5 min |
| SC-006 | 100% pytest: activate blocked when a stage lacks approver |
