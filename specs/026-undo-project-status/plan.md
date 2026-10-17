# Implementation Plan: Undo Project Suspension and Completion

**Branch**: `main` (actual Git branch; unchanged) | **Date**: 2026-10-17 | **Spec**: [spec.md](spec.md)

**Input**: `specs/026-undo-project-status/spec.md`
**Feature Directory**: `specs/026-undo-project-status`
**Spec Kit logical feature key**: `026-undo-project-status` (setup JSON reports this as BRANCH; no Git branch was created/switched).

**Status**: Phase 0 research and Phase 1 design complete. This invocation produces design artifacts only; no tasks, source, tests or migrations are created/executed. The spec's “only spec/checklist in this invocation” describes the earlier specify stage; the current plan request authorizes these additional documents. The existing spec, checklist, parent registration/archive documents and all earlier dirty work remain unchanged.

## Summary

Reuse the sole suspended→active resume action, preserving existing edit_project/global-admin authority while requiring reason, signed fixed-destination preview and durable retry. Add global-admin-only undo-completion to the actual active/suspended origin captured at completion. Source suspension/completion events are distinct protected references to synchronous semantic AuditLog rows; archive round trips retain them. One new narrow ProjectStatusUndo receipt commits with status and success audit under the existing Project row lock. No generic lifecycle engine or archive API/schema rewrite.

Two integration requirements prevent incomplete delivery: completed-origin-active needs a narrowly bound missing-scope/amount CR repair path because current completed projects cannot create CRs; UI must use server capabilities for nonmember/group-less administrators. Draft/pending identity includes operation as well as actor/project, and safe history distinguishes original event from undo and historical receipt from current status.

## Technical Context

**Language/Version**: Python 3.12.3 / Django 4.2.11 verified from the existing API venv. TypeScript ~5.9, React 19, React Router 7.12, Vite 7 from current manifests; frontend runtime/deployed versions were not probed in planning.

**Primary Dependencies**: Existing DRF, Django signing/gettext/transaction APIs, PostgreSQL/psycopg, TanStack Query, i18next, React Router and accessible dialog/buttons/manager lookup. No new dependency, external service, framework or Django upgrade.

**Storage**: Existing Project gains two protected AuditLog source references and completion origin; one new ProjectStatusUndo receipt; existing AuditLog reused for typed original/success events; existing CR gains an exclusive nullable completion-event binding. PostgreSQL is authoritative; Redis remains normal runtime infrastructure, not idempotency storage.

**Testing**: TDD with actual pytest/pytest-django/PostgreSQL, independent transaction/connection races and migration forward/reverse; frontend typecheck; intercepted Playwright UX separate from actual API/browser tests; both locales and desktop/mobile. Existing archive, lifecycle, protected-field, gate, activation-feedback, audit and SoD regressions must remain covered. Prior test totals are historical, not current-run proof.

**Target Platform**: Existing bilingual Linux-hosted API and browser application, Persian RTL/English LTR desktop/mobile. No native/mobile backend or new deployment platform.

**Project Type**: Existing pnpm web/API monorepo.

**Performance Goals**: Ready users complete choose/reason/confirm in three business steps (SC-UPS-002). Preview/result use indexed source/request lookups independent of history size. History default page 50/max 100 with stable ordering and bounded count/page queries, no per-row actor/source query. Locks enclose only short database work; no external I/O. No unsupported latency SLA or throughput requirement is introduced.

**Constraints**: Preserve resume authority and exact activation_missing predicate; undo-completion admin only; no inferred old origin, arbitrary expiry, free target, budget restamp, finance/approval/baseline replay or reasonless bypass. Preserve existing archive contracts/receipts/metadata and all prior source/document edits. General suspended CR rules and unbound CR policy remain unchanged; new completed creation is missing-fields-only and event-bound.

**Scale/Scope**: Two reverse operations, three valid source/destination pairs, 15 FR, 25 acceptance scenarios, seven SC; fa/en × two viewport classes. One receipt table and three Project metadata fields rather than another event ledger. No generic audit browser, bulk undo, multi-step undo history or new permission role.

## Constitution Check

Pre-research and post-design checks both PASS as design gates. These are not runtime/migration/security proof. No constitution change or unjustified violation remains.

