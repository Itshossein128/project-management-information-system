# Data Model: Native Microsoft Project MPP Import

**Feature**: `029-native-mpp-import`  
**Date**: 2026-10-20

This feature primarily **reuses** existing schedule-import and project schedule entities. The only intended schema addition is an optional audit field on import jobs for stable error codes.

## Entities (existing — unchanged semantics)

### Project (`projects.Project`)

Tenant scope for all uploads, previews, jobs, WBS, and activities.

### WBS (`projects.WBS` / treebeard)

Created from Microsoft Project **summary** tasks (same as MSP XML today).

### Activity (`projects.Activity`)

Created from **non-summary** tasks and milestones under the appropriate WBS parent.

### ActivityRelation (`projects.ActivityRelation`)

Predecessor links with type + lag as mapped by the existing MSP importer.

### BaselineSchedule / BaselineActivity

Created on successful MSP-family import (XML or MPP) under current product rules (imported snapshots remain subject to lock/approve policies from schedule/baseline specs).

### MspImportJob (`schedule.MspImportJob`)

Project-scoped job for MSP-family imports (`.xml` and `.mpp`).

| Field (existing) | Role |
|------------------|------|
| `id` (UUID) | Job id returned as `task_id` to clients |
| `project` | Isolation scope |
| `created_by` | Actor for audit |
| `filename` | Original upload name (preserve `.mpp`) |
| `replace_existing` | Append vs replace mode |
| `file_data` | Stored upload bytes until job completes (existing pattern) |
| `status` | `pending` → `running` → `done` \| `failed` |
| `progress_pct` | 0–100 |
| `result` | JSON: `wbs_nodes_created`, `activities_created`, `relations_created`, `warnings` |
| `error_message` | Localized or operator-visible failure text |
| `task_id` | Celery id (existing) |

### P6ImportJob

Unchanged; `.xer` only.

## Additive field

### `BaseImportJob.error_code` (new, nullable/blank)

| Attribute | Rule |
|-----------|------|
| Type | Short string (e.g. `CharField(max_length=64)`, blank default) |
| Purpose | Stable, language-independent failure code for audit and clients |
| Values | See Error codes below; empty when `status=done` or not failed |
| Applies to | `MspImportJob` and `P6ImportJob` via abstract base (P6 may leave unused) |

Migration: additive, nullable/blank — no data backfill required.

## Transient / non-persisted structures

### Uploaded Schedule File

Validated multipart upload: size ≤ 50 MB; extension in `{.xml,.mpp}` for MSP routes (`.xer` for P6); content sniffed (XML vs OLE/MPP).

### Schedule Preview DTO

Existing `build_preview` shape: `wbs_tree`, `activities`, `warnings`. Not persisted. For MPP, produced only after successful conversion + parse.

### ParsedTask / ParseResult

Existing dataclasses from `msp_import`. MPP path must end in the same structures (via MSPDI parse).

### Compatibility Fixture

Test-only files under `schedule/tests/fixtures/mpp/`; not a runtime DB entity.

## Validation rules

1. **Size**: reject > 50 MB → `file_too_large`.
2. **Type**: MSP route accepts `.xml` and `.mpp` only; content must match (XML root / OLE-MPP), else `invalid_file_type` or `mpp_corrupt`.
3. **Password**: protected MPP → `mpp_password_protected`; never decrypt/bypass.
4. **Unsupported**: genuine MPP that converter cannot process → `mpp_unsupported`.
5. **Corrupt**: truncated/unreadable → `mpp_corrupt` (or existing XML invalid path for bad XML).
6. **Timeout / conversion**: → `processing_timeout` / `conversion_failed`.
7. **Auth**: missing membership or `edit_wbs` → HTTP 403 (no job created for denied preview/start).
8. **Replace / append**: unchanged domain rules from `execute_msp_import`.

## State transitions (`MspImportJob`)

```text
[upload validated + parse/convert OK]
    → PENDING (job created, file_data stored)
    → RUNNING (worker started)
    → DONE (result filled, progress 100)
       or FAILED (error_code + error_message; no partial domain commit)
```

Preview does **not** create a job. Failed conversion on **start** before job create may return 400 without a job; if job already created and worker fails conversion/execute → `FAILED`.

Failed or timed-out jobs must not block creating a new job for the same project.

## Error codes (canonical)

| Code | Meaning |
|------|---------|
| `invalid_file_type` | Not an allowed schedule file |
| `file_too_large` | Exceeds upload policy |
| `mpp_corrupt` | Corrupt/truncated/unreadable MPP |
| `mpp_password_protected` | Password-protected MPP |
| `mpp_unsupported` | Recognized MPP, cannot process |
| `msp_invalid_xml` | Invalid/suspicious MSP XML |
| `processing_timeout` | Conversion/processing exceeded bound |
| `conversion_failed` | Internal converter/JRE failure |
| `import_failed` | Execute-time domain failure after successful parse (rare; message required) |

## Relationships (logical)

```text
Project 1──* MspImportJob
Project 1──* WBS 1──* Activity
Activity *──* Activity (via ActivityRelation)
MspImportJob --(on DONE)--> creates WBS / Activity / Relations / Baseline (via execute)
```

## Retention / cleanup

Follow existing import-job `file_data` retention. Ephemeral conversion buffers/temp files must be deleted after request/task completion; never shared across projects.
