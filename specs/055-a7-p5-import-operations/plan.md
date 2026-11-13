# Implementation Plan: Reliable Schedule Import Operations

**Branch**: `develop` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Feature directory**: `specs/055-a7-p5-import-operations`
**Input**: Validated A.7-P5 specification; user-approved seven-day original-file retention.
**Planning status**: Phase 0 research and Phase 1 design complete. Independent design is authorized by the current `/speckit-plan` invocation. This does not waive the predecessor gate for implementation. No runtime acceptance claimed.

## Summary

Extend existing MSP/MPP and P6 import jobs instead of adding a second job platform. Prepare untrusted input within a killable, resource-contained helper shared by preview, start validation, and background import. Claim jobs with bounded ownership; serialize application with project→job locks; commit domain changes and DONE/result together. Reconcile abandoned pending/running jobs and clean expired originals and derived artifacts using existing Celery Beat and idempotent management commands. Explicit retry intent requires a failed-predecessor link, matching in-flight starts bypass capacity admission, and finite oldest-first maintenance cohorts use backlog-dependent completion bounds. Preserve P2 safety, P3 fidelity, P4 UI contracts, and the selected seven-day diagnostic retention.

## Technical Context

**Language/Version**: Python 3.12 runtime; Django remains pinned to 4.2.11. Existing frontend TypeScript/React Router 7; no preview redesign.

**Primary Dependencies**: Existing Celery/Redis, PostgreSQL, MPXJ/JPype/JRE, defusedxml. Read-only local package inventory: Python 3.12.3, Celery 5.6.3, MPXJ 16.10.0, JPype 1.7.1, Redis Python client 8.0.1, OpenJDK 21.0.12.1. Delivery-image versions must be captured independently; floating lower bounds are not a lockfile.

**Storage**: Existing `msp_import_jobs`/`p6_import_jobs` BinaryField originals; PostgreSQL business records; restrictive per-execution temporary workspace on a bounded filesystem; delegated cgroup-v2 subtree for helper containment. Existing result backend is not the business source of truth.

**Testing**: pytest/pytest-django on isolated PostgreSQL; real non-eager Redis broker/Celery worker/maintenance process; actual native MPP conversion and failure injection; bilingual browser verification for changed error feedback; migration/data-preservation checks. Source inspection is current evidence; operational tests remain future work.

**Target Platform**: Linux delivery environment with JRE, cgroup v2 memory/pids/CPU controllers delegated to the import launcher, and bounded scratch storage. Unsupported containment fails closed. No change to other running services is authorized by this plan.

**Project Type**: Existing pnpm web/API monorepo; narrowly scoped backend/import/deployment extension.

**Performance Goals**: Every admitted attempt terminates within effective processing/recovery limits; duplicate messages produce at most one committed application; a healthy import succeeds after each failure. Recovery/expiry bounds and successful-pass assumptions use N-sized cohorts, B=100, C=10 seconds per item and G≤1 second inter-batch delay as defined in the runtime contract; intervals alone are not completion bounds. Numeric settings below are an initial engineering acceptance profile, not customer throughput/SLA commitments.

**Constraints**: Preserve the existing 50 MiB upload limit and configurable 60-second conversion default. All routes share one conversion deadline. Seven days is 168 elapsed hours from immutable terminal time. No broad dependency upgrade, new broker family, production deployment, independent WBS spreadsheet importer, or relaxed A6 access.

**Scale/Scope**: One conversion/preparation slot across the isolated acceptance deployment; existing production Celery concurrency two is not asserted as tested conversion capacity. Four audit owners: I09/I19/I20/D02.

## Constitution Check

*Pre-research gate: PASS for independent design. Post-design review: PASS with the same constraints. No Constitution exception is requested.*

- I — Authorization/isolation: preserve actor/project checks at start and apply; no new raw-file download; diagnostic retention gives no new permission; status remains project-scoped.
- II — Integrity: project→job lock order and atomic domain/result commit; additive job migrations preserve existing bytes/history; forward/backfill/rollback validation required. Existing P3 fields and P4 counts remain regression targets.
- III — Bilingual: stable existing codes plus explicitly translated operational failures; browser acceptance in Persian/English if presentation changes.
- IV — Safe mutations: only phase-specific disposable environment may receive fault injection/cleanup tests. No production action or deletion of shared uploads.
- V — Minimal changes: retain concrete job tables, API routes, Celery and conversion libraries. A small helper/maintenance command is internal infrastructure, not a parallel application/service family.
- VI — Evidence: separate source inventory, pytest, migration, browser, actual worker, containment and delivery-image evidence; no eager substitutes.
- VII — Practical UX: preserve synchronous preview and existing wizard/recovery; existing accessibility checks cover changed errors.

