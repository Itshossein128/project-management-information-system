# Implementation Plan: Core Domain Principles & Glossary

**Branch**: `002-core-domain-principles` | **Date**: 2026-10-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-core-domain-principles/spec.md`

**Note**: TDD is mandatory. This plan and subsequent `tasks.md` define work only — **do not implement** until explicitly requested.

## Summary

Close the FR-CORE gaps identified against `01-دامنه، اصول و واژه‌نامه.md`: consistent glossary labels, universal audit/soft-delete hygiene on core project models still missing it, project currency + mixed-unit guards, unset-vs-zero conventions, richer actionable notifications, per-project capability toggles, and fiscal-period lock with duplicate-document warnings. Approach extends existing `common.AuditSoftDeleteModel`, permissions, audit middleware, Jalali helpers, and i18n catalogs — no new microservice. Delivery is test-first (pytest API contracts/services, then minimal code; frontend typecheck + targeted UI verification for labels/currency).

## Technical Context

**Language/Version**: Python 3.11+ (Django 4.2.11), TypeScript 5.x (React Router 7 + Vite)

**Primary Dependencies**: Django REST Framework, drf-spectacular, simplejwt, Redis cache (existing), React + TanStack Query, i18next (fa/en), existing `common.jalali`

**Storage**: PostgreSQL via `DATABASE_URL` (additive columns/tables for currency, capability flags, fiscal locks; soft-delete columns on models migrating onto `AuditSoftDeleteModel`)

**Testing**: pytest + pytest-django (TDD: write failing tests first); frontend `pnpm typecheck`; optional Playwright smoke only if a UI story requires it after API green

**Target Platform**: Web SPA (`apps/web`) + Django API (`apps/api/core`) under `/api/v1/projects/{uuid}/`

**Project Type**: Monorepo web application (frontend + backend)

**Performance Goals**: Negligible overhead on existing CRUD; capability/fiscal checks O(1) per request via project-scoped lookup/cache

**Constraints**: Django 4.2 pin; no SQLite; server-enforced tenancy/permissions; bilingual UX; minimal coherent change; no ERP/accounting integration; no implementation in this Spec Kit pass

**Scale/Scope**: Cross-cutting foundation touching `common`, `projects`, `notifications`, selected financial UI labels, and a small settings surface for capability toggles / fiscal lock — not a rewrite of modules 03–16

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Server-enforced authorization / project isolation | PASS | New endpoints stay under project tenancy + existing permission codes; admin capability toggles require elevated project/system permission |
| II. Data integrity end-to-end | PASS | Trace currency, soft-delete, capability flags through model → migration → serializer → API → UI → i18n → tests |
| III. Bilingual / locale-correct | PASS | Glossary work updates `fa.json`/`en.json`; Jalali day-boundary tests retained |
| IV. Explicit safe mutations | PASS | Soft-delete / corrective paths; fiscal lock blocks ordinary edits; duplicate warning before finalize |
| V. Minimal coherent changes | PASS | Extend `AuditSoftDeleteModel` and existing notification/project models; avoid parallel frameworks |
| VI. Evidence-based verification | PASS | TDD pytest mandatory per story; document verification evidence in implement phase |
| VII. Accessible practical UX | PASS | Clear unset vs zero messaging; currency labels beside amounts; capability disable does not delete history |

**Gate result (pre-research)**: PASS — no unjustified violations.

**Gate result (post-Phase 1 design)**: PASS — contracts remain project-scoped; data model is additive; TDD path documented in quickstart; Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/002-core-domain-principles/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── project-currency.md
│   ├── project-capabilities.md
│   ├── fiscal-period-lock.md
│   └── notifications-actionable.md
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
apps/api/core/
├── common/
│   ├── models.py                 # AuditSoftDeleteModel (reuse/extend helpers)
│   ├── money.py                  # NEW: currency units + mix guard helpers
│   ├── unset.py                  # NEW: null-vs-zero serialization helpers (optional)
│   └── tests/                    # NEW/extend unit tests for money/unset
├── projects/
│   ├── models.py                 # Project.currency; soft-delete migration targets (WBS/Project as decided)
│   ├── capability_models.py      # NEW or section: ProjectCapabilitySetting
│   ├── fiscal_models.py          # NEW or section: FiscalPeriodLock
│   ├── serializers.py / views.py # currency + capabilities + fiscal APIs
│   └── tests/                    # TDD modules per story
├── notifications/
│   ├── models.py                 # responsible_user, due_at fields
│   ├── serializers.py / views.py
│   └── tests/
├── permissions/                  # reuse HasProjectPermission; add codes if needed
└── audit/                        # reuse middleware; assert coverage in tests

apps/web/src/
├── app/locales/fa.json
├── app/locales/en.json
├── app/lib/money.ts              # NEW: display + mix guard helpers
├── app/routes/project-settings.tsx  # capability toggles + currency + fiscal lock UI hooks
├── components/notifications/     # show owner/deadline/link
└── components/**                 # glossary label fixes on WBS/cost/IPC surfaces
```

**Structure Decision**: Keep changes inside existing Django apps (`common`, `projects`, `notifications`) and shared web locales/settings. No new top-level package.

## Complexity Tracking

> Not applicable — Constitution Check passed without violations.
