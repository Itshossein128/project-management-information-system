# Implementation Plan: Restore Project from Archive

**Branch**: `main` (actual Git branch; no new branch) | **Date**: 2026-10-16 | **Spec**: [spec.md](spec.md)

**Input**: `specs/008-project-registration/restore-project-archive/spec.md`
**Feature Directory**: `specs/008-project-registration/restore-project-archive`
**Spec Kit logical feature key**: `restore-project-archive` (setup output labels this BRANCH; it does not mean Git switched branches).

**Status**: Phase 0 research and Phase 1 design complete. This invocation creates planning documents only. The spec's earlier “no plan in this stage” refers to the completed specify invocation; the user's current `/speckit-plan` request authorizes these design artifacts. No tasks, source code or migrations are created or executed.

## Summary

Extend the existing project lifecycle with a global-admin-only restoration action in overview. Capture the origin and unique archive cycle at archive time; preview the exact project/target/effects, require a reason and recheck current readiness only for active target. Use a signed confirmation context, monotonic project revision and immutable per-cycle success receipt to make stale confirmations, transport retries and concurrent requests safe. Restore, receipt and semantic audit commit together under the Project row lock. Existing writers that can overwrite this state adopt the same fresh-row convention without changing their lifecycle rules.

Two necessary integrations are explicit: archived missing scope/amount must be completable through the existing approved change-request workflow, and restoration history needs a narrow read-only overview/API surface because no generic audit browser currently exists. Preserve all prior data, approvals and parent artifacts. Old development data needs no restoration compatibility or inferred destination.

## Technical Context

**Language/Version**: Python with pinned Django 4.2.11; TypeScript ~5.9, React 19, React Router 7.12 and Vite 7 as declared in current manifests. Planning runtime exists; exact deployed interpreter/package versions were not probed.

**Primary Dependencies**: Existing DRF, PostgreSQL/psycopg, Django signing/transactions/gettext; React Query, i18next, existing dialog/forms and user lookup. No new external package or service.

**Storage**: Existing PostgreSQL Project with three added metadata fields; new narrow `ProjectArchiveRestore` receipt; existing AuditLog reused synchronously for this business action. Redis remains an application prerequisite, not the idempotency source.

**Testing**: pytest/pytest-django with real PostgreSQL transactions and independent connections; focused migration/fault/preservation checks; frontend typecheck; intercepted Playwright UX checks plus separate real API/browser integration in Persian and English, desktop and mobile.

**Target Platform**: Existing bilingual web application and Linux-hosted API.

**Project Type**: Existing pnpm frontend/backend monorepo.

**Performance Goals**: Preview/history require bounded project/receipt queries, with history default page 50/max 100. A normal uncontended preview or restore should complete within 2 seconds at p95 in the local integration test environment (record hardware/sample count). Do not hold database locks during external I/O; same-project contention may wait for the current short transaction. This is a planning target, not measured evidence.

**Constraints**: Global administrator only; known active/suspended/completed origin; current activation helper reused unchanged; no budget restamp, financial execution, approval replay, legacy-origin backfill or status-PATCH bypass. Preserve pre-existing dirty activation work and all parent docs/tasks. No database resets in planning. Existing Django pin remains.

**Scale/Scope**: One lifecycle action, preview/result/history interfaces, three destinations, two frontend locales, small overview dialog/history and narrowly reachable existing remediation flows. Schema/query design scales history by pagination and indexed project/cycle/request lookups; no arbitrary user-volume claim is introduced.

## Constitution Check

Pre-research gate reviewed against `.specify/memory/constitution.md`; post-design gate re-evaluated against the contracts and data model. PASS here means design alignment, not runtime test completion.

- **I — Authorization/isolation: PASS before and after.** Global-admin authority is enforced server-side in view/service; project scope remains authoritative. Nonmember global-admin access follows the existing explicit bypass and user requirement; project-only permissions cannot restore. History uses existing view authority.
- **II — Integrity/domain consistency: PASS before and after.** Lock/reload all participating Project writers; version and cycle distinguish context; status/receipt/audit are one atomic unit. Schema migration/reversal and valid project data preservation are required in implementation. User's explicit waiver permits recreating old unknown-origin development data; no compatibility backfill or hidden reset is planned. No constitution file is amended.
- **III — Bilingual: PASS before and after.** Stable machine codes, fa/en interface labels/errors and Persian backend catalog, with real browser verification planned in both locales.
- **IV — Safe mutations: PASS before and after.** Fixed destination and effects shown before reason/confirmation; cancellation scope explicit; uncertain network outcome stays uncertain until evidenced. No elapsed-time undo limit; confirmation is valid only for its unchanged context. Required audit failure rolls back; no destructive validation runs now.
- **V — Minimal coherent change: PASS before and after.** Extend existing lifecycle/Project/CR/dialog/audit modules. One durable receipt is justified by retry after later archive cycles; no generic engine. Scoped CR availability preserves approved-field and SoD controls.
- **VI — Evidence: PASS before and after.** TDD and real transactional/browser/migration proof are specified separately; intercepted tests do not stand for backend proof. This plan reports source/design validation only.
- **VII — Accessible practical UX: PASS before and after.** Existing accessible dialog, RTL/LTR, keyboard focus, inline reason validation, all missing prerequisites and executable completion paths.

