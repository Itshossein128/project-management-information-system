# Research: Native Microsoft Project MPP Import

**Feature**: `029-native-mpp-import`  
**Date**: 2026-10-20

## Decision 1 — Processing strategy: MPP → MSPDI XML → existing MSP parser

**Decision**: Read genuine `.mpp` bytes with a bounded converter, produce in-memory Microsoft Project XML (MSPDI), then feed that XML into the existing `parse_msp_xml` → `build_preview` / `execute_msp_import` pipeline. Do not invent a second WBS/activity mapping model.

**Rationale**: Spec FR-004–FR-006 and SC-003 require MPP and MSP XML equivalence for supported fields and the same summary→WBS / leaf→activity presentation. Reusing the proven XML importer maximizes parity and satisfies constitution V (minimal coherent change).

**Alternatives considered**:
- Map MPXJ/`ProjectFile` tasks directly to `ParsedTask` — viable, but duplicates mapping logic and risks subtle drift from XML path.
- Replace XML importer entirely with a universal binary reader — out of scope; breaks FR-002 backward compatibility risk surface.
- Require users to export XML — status quo; rejects primary user value.

## Decision 2 — Converter library: MPXJ (Python package + JVM)

**Decision**: Use the open-source **MPXJ** stack to read MPP and write MSPDI XML. Prefer PyPI `mpxj` via JPype when installed; otherwise fall back to a **Java CLI** classpath (`MPP_MPXJ_CLASSPATH` / `net.sf.mpxj.sample.MpxjConvert`). Runtime requires a compatible **JRE**. Prefer lazy JVM start once per process when using JPype; never start/stop JVM per request.

**Rationale**: MPXJ reads MPP8/9/12/14 generations (Project 98 through modern Microsoft 365 binaries)—aligned with FR-022 best-effort policy. Password-protected files raise a distinct “File is password protected” exception usable for FR-013. LGPL-compatible for server-side use; widely used for schedule interchange.

**Alternatives considered**:
- **Aspose.Tasks** — strong native support; commercial license cost and heavier ops; rejected for default Velora open-stack path.
- **Pure-Python OLE/MPP parsers** (e.g. experimental `msp-export` / custom olefile) — no JVM, but narrower version coverage; conflicts with FR-022 best-effort.
- **Shell out to a separate conversion microservice** — clearer isolation, but new deployable and network surface; deferred unless JVM-in-process proves untenable in ops.

**Ops note**: Document JRE install for local/cloud/Docker images. Preview/import fail with localized “internal conversion failure” if JRE/MPXJ unavailable (distinct from corrupt file).

## Decision 3 — Password policy: reject, never bypass

**Decision**: On password-protected MPP, return the specific `mpp_password_protected` error. Do **not** call MPXJ options that ignore password protection (e.g. `setRespectPasswordProtection(false)`), even for MPP9 where bypass is technically possible.

**Rationale**: Spec out-of-scope and FR-010 explicitly forbid recovering/bypassing passwords. Constitution IV safe mutations / untrusted input.

**Alternatives considered**:
- Silently decrypt MPP9 without password — security and policy violation.
- Prompt for password in UI — out of scope for v1.

## Decision 4 — Content validation before conversion

**Decision**: Extend schedule upload validation to allow `.mpp` in addition to `.xml` for the MSP import endpoints. Enforce 50 MB size. Detect content with `python-magic` (and/or OLE compound-document signature `D0 CF 11 E0…`) rather than trusting client MIME/extension alone. Extension `.mpp` with non-OLE/non-MPP content → `invalid_file_type` or `mpp_corrupt` as appropriate. True OLE that is not a readable Project file → `mpp_corrupt` / `mpp_unsupported` after converter fails to recognize Project structure.

**Rationale**: FR-008, FR-009, FR-013; existing `validate_upload` / `python-magic` pattern in `common.validators`.

**Alternatives considered**:
- Extension-only client checks — rejected by FR-009.
- Separate `/import/mpp/` endpoint tree — unnecessary duplication; keep `/import/msp/` as the MSP family (XML + MPP).

## Decision 5 — API surface: extend MSP import, not a third family

**Decision**: Keep existing routes under `/api/v1/projects/{id}/import/msp/` for both `.xml` and `.mpp`. P6 remains `/import/p6/` for `.xer`. Server dispatches on validated content/extension: XML → current path; MPP → convert then current path. Reuse `MspImportJob` for both.

**Rationale**: Spec says same wizard and same MSP workflow; constitution V. Frontend already branches XER vs MSP by extension; extend MSP branch to include `.mpp`.