**Predecessor implementation gate — VERIFIED (2026-11-12)**: The separately user-authorized [P4 handoff](../054-a7-p4-import-experience/handoff.md) now exists. P1/P2/P3 downstream-readiness supplements confirm the same integrated HEAD, supported by 93 passing tests with no skips/failures/errors and fresh typecheck; browser evidence is explicitly historical and retains its limits. P5 T001 is verified against these sources. This clears the local predecessor gate only; operational containment/services/worker/recovery/retention acceptance remains unverified. Recheck actual code/handoff drift before continuing implementation.

**Operational acceptance gate — OPEN, specified prerequisites**: delegated containment, bounded scratch, actual broker/worker/maintenance configuration and delivery-image behavior must be demonstrated in the isolated environment. Executable presence does not establish service availability. These are known deployment requirements, not unresolved product choices.

## Phase 0 — Research decisions

See [research.md](research.md): source findings, two read-only research-agent investigations, official references, choices/alternatives. Technical choices are resolved; environment provisioning and empirical calibration are explicit acceptance gates rather than assumed successful tests.

## Phase 1 — Design

- [data-model.md](data-model.md): additive lifecycle fields, conservative legacy anchoring, lock/fencing rules, migration checks.
- [contracts/import-operations.md](contracts/import-operations.md): existing endpoint compatibility, dispatch/claim/application, retry and cleanup semantics.
- [contracts/runtime-containment.md](contracts/runtime-containment.md): launcher, deadlines, resource profile, recovery and deployment requirements.
- [quickstart.md](quickstart.md): isolated validation procedure and evidence matrix; proposed commands clearly marked as implementation outputs.

### Implementation sequence for later task generation

1. Confirm integrated predecessor handoffs and snapshot code/environment identity.
2. Add lifecycle/digest/backfill migration and preservation checks before using new fields.
3. Build the contained helper/launcher and shared bounded preparation adapter; preserve existing parser/fidelity semantics and wire all three entry paths.
4. Introduce fenced claims, atomic final outcome, durable dispatch recovery, and monotonic visible stage progress; then enable per-import late acknowledgment.
5. Implement seven-day expiry and abandoned-workspace reconciliation through existing Beat plus explicit commands; add operational translations.
6. Add isolated acceptance configuration and fault-injection harness; run migrations, regressions, actual file conversion/import, resource/restart/duplicate/cleanup matrix and bilingual UI checks. Only evidence can close operational gates.

## Project Structure

### Documentation (this feature)

```text
specs/055-a7-p5-import-operations/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── import-operations.md
│   └── runtime-containment.md
├── traceability.md
├── handoff.md
├── checklists/requirements.md
└── evidence/verification.md
```

### Source Code (repository root; new paths explicitly proposed)

```text
apps/api/core/
├── config/settings.py                 # new bounded import settings/Beat entries
├── schedule/models.py                 # BaseImportJob lifecycle extensions
├── schedule/views.py                  # existing preview/start/status routes
├── schedule/tasks.py                  # fenced execution and terminal outcome
├── schedule/services/
│   ├── mpp_convert.py                 # replace in-process JVM route with launcher
│   ├── msp_import.py                  # reuse parser + shared prepared-input apply
│   ├── p6_import.py                   # same adapter boundary
│   ├── import_safety.py               # preserve P2 gate and project serialization
│   ├── import_operations.py           # proposed lifecycle/dispatch/cleanup helpers
│   └── import_process.py              # proposed standalone helper/launcher protocol
├── schedule/management/commands/
│   ├── maintain_import_jobs.py        # proposed idempotent reconciliation + purge
│   └── verify_import_runtime.py       # proposed isolated acceptance harness
├── schedule/migrations/                # next available number; inspect at implementation
├── schedule/tests/                     # focused runtime and migration regressions
└── locale/fa/LC_MESSAGES/               # operational errors if server text changes
apps/web/src/app/locales/{en,fa}.json     # matching new failure codes only
ops/a7-p5/compose.yml                    # proposed isolated acceptance config
```

**Structure Decision**: Extend the established schedule domain; do not add another queue/job framework. Preserve event `worker` separately from `celery-worker`; `run_event_worker` is not Celery. Tasks are generated by `/speckit-tasks`, not this command.

## Complexity Tracking

No Constitution violations or exemptions. Linux helper containment and two-table lifecycle extensions are required by bounded untrusted processing and crash-safe application. A thread timeout, result-backend status, and whole-job deletion were rejected because they do not meet those requirements.

## Authorized analysis remediation — 2026-11-12

The user authorized direct document edits after the read-only analysis. I1 is addressed by request intent=new/retry, mandatory failed-predecessor linkage for the explicit Retry action, API-client/wizard propagation and status-refresh distinction (T035/T040/T043). I2 is addressed by scoped in-flight matching before capacity plus post-preparation locked recheck (T017/T019/T020/T022). U1 is addressed by the finite-cohort maintenance protocol/formulas and 201-item fairness/budget tests (T012/T025/T027/T028/T035/T039/T042/T047). I3 is addressed by separate pre-admission rejection and admitted-job failure semantics/evidence (T017/T018/T024). These are design corrections, not product implementation or runtime proof. The predecessor gate remains open.