No unjustified violation or unresolved design question remains. Implementation gates remain pending actual tests.

## Project Structure

### Documentation (this feature)

```text
specs/008-project-registration/restore-project-archive/
├── spec.md                        # preserved from specify
├── checklists/requirements.md     # preserved requirements-quality review
├── plan.md                        # this plan
├── research.md                    # Phase 0 decisions/evidence
├── data-model.md                  # Phase 1 state/constraints/migration strategy
├── quickstart.md                  # Phase 1 future validation guide
└── contracts/
    ├── restore-api.md             # preview, mutation, recovery, history
    └── restore-ui.md              # dialog, remediation, bilingual states
```

`tasks.md` is deliberately absent; it belongs to a later `/speckit-tasks` invocation in this subdirectory. Do not reuse or reopen `../tasks.md` for this extension.

### Source Code (repository root; proposed implementation touchpoints)

```text
apps/api/core/
├── projects/
│   ├── models.py                   # metadata and success receipt
│   ├── lifecycle_service.py        # archive/restore/preview and fresh locks
│   ├── change_request_service.py   # targeted writes and narrow remediation access
│   ├── serializers.py             # contextual restore/support/CR actions, request/receipt shapes
│   ├── views.py / urls.py          # explicit scoped interfaces, locked PATCH/delete
│   ├── migrations/                # new migration only
│   └── tests/                     # proposed restore/transaction/preservation tests
├── audit/middleware.py            # narrow explicitly-audited request marker
├── audit/service.py               # reuse direct persistence helper
├── permissions/project.py         # reuse global-admin and view permission rules
└── locale/fa/LC_MESSAGES/          # backend localized failure messages
apps/web/src/
├── components/projects/
│   ├── ProjectLifecycleBar.tsx     # preserve dirty activation feedback
│   ├── ProjectArchiveRestoreDialog.tsx  # proposed focused dialog
│   ├── ProjectArchiveRestoreHistory.tsx # proposed focused read-only history
│   └── ProjectChangeRequestPanel.tsx    # existing remediation path
└── app/
    ├── routes/project-overview.tsx
    ├── routes/project-settings.tsx # manager control; protected fields stay protected
    ├── lib/api/projects.ts         # typed preview/restore/result/history
    └── locales/fa.json / en.json
 e2e/
├── playwright.restore.config.ts    # proposed intercepted frontend tests
├── playwright.restore.integration.config.ts # proposed real-service tests
└── tests/project-archive-restore*.spec.ts
```

**Structure Decision**: Use existing source boundaries. Proposed filenames identify later work; they have not been created. Keep existing structured-error `config/exceptions.py` and frontend `api-client.ts` changes; use them, adjusting only if focused contract tests expose a missing boundary. Preserve other CI/package edits.

## Phase 0 — Research outcome

[research.md](research.md) resolves authority exposure, archive-cycle identity, freshness, replay, lock coverage, atomic audit, visible history, executable remediation, old-data scope and evidence boundaries. Two read-only research agents inspected concurrency/audit and UI/contracts; the main agent consolidated decisions and official Django transaction documentation. No research agent modified the shared checkout.

## Phase 1 — Design outcome

- [data-model.md](data-model.md): Project metadata, immutable receipt, database constraints, signed context, writer ordering and explicit fresh-development-data migration boundary.
- [contracts/restore-api.md](contracts/restore-api.md): existing authorization/error conventions, exact retry and current-state separation, preview/results/history and narrow remediation availability.
- [contracts/restore-ui.md](contracts/restore-ui.md): independent server capability, confirmation/keyboard flow, all prerequisite guidance, uncertain outcome recovery and bilingual messages.
- [quickstart.md](quickstart.md): runnable future checks, planned test files, exact proof boundaries and all 25 acceptance scenarios mapped to evidence categories.

## Implementation sequencing and verification gates

Later tasks should follow a dependency sequence, preserving red → minimally implement → green evidence:

1. Write failing authorization/cycle/receipt/rollback contracts; add schema metadata/receipt and verify the new migration on isolated databases. Fixtures archive from known states; no inferred old origin.
2. Introduce Project-first lock/fresh-validation/targeted-save integration for existing writers, then implement archive metadata, preview, restore, durable replay and synchronous audit with middleware suppression. Prove races with independent PostgreSQL connections.
3. Add typed interfaces and narrow history. Make existing manager/CR remediation paths executable without relaxing protected-field approval or SoD, including server support capabilities/per-record CR actions so nonmember administrators are not blocked by membership-derived UI permissions. Prove non-admin archived behavior remains denied.
4. Add overview dialog/history and recovery states using existing components, preserving dirty activation feedback. Add fa/en frontend/backend messages and request-context capabilities.
5. Run focused pytest/regressions, migration/reversal, typecheck, intercepted bilingual UI and real API/browser data-preservation/retry checks. Record existing unrelated failures separately. Check that financial/approval functions are not invoked and existing data snapshots match.

No completed parent task is reset and no new task checkboxes are generated here. This planning gate may proceed to `/speckit-tasks`; implementation remains a separate user-invoked phase.