- **I — Authorization/isolation: PASS before/after.** Fresh service/view project scope and authority; existing active-member edit_project/global bypass for resume; accepted global-admin-only undo-completion including nonmembers. The global bypass is existing server policy and explicit accepted scope, not an invented membership exception. Owned recovery does not expose another actor's attempt; shared history requires view_project. Client capability is UX only.
- **II — Data/domain integrity: PASS before/after.** Fresh Project lock, exact source/origin association, shared participating writers, atomic required original/success audits and receipt, targeted writes/version. Additive constraints and forward/reverse proof preserve valid prior business/archive records. The accepted old-development-data waiver permits explicit fresh isolated preparation, not guessed metadata or silent cleanup. Readiness and protected-field SoD remain intact.
- **III — Bilingual experience: PASS before/after.** Stable code identifiers, backend fa catalog, new fa/en UI messages, actual status/source/destination labels, and real browser validation across languages/viewports are specified.
- **IV — Explicit safe mutations: PASS before/after.** Reason + project/target/effect before confirm; cancel-before-send scope, unknown result recovery, request/event isolation and no clock cutoff explicit. No production-like data action or DB reset during planning. Required audit rollback is part of the same business outcome.
- **V — Minimal coherent change: PASS before/after.** Existing resume route, lifecycle locks, audit storage, protected CR, controls and auth cleanup are extended. One receipt is necessary for durable exact replay; source FKs reuse typed audit rows rather than add a generic/event table. Archive model/API remain separate and compatible.
- **VI — Evidence: PASS before/after.** Meaningful RED→minimal fix→GREEN for missing behavior; existing correct behavior remains GREEN. Separate API, true PostgreSQL contention, migration, typecheck, mocked UI, real browser and external-storage/CI boundaries. No checked task or historical pass substitutes for current final-tree verification.
- **VII — Accessible practical UX: PASS before/after.** Existing accessible dialog, one resume action, visible reason validation, all missing fields + usable authorized repair paths, locale-aware provenance, keyboard/viewport checks and retained actor/project/operation-safe drafts.

## Project Structure

### Documentation (this feature)

```text
specs/026-undo-project-status/
├── spec.md                         # preserved accepted feature specification
├── checklists/requirements.md      # preserved 16/16 spec-quality review
├── plan.md                         # this plan
├── research.md                     # Phase 0 decisions and source evidence
├── data-model.md                   # Phase 1 fields/invariants/transactions
├── contracts/
│   ├── status-undo-api.md           # preview/resume/undo/result/history/repair
│   └── status-undo-ui.md            # capabilities/dialog/recovery/drafts/locales
└── quickstart.md                   # future isolated validation commands
```

`tasks.md` is intentionally not created; `/speckit-tasks` is the next phase. Do not reopen/reset parent `008` tasks or archive T001–T085 to represent this feature.

### Source Code (repository root; proposed touchpoints, not edits)

```text
apps/api/core/
├── projects/
│   ├── models.py                      # source FKs, undo receipt, CR binding
│   ├── lifecycle_service.py           # real suspend/complete origin capture,
│   │                                  # required confirmed resume delegation
│   ├── status_undo_service.py          # proposed focused preview/undo/replay
│   ├── change_request_service.py       # narrow completed-bound repair
│   ├── serializers.py                 # read-only guards/capabilities/contracts
│   ├── views.py / urls.py              # scoped explicit routes, existing resume
│   ├── migrations/                    # new additive migration(s) after 0016
│   └── tests/test_project_status_undo*.py
├── audit/middleware.py                # narrow additional semantic-action marker
└── locale/fa/LC_MESSAGES/              # translated backend errors
apps/web/src/
├── components/projects/
│   ├── ProjectLifecycleBar.tsx         # replace immediate resume, preserve others
│   ├── ProjectStatusUndoDialog.tsx     # proposed operation-scoped section/dialog
│   ├── ProjectStatusUndoHistory.tsx    # proposed safe original/undo projection
│   ├── ProjectArchiveRestoreManager.tsx # reuse manager-only control
│   └── ProjectChangeRequestPanel.tsx   # actual completed/archived per-record actions
└── app/
    ├── lib/api/projects.ts             # distinct undo types, required resume body
    ├── lib/project-status-undo-state.ts # proposed separate drafts/frozen attempts
    ├── contexts/auth-context.tsx       # extend existing cleanup namespaces
    ├── routes/project-overview.tsx     # independent server-capability mounting
    ├── routes/project-settings.tsx     # actionable field/CR repair controls
    └── locales/fa.json / en.json
 e2e/
├── helpers/project-status-undo.ts      # proposed real fixture/client helpers
├── helpers/seed-project-status-undo.py # proposed isolated actors, private output
├── playwright.status-undo.config.ts    # proposed intercepted UX category
├── playwright.status-undo.integration.config.ts # proposed actual API category
└── tests/project-status-undo*.spec.ts
```

