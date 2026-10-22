# Implementation Plan: Site Inactivity Reasons, Conflict Guard, and Daily-Report Access Hardening

**Branch**: `031-site-inactivity-security` (Spec Kit logical branch; actual Git branch: `develop`) | **Date**: 2026-10-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/031-site-inactivity-security/spec.md`

**Feature Directory**: `specs/031-site-inactivity-security`
**Status**: Phase 0 research and Phase 1 design complete. This command updates design artifacts only; it does not implement source changes or regenerate `tasks.md`.

## Summary

Brownfield convergence on PROMPT-03: the daily-report site-closure cycle — five standard inactivity reasons, conditional mandatory validation with stable error code `inactivity_reason_required`, dynamic header selector, PDF parity, the inactive-day activity confirmation guard, and the by-date creation permission — is **already implemented end-to-end** (model, serializers, lifecycle views, aggregation, PDF, correction copy, sync comparison, by-date permissions with dedicated tests, locale catalogs, and the ActivityTab confirm dialog). Research identified a small residue: (1) the guard's warning copy deviates from the approved prompt text and the component requests a locale key (`dailyReports.inactiveActivityWarning`) that does not exist in the catalogs (`inactivitySiteActivityWarning` mismatch), so the hardcoded constant always wins; (2) the dialog title and buttons and the shared `INACTIVITY_REASONS` option labels are hardcoded Persian instead of sourced from both locale catalogs; (3) browser E2E evidence for the confirm/cancel modal is missing. The work is a minimal, coherent alignment pass plus verification — no schema, permission, or behavior changes.

## Technical Context

**Language/Version**: Python 3.12 / Django 4.2.11; TypeScript 5.9 / React 19 / React Router 7

**Primary Dependencies**: Django REST Framework (repository pin 3.17.1), PostgreSQL, ReportLab 4.2.5, TanStack Query, i18next, IndexedDB via `idb`, Playwright 1.63

**Storage**: PostgreSQL tables for daily reports and their child rows; browser IndexedDB for cached daily reports and pending offline mutations

**Testing**: pytest + pytest-django against PostgreSQL/Redis; Django model `full_clean`/`save` behavior; TypeScript typecheck; Playwright desktop/e2e flows; PDF text extraction

**Target Platform**: Bilingual Persian/English web application and Django API; desktop and responsive mobile browsers

**Project Type**: pnpm monorepo with Django API (`apps/api`) and React web client (`apps/web`)

**Performance Goals**: Inactivity validation is a local check during the edit interaction; the confirmation dialog is purely client-side; no additional API round trips are added

**Constraints**: Preserve Django 4.2; PostgreSQL + Redis for tests; keep existing `edit_reports`-guarded by-date POST and `view_reports`-guarded reads; keep stable reason values, field names, and error code `inactivity_reason_required`; keep the existing SiteStatus derivation/override and aggregation lifecycle unchanged; MinIO and RabbitMQ are not required for this feature

**Scale/Scope**: One vocabulary (five reasons), two editable header surfaces, one activities grid, one PDF header row adjustment already in place, one permission rule already in place

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

Pre-research: **PASS**. Post-design: **PASS**.

| Principle | Design gate and evidence obligation |
|-----------|-------------------------------------|
| **I — Authorization and isolation** | PASS — the permission hardening (by-date POST requires `edit_reports`; reads keep `view_reports`) already exists with a dedicated test module (`test_daily_summary_permissions`); no surface bypasses the authorized project scope. |
| **II — End-to-end consistency** | PASS — the reason vocabulary is traced across model enum, `clean`/`save`, serializers, lifecycle views, aggregation rebuild, corrections, sync conflict fields, PDF, UI, and tests; existing migration state is committed and immutable. |
| **III — Bilingual experience** | PASS with a closing gap — reason labels and warning copy are required in both catalogs; design aligns the shared option source and dialog text to the existing `dailyReports.inactivityReasons` / warning keys in `fa.json` and `en.json`; bilingual verification is a required evidence category. |
| **IV — Explicit, safe mutations** | PASS — the inactive-day guard is a non-destructive confirmation (cancel keeps the entry); invalid inactive saves are rejected server-side on all lifecycle paths even when the UI is bypassed. |
| **V — Minimal coherent change** | PASS — remaining work is copy/key alignment, label localization from existing catalog keys, and tests; no parallel subsystems, schema changes, or permission refactors. |
| **VI — Evidence-based verification** | PASS — quickstart separates backend pytest, typecheck, browser E2E, and PDF extraction evidence; current-tree re-runs are required. |
| **VII — Accessible operational UX** | PASS — the confirmation dialog must expose an accessible title/description, keyboard-operable confirm/cancel buttons, and focus restore to the editor after cancel. |

No constitution violation requires a complexity exception.

## Project Structure

### Documentation (this feature)

```text
specs/031-site-inactivity-security/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── daily-report-inactivity-api.md
│   └── daily-report-inactivity-ui.md
├── spec.md
└── checklists/requirements.md
```

`tasks.md` is generated later by `/speckit-tasks`.

### Source Code (repository root; planned touchpoints)

```text
apps/api/core/
├── field_reports/
│   ├── models.py                          # InactivityReason enum + clean/save — exists; verify only
│   ├── serializers.py                     # inactivity_reason_required validation — exists; verify only
│   ├── daily_report_views.py              # submit/review/approve path checks — exists; verify only
│   ├── pdf.py                             # inactive + reason header row — exists; verify only
│   ├── services/
│   │   ├── __init__.py                    # summary read fields — exists
│   │   ├── correction_service.py          # reason copy on versioning — exists
│   │   └── daily_report_aggregation.py    # rebuild clears/preserves reason — exists
│   ├── tests/
│   │   ├── test_spec_01_daily_header_weather.py   # inactivity validation tests — exists; extend for spec 031 SCs
│   │   └── test_daily_report_summary_permissions.py  # by-date permission tests — exists; verify only
│   └── ENDPOINTS.md                       # already documents the rules — verify wording
└── projects/seeds/full_project.py         # fixtures — verify legal reason values