**Alternatives considered**:
- New `/import/mpp/` + `MppImportJob` — parallel jobs/UI; rejected.
- Force all formats through one `/import/schedule/` — larger rename; defer.

## Decision 6 — Error taxonomy (stable codes + localized messages)

**Decision**: Introduce stable machine-readable **error codes** (language-independent) with localized `message` strings:

| Code | When |
|------|------|
| `invalid_file_type` | Extension/MIME/content not an allowed schedule type |
| `file_too_large` | Exceeds 50 MB policy |
| `mpp_corrupt` | Truncated/corrupt/unreadable as MPP |
| `mpp_password_protected` | Password-protected MPP |
| `mpp_unsupported` | Recognized as MPP but converter cannot process (FR-022) |
| `msp_invalid_xml` | Existing invalid/suspicious XML (preserve behavior) |
| `processing_timeout` | Wall-clock bound exceeded |
| `conversion_failed` | JRE/MPXJ/internal conversion failure not classified above |
| `permission_denied` | Missing membership / `edit_wbs` (HTTP 403) |

Preview responses use the existing error envelope with `code` populated. Failed jobs store `error_code` (additive field on import job) plus localized `error_message`.

**Rationale**: FR-012, FR-013; constitution III (stable identifiers, localized presentation).

## Decision 7 — Time/resource bounds

**Decision**:
- Hard wall-clock timeout for MPP conversion (recommended default **60s**, configurable via settings env).
- On timeout: terminate conversion work cleanly, return `processing_timeout`, no project mutation; do not leave JVM/thread in a state that blocks later imports.
- Memory: rely on 50 MB upload cap; avoid writing unbounded temp files—prefer in-memory byte buffers; if temp files required, project-scoped ephemeral paths with existing cleanup expectations.
- Preview remains **synchronous** HTTP (like XML today); UI shows processing state while awaiting response. Import remains Celery/`CELERY_TASK_ALWAYS_EAGER` async job with progress.

**Rationale**: FR-011, FR-015, FR-020, SC-006. Async preview would redesign the wizard job model; out of minimal scope.

**Alternatives considered**:
- Async preview jobs — better for huge files but new UX/API; defer.
- No timeout — violates FR-020 / SC-006.

## Decision 8 — Atomicity

**Decision**: Keep `execute_msp_import` `@transaction.atomic`. Conversion happens **before** any WBS/activity writes (preview always; import job converts then executes). If conversion fails, job → `failed` with code; project rows unchanged. Mid-execute failure rolls back transactional mutations; baseline/relations created only inside the same transaction as today.

**Rationale**: FR-010, FR-011, SC-004.

## Decision 9 — Frontend routing and UX

**Decision**: Update `msp-import-wizard.tsx` and `msp.ts`:
- Accept `.mpp` in picker, drag-drop, and client pre-check.
- Route `.xer` → P6; `.xml` and `.mpp` → MSP endpoints.
- Replace “binary .mpp not supported” help with accepted-formats copy (MPP + XML + XER).
- While `previewMutation.isPending`, show explicit preparing/processing state and disable duplicate submit.
- Surface server error codes into localized toasts/inline fatal errors with recovery actions (choose another file / export XML / retry).
- Keep filename visible; preserve RTL/LTR and keyboard access.

**Rationale**: Spec UX requirements + FR-015–FR-017.

## Decision 10 — Compatibility corpus

**Decision**: Add fixtures under `apps/api/core/schedule/tests/fixtures/mpp/` (and paired XML where applicable): hierarchy, milestones, dependencies, dates/durations/progress, critical/slack when present, plus rejection set (corrupt, wrong content + `.mpp` name, password-protected, oversized stub, unreadable genuine MPP). Prefer generating paired XML via MPXJ from the same MPP for SC-003, checked into fixtures once stable.

**Rationale**: FR-021, SC-002, SC-003, SC-004.

## Decision 11 — Permissions unchanged

**Decision**: Preview/start remain `edit_wbs`; status poll remains project-scoped job lookup (`project_id` + job pk) with existing `view_wbs` / membership checks as today. No cross-project file or job access.

**Rationale**: FR-018; constitution I.

## Resolved Technical Context unknowns

| Unknown | Resolution |
|---------|------------|
| How to read MPP | MPXJ → MSPDI → existing parser |
| Version policy | Best-effort via MPXJ; `mpp_unsupported` when recognized but unreadable |
| Password | Reject; never bypass |
| New API family? | No — extend MSP import |
| Preview sync vs async | Sync + timeout + UI pending state |
| Size limit | 50 MB unchanged |
| JRE dependency | Required for API/worker; document in quickstart |