**Structure Decision**: Keep source-event capture at the existing forward lifecycle boundary; a focused new service can import existing root-lock/version/readiness primitives, while the existing resume entry point delegates with mandatory confirmation arguments (no reasonless internal fallback). Reuse `audit.service.persist_audit_log` as it stands; it returns the created audit UUID. Do not add a second auth lifecycle or general command bus. Existing archive receipt/history/types and `_project_restore_audited` behavior remain intact; shared helper extraction is limited to what this feature actually needs and requires archive regressions.

Creation/template/import paths and directly constructed fixtures are integration touchpoints for guarding/setting valid new metadata, not authorization to change other domain behavior. Existing structured-error/API-client/activation/CI/package changes are preserved.

## Phase 0 — Research outcome

[research.md](research.md) resolves fourteen decisions: authority asymmetry, sole resume contract upgrade, exact typed original audit references, archive/suspension round trips, immutable receipts, root-lock/replay ordering, context freshness, exact readiness/no side effects, completed remediation/SoD, capability/history UI, scoped state/refresh, atomic audit/errors, migrations/development data, and evidence design.

Two read-only research agents inspected backend and UI integration. The chosen smaller source-event design uses protected audit references (not an extra source-event table); the one new receipt model carries durable reverse success. Official Django 4.2 transaction/queryset/signing references are linked beside the relevant research decisions. No unresolved technical/product question remains.

## Phase 1 — Design outcome

- [data-model.md](data-model.md): exact fields, null/effective-state/uniqueness constraints, safe provenance, preserved references across archive/undo, current-state validation, immutable receipt, CR binding, token context, transactions and schema reversal.
- [API contract](contracts/status-undo-api.md): existing resume's intentional confirmed-body/result upgrade, dedicated completion undo, no-store previews/results/history, exact replay before state checks, owned lookup, safe shared history, capability and repair shapes, errors.
- [UI contract](contracts/status-undo-ui.md): one existing resume control, independent admin capability, truthful original/current states, read failures versus sent-unknown outcomes, operation-scoped frozen requests/drafts, actual repair and cache keys, fa/en/keyboard behavior.
- [quickstart.md](quickstart.md): future commands using a new isolated database through the existing runner, proposed test modules/configs, TDD and all 25 acceptance scenarios mapped to evidence categories.

Post-design constitution gate was re-evaluated against these exact contracts/invariants: PASS. Spec and its checklist are unchanged. No tests/migration/source edits or implementation delivery are claimed.

## Implementation sequencing and validation gates

Future `/speckit-tasks` should order the work without changing the accepted scope:

1. Capture current tree/runtime/baselines and isolated fixture boundary. Write missing-behavior RED for original source capture, strict metadata/receipt constraints and reverse schema behavior; add new migrations and prove forward/reverse with old valid business/archive records.
2. Capture exact original suspend/complete events atomically; preserve references through archive/restore and completion undo. Implement fresh authority, confirmed sole resume/new undo-completion and immutable receipt/replay. Prove Project-first contention, all destinations, known rollback versus lost acknowledgment and zero side effects.
3. Add completed-active-only bound remediation and server capabilities/per-record CR actions; prove normal suspended/unbound policy, open-CR handling, stale binding/current-field/role rechecks, other-approver SoD and permitted cancel. Add safe no-store original/undo history and owned result lookup.
4. Update typed resume caller and one UI control; add focused dialog/history, actor/project/operation ownership, frozen sent body, separate drafts and existing auth cleanup, fresh preview/read failures, real cache invalidation and bilingual text. Observe UX RED before fixes where behavior is actually missing.
5. Run meaningful final backend/archive regressions, PostgreSQL contention/migrations, typecheck, full intercepted UI and actual fa/en desktop/mobile browser journeys on final tree. Record exact exits, baseline failures, artifacts and external-storage/CI/deployment limits; mark future tasks complete only after their actual deliverables/gates.

This command ends after Phase 1. It generates neither task markers nor code, performs no database reset, and creates no commit/branch/deployment.