apps/web/src/
├── components/daily_reports/
│   ├── ActivityTab.tsx                    # confirm dialog — align locale key + copy + title/buttons
│   ├── activity-guard.ts                  # guard predicate + constant copy — align approved text
│   ├── ReportHeader.tsx                   # dynamic reason select — localize labels
│   └── DailyReportForm.tsx                # hydration — verify reason state passes through
├── app/
│   ├── lib/api/daily-reports.ts           # INACTIVITY_REASONS shared source — labels from catalogs
│   ├── locales/fa.json, en.json           # warning copy + title keys
│   └── routes/daily-report-view.tsx       # summary metadata editor select — localize labels
└── app/lib/__tests__/                     # unit tests for guard predicate — add/extend

e2e/tests/
└── daily-report-inactivity-guard.spec.ts  # new: bilingual guard E2E (confirm/cancel/zero-qty)
```

**Structure Decision**: Brownfield convergence. The `InactivityReason` enum, validation chain, permission rule, PDF row, aggregation behavior, and dialog interaction already exist and carry tests; the plan extends no models, adds no migration, and changes no permission semantics — it aligns user-facing copy and label sources with the approved vocabulary and locale catalogs, then collects verification evidence.

## Phase 0 — Research Outcome

[research.md](./research.md) resolves the feature's current implementation state, the guard copy/key mismatch, the label-localization approach, offline/summary-preservation behavior, and verification strategy. No open clarification remains.

## Phase 1 — Design Outcome

- [data-model.md](./data-model.md) — entity fields, the five-reason vocabulary, conditional invariants, active-state clearing, summary reconciliations, and preservation rules
- [contracts/daily-report-inactivity-api.md](./contracts/daily-report-inactivity-api.md) — header payloads, stable validation error, by-date permission matrix, aggregation/PDF behavior
- [contracts/daily-report-inactivity-ui.md](./contracts/daily-report-inactivity-ui.md) — dynamic selector, warning dialog interaction, localization, accessibility, and E2E test id mapping
- [quickstart.md](./quickstart.md) — runnable backend, typecheck, browser, offline, and PDF verification for the residual scope

## Complexity Tracking

> None — no constitution violation requires justification.
