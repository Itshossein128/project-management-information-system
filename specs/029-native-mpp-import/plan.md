# Implementation Plan: Native Microsoft Project MPP Import

**Branch**: `develop` (actual Git branch; unchanged) | **Date**: 2026-10-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/029-native-mpp-import/spec.md`  
**Feature Directory**: `specs/029-native-mpp-import`  
**Spec Kit logical feature key**: `029-native-mpp-import` (setup JSON `BRANCH`; no Git branch created/switched)

**Status**: Phase 0 research and Phase 1 design complete. Design artifacts only; no `tasks.md`, source edits, or migrations in this invocation.

## Summary

Extend the existing MSP/P6 schedule import wizard so planners can upload native Microsoft Project **`.mpp`** files alongside MSP XML (`.xml`) and P6 XER (`.xer`). Server validates genuine MPP content, converts MPP → MSPDI XML via **MPXJ** (bounded time/resources), then reuses the current MSP preview/import pipeline (`parse_msp_xml` / `build_preview` / `execute_msp_import`, `MspImportJob`). UX copy, acceptance of `.mpp`, processing state, and localized error taxonomy (invalid type, corrupt, password-protected, unsupported/cannot-process, too large, timeout/conversion failure) complete the user-visible change without altering summary→WBS / leaf→activity mapping.

## Technical Context

**Language/Version**: Python 3.x / Django 4.2.11 (API); TypeScript + React Router 7 + Vite (`apps/web`)

**Primary Dependencies**: Django REST Framework, Celery (eager-capable), `python-magic`, `defusedxml` (existing MSP XML); **MPXJ** (`mpxj` + JPype) + **JRE** for MPP read/MSPDI write; TanStack Query on web

**Storage**: PostgreSQL — reuse `msp_import_jobs` (`MspImportJob`); additive `error_code` on import-job base; binary `file_data` unchanged; no new schedule domain tables

**Testing**: pytest for validators, converter error taxonomy, MPP→preview/import, XML/XER regression, permissions/IDOR, atomicity/timeout; fixture corpus under `schedule/tests/fixtures/mpp/`; `pnpm typecheck`; browser check of wizard accept/processing/errors in fa RTL + en LTR

**Target Platform**: Bilingual web SPA + Django API (Linux-hosted); JRE required on API/worker hosts

**Project Type**: pnpm monorepo (`apps/api` + `apps/web`)

**Performance Goals**: MPP conversion completes within configured wall-clock bound (default 60s) for ≤50 MB files; preview returns success or terminal failure (no indefinite hang); import progress continues via existing job polling

**Constraints**: 50 MB upload cap; untrusted uploads; no password bypass; server-enforced `edit_wbs` + project scope; no Django upgrade; preserve XML/XER behavior; do not change WBS-vs-activity mapping; bounded CPU/memory for conversion

**Scale/Scope**: One wizard; MSP endpoints accept XML+MPP; one compatibility corpus; no MPP edit/export/sync

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Pre-research and post-design: **PASS** (design gates only; not runtime proof).

| Principle | Gate |
|-----------|------|
| **I — Authorization / isolation** | PASS — Preview/start remain `edit_wbs`; job status project-scoped; no cross-project file/job access (contracts + data-model) |
| **II — Data / domain integrity** | PASS — Same `ParsedTask` / execute path after MSPDI conversion; summary→WBS / leaf→activity unchanged; atomic execute |
| **III — Bilingual** | PASS — Stable error codes; localized messages fa/en; wizard copy updated |
| **IV — Safe mutations** | PASS — Preview non-destructive; replace/append unchanged; password never bypassed; failed conversion/import leaves no partial structures |
| **V — Minimal coherent change** | PASS — Extend MSP import + wizard; no parallel job model or UI redesign |
| **VI — Evidence** | PASS — Plan requires pytest corpus + XML/XER regression + browser/locale checks |
| **VII — Accessible UX** | PASS — Processing state, distinct warnings vs fatals, keyboard + RTL/LTR called out in UI contract |

No unjustified violations → Complexity Tracking empty.

**Note**: JRE/MPXJ is an operational dependency, not a constitution violation; document in quickstart and deploy docs during implementation.

## Project Structure

### Documentation (this feature)

```text
specs/029-native-mpp-import/
├── plan.md              # This file
├── research.md          # Phase 0
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   ├── msp-mpp-import-api.md
│   └── msp-mpp-import-ui.md
├── spec.md
└── checklists/requirements.md
```

`tasks.md` is **not** created here — use `/speckit-tasks` next.

### Source Code (repository root; proposed touchpoints, not edits)

```text
apps/api/core/
├── common/
│   └── validators.py              # allow .mpp; content sniff; size 50MB
├── schedule/
│   ├── models.py                  # BaseImportJob.error_code (additive)
│   ├── views.py                   # MSP preview/start accept MPP; error codes
│   ├── tasks.py                   # convert-then-execute; map failures to codes
│   ├── services/
│   │   ├── msp_import.py          # optional thin dispatch helper
│   │   ├── mpp_convert.py         # NEW: MPXJ MPP→MSPDI; timeout; error mapping
│   │   └── shared_import.py       # unchanged mapping helpers
│   ├── ENDPOINTS.md               # document .mpp on MSP routes
│   └── tests/
│       ├── test_msp_import.py     # regression XML
│       ├── test_p6_import.py      # regression XER
│       ├── test_mpp_import.py     # NEW
│       ├── test_mpp_convert.py    # NEW
│       └── fixtures/mpp/          # NEW corpus
├── locale/fa/LC_MESSAGES/         # localized messages
└── config/settings.py             # MPP_CONVERT_TIMEOUT_SECONDS (or env)

apps/web/src/
├── components/wbs/msp-import-wizard.tsx   # accept .mpp; copy; processing UX
├── app/lib/api/msp.ts                     # treat .mpp as MSP family
├── app/routes/project-wbs.tsx             # button label if needed
└── locales/fa.json / en.json              # help + error strings
```

**Structure Decision**: Keep MSP import as the single Microsoft Project family (XML + MPP). Convert MPP to MSPDI then reuse existing parse/execute. P6 stays separate. Additive `error_code` on import jobs for auditability; no new domain tables for WBS/activities.

## Phase 0 — Research outcome

[research.md](./research.md) resolves: converter choice (MPXJ), MPP→MSPDI→existing parser, password reject, validation, API surface, error codes, timeouts, atomicity, frontend dispatch, corpus, permissions.

## Phase 1 — Design outcome

- [data-model.md](./data-model.md) — entities, validation, job states, error codes  
- [contracts/msp-mpp-import-api.md](./contracts/msp-mpp-import-api.md) — MSP endpoints + MPP behavior  
- [contracts/msp-mpp-import-ui.md](./contracts/msp-mpp-import-ui.md) — wizard UX contract  
- [quickstart.md](./quickstart.md) — validation scenarios  

## Complexity Tracking

> None — no constitution violations requiring justification.
