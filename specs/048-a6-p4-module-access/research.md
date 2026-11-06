# Research: A6-P4 module access

## 1. Observation vs write bypass

**Decision**: Keep `has_organizational_observation` as the only membership-free read exception (superuser or group `admin`). Stop treating `_is_global_admin` as a silent write/read bypass on remaining project consumers during this phase. Observation still does not grant wages, person/stakeholder contacts, file source ACL, or SoD break-glass.

**Rationale**: Constitution I and A6-P1 Clarification already named this exception. P1 traceability notes `_is_global_admin` still bypasses unselected modules until P4. Expanding observation would violate the 2026-11-06 instruction not to widen prior policy.

**Alternatives considered**: Leave `_is_global_admin` bypass everywhere. Rejected because it collapses observation into full project authority. Replace observation with membership-only. Rejected because customer already approved the bounded read exception.

## 2. Person directory and contact policy (PM-16)

**Decision**: Implement four separate server checks matching Clarification Q1. Add a project/org permission codename for person contacts, provisionally `view_person_contacts`, distinct from `view_sensitive_contacts`. `UserLookupView` requires active `manage_members` in a project context (or equivalent caller scope already used by the team screen), returns `user_id` and `full_name` by default, and only includes mobile/email when `view_person_contacts` is present. Roster serializers omit mobile/email unless that permission is present. Full organization directory stays behind the existing account-administration gate (`IsHrOrAdmin` / account-admin permission from P3), not HR title, staff, or project manager alone.

**Rationale**: Current `UserLookupView` returns email and mobile to any authenticated caller. Stakeholder ACL already uses `view_sensitive_contacts`; reusing it for people would violate Q1.4.

**Alternatives considered**: Reuse `view_sensitive_contacts` for people. Rejected by Q1. Limit lookup to current project members only. Rejected because Q1.3 allows searching assignable org accounts not yet on the project. Return hashed contact hints. Rejected as unnecessary complexity.

## 3. Nested sensitive redaction

**Decision**: Extend wage/sensitive redaction beyond top-level keys. Reuse and deepen `_redact_wage_fields` (and equivalent contact redactors) so nested dict/list payloads, exports, and drill responses apply the same permission set. Server responses are authoritative; UI hiding is not sufficient.

**Rationale**: Spec A6-R42 and historical note that catalog redaction only strips a top-level `wage` key.

**Alternatives considered**: Frontend-only masking. Rejected by Constitution I and Q1.4. Separate redactor per module with divergent rules. Rejected; prefer shared helpers with module registration of sensitive paths.

## 4. SoD break-glass and missing creator (PM-17)

**Decision**: Change `assert_not_self_final_approve` so null `created_by` no longer passes, and superuser no longer auto-bypasses. Callers that need break-glass must pass an explicit non-empty reason and a successful `record_access_change` (or equivalent durable audit write) before approve proceeds. Superuser must still be an active member with the normal approve permission for that project/record. Wire `approve_commitment` and any remaining final-approve paths that omit the helper. New SoD-covered creates, including import/background jobs, must set a real actor; system actors are labeled as system, not mapped to a human. Legacy null-creator rows cannot take the normal final-approve path until attribution is repaired with audit, or break-glass is used with reason `unknown_creator` / «ثبت‌کننده نامعلوم».

**Rationale**: Clarifications Q2 and Q3. Current helper explicitly no-ops on null creator and auto-passes superuser, which the customer rejected.

**Alternatives considered**: Keep automatic superuser bypass. Rejected. Allow admin group break-glass. Rejected by Q2. Auto-assign `created_by` to the approver to unblock legacy rows. Rejected by Q3.

## 5. Cross-project object binding

**Decision**: Enforce project consistency in `ProjectScopedViewSet`, serializers that accept related ids, and action endpoints. Reject foreign project ids on create/update/actions without creating partial relations.

**Rationale**: A6-R33. Existing helpers cover some paths; coverage is incomplete across modules.

**Alternatives considered**: Only filter querysets on list/retrieve. Rejected because writes can still bind foreign ids.

## 6. Alternate/legacy routes and offline revocation

**Decision**: Build an operation inventory from live URL/action maps per module area. Each alternate path must use the same permission helper as the canonical path. Offline/retry paths re-check current actor and effective permission; queued payloads stay with the original actor and are not submitted under a switched account.

**Rationale**: A6-R38 and A6-R35. Legacy inventory probes already showed main-route guards are not enough.

**Alternatives considered**: Document-only legacy warnings without tests. Rejected by package exit criteria.

## 7. Delivery packaging

**Decision**: Three sequential packages as in the spec. Package N+1 starts only after package N matrix rows are green or N/A with reason. Defect classes: policy, project-scope, sensitive-field, action/SoD, file, UI, queue/session.

**Rationale**: Prompt and implementation-phases require internal sequential delivery without claiming all 29 areas at once.

**Alternatives considered**: Big-bang across all modules. Rejected as unverifiable and high regression risk.

## Appendix: `_is_global_admin` write consumers (A6-P4 inventory)

Files still importing or defining `_is_global_admin` after package-2 close:

- `apps/api/core/permissions/project.py` (definition; write classes use observation / active membership)
- `apps/api/core/projects/serializers.py` (archive/completion restore remediation UI only)
- `apps/api/core/projects/status_undo_service.py` (undo-completion / resume — deliberate global-admin lifecycle ops)
- `apps/api/core/projects/lifecycle_service.py` (archive unlock — deliberate global-admin lifecycle ops)

Removed during A6-P4: `cash_flow/services/portfolio_access.py` (no longer uses global-admin bypass). Lifecycle archive/undo remains explicit admin, not module write observation.
