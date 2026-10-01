<!--
Sync Impact Report
- Version change: (none / template scaffold) → 1.0.0
- Modified principles: N/A (initial ratification; replaced template placeholders)
- Added sections:
  - Core Principles I–VII (authorization, data integrity, bilingual UX,
    safe mutations, minimal changes, evidence-based verification,
    accessible construction-management UX)
  - Architecture and Development Constraints
  - Quality Gates
  - Governance
- Removed sections: none (template placeholders only)
- Follow-up TODOs: none
-->

# Building Management Constitution

## Core Principles

### I. Server-Enforced Authorization and Tenant/Project Isolation

Authentication alone is NEVER sufficient authorization. Every project-scoped
read or mutation MUST verify membership and the required project permission
server-side. Client-side permission checks are UX only and MUST NOT be treated
as the security boundary. Resource resolution MUST go through the authorized
project scope to prevent IDOR (insecure direct object reference).

**Rationale**: Construction data is multi-tenant and permission-sensitive;
leaking or mutating another project's records is an unacceptable failure mode.

### II. Data Integrity and End-to-End Domain Consistency

Changes to domain fields—especially project, WBS, activity, department,
procurement, and reporting data—MUST be traced across database models,
migrations, serializers, APIs, UI, imports, exports, PDF output, and tests.
Migrations MUST preserve valid existing data or provide an explicit migration
and rollback strategy. Hierarchical WBS codes MUST preserve uniqueness and
consistency during renumbering; use safe staged updates when a direct update
could violate uniqueness constraints.

**Rationale**: Domain fields flow through many surfaces; a partial update
creates silent inconsistency that is expensive to detect in production.

### III. Bilingual and Locale-Correct Experience

User-facing text, validation errors, dates, and status values MUST work
correctly in Persian and English. Permission codes and stable API identifiers
MUST remain language-independent; only presentation is localized. Date-picker
and calendar changes REQUIRE real UI verification in both Persian and English,
including reopen and persistence behavior.

**Rationale**: The product is bilingual by design; locale bugs block operational
users and undermine trust in status and scheduling data.

### IV. Explicit, Safe Business Mutations

Destructive actions, bulk updates, approval decisions, imports, exports, and
project deletion MUST have clear authorization, validation, recoverability
where appropriate, and understandable localized feedback. Irreversible
production-like actions MUST NOT be executed merely to validate an
implementation without explicit authorization. When undo is offered, its scope,
time limit, unsupported cases, and server-side restore behavior MUST be
explicit and tested.

**Rationale**: Operational mistakes and unsafe “try it live” verification can
destroy project history that cannot be reconstructed.

### V. Minimal Coherent Changes

Prefer the smallest change that meets the approved requirement. Extend
established models, services, serializers, components, and localization
systems instead of creating parallel implementations. Unrelated refactors and
speculative abstractions MUST be avoided.

**Rationale**: Parallel paths and drive-by refactors raise review cost and
increase the chance of incomplete localization, permission, or data-path
coverage.

### VI. Evidence-Based Verification

Completion MUST NOT be claimed from source inspection, typechecking, or one
narrow test alone. State what was verified and distinguish backend tests,
frontend typechecks, API integration tests, browser E2E tests, migration
checks, and live-environment evidence. Relevant checks MUST run against the
final changed tree. Use pytest for Django tests and preserve the project's
pinned Django 4.2 dependency boundary.

**Rationale**: Narrow green signals create false confidence; verification
claims must match the evidence actually collected.

### VII. Accessible, Practical Construction-Management UX

Forms and tables MUST provide clear validation, localization,
keyboard-accessible interaction, and feedback suitable for operational users.
Searchable creatable selects MUST place their Add action inside the opened
menu. Derived values, such as WBS child codes, SHOULD be auto-filled and
protected from accidental manual edits when the domain rules require
derivation.

**Rationale**: Field and office users need fast, unambiguous UIs; broken
selects and editable derived fields cause data-entry errors at scale.

## Architecture and Development Constraints

- Preserve the pnpm monorepo structure and the boundary between `apps/api`
  (Django 4.2 + Django REST Framework) and `apps/web` (React Router 7 + Vite +
  TypeScript). Cross-app coupling MUST go through documented APIs and shared
  contracts, not ad-hoc file sharing of runtime code.
- Do NOT upgrade Django outside the approved compatibility range as a side
  effect of installing development dependencies. The pinned Django 4.2 line is
  a hard runtime boundary.
- PostgreSQL and Redis are required for normal development and tests.
  Asynchronous integrations (e.g., RabbitMQ, Celery, MinIO) are
  environment-dependent. Documentation and verification reports MUST state what
  local tests do and do not prove when those services are unavailable.
- Product scope includes projects, WBS hierarchies, activities, departments,
  procurement, reports, permissions, imports/exports, and PDFs. Changes in one
  of these areas MUST account for dependent surfaces listed under Principle II.

## Quality Gates

- Focused backend and/or frontend tests MUST cover changed behavior before
  claiming completion.
- Model changes REQUIRE migration verification (apply, data preservation or
  documented strategy, and rollback awareness where applicable).
- User-visible interaction changes REQUIRE browser verification, including
  bilingual checks when locale-sensitive (see Principle III).
- Documentation MUST be updated when behavior, permissions, imports/exports, or
  operational setup changes.
- Verification reports MUST name the evidence categories used (Principle VI)
  and MUST NOT equate a single pass (e.g., typecheck only) with full
  completion.

## Governance

This constitution supersedes feature-level plans, specs, and tasks where they
conflict. AGENTS.md and other project documentation remain implementation
guidance and operational detail, but MUST NOT weaken these principles.

Amendments REQUIRE:

1. Rationale for the change
2. Affected areas (domains, apps, environments)
3. Migration and compatibility impact
4. Verification evidence appropriate to the change

Versioning follows semantic versioning for governance:

- MAJOR: backward-incompatible principle removals or redefinitions
- MINOR: new principle/section or materially expanded guidance
- PATCH: clarifications, wording, and non-semantic refinements

Compliance reviews for PRs and feature work MUST check alignment with these
principles, Architecture and Development Constraints, and Quality Gates.

**Version**: 1.0.0 | **Ratified**: 2026-10-01 | **Last Amended**: 2026-10-01
