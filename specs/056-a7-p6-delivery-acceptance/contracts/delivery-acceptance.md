# Contract: Integrated Acceptance and Employer Delivery Package (A.7-P6)

**Feature Directory**: `specs/056-a7-p6-delivery-acceptance`  
**Direct Audit IDs**: `D03`, `D04`  
**Predecessor Contracts**:
- `specs/051-a7-p1-project-reference/contracts/schedule-reference.md`
- `specs/052-a7-p2-import-safety/contracts/import-safety.md`
- `specs/053-a7-p3-import-fidelity/contracts/import-fidelity.md`
- `specs/054-a7-p4-import-experience/contracts/import-experience.md`
- `specs/055-a7-p5-import-operations/contracts/import-operations.md` & `runtime-containment.md`

---

## 1. Scope & Non-Mutation Contract

1. **No New Product Endpoints or Tables**: `A.7-P6` adds no new Django database tables and no new product HTTP endpoints. All acceptance tests exercise the existing product endpoints (`/api/v1/projects/...`, `/api/v1/wbs/...`, `/api/v1/project-templates/...`, `/api/v1/schedule/...`) and UI screens (`/projects`, `/wbs`, schedule import wizard, project charter, change requests, and lifecycle actions).
2. **Immutable Historical Snapshot**: `output/a7-requirements-2026-11-10/requirements.json` and `output/a7-requirements-2026-11-10/report.md` MUST NOT be modified. Current-version dispositions are recorded exclusively in `specs/056-a7-p6-delivery-acceptance/`.
3. **Secret-Free & Proprietary-Text-Free Package**: No artifact under `specs/056-a7-p6-delivery-acceptance/` may contain raw passwords, JWT tokens, session cookies, or full proprietary task text from `real-data/plan.mpp`.

---

## 2. Deliverable Package Layout (`D04`)

The delivery package under `specs/056-a7-p6-delivery-acceptance/` MUST contain:

| Path | Purpose |
| --- | --- |
| `guide.md` | Concise Persian Employer Test Guide (`راهنمای کوتاه تست کارفرما`) with environment setup/reset, 5-role login guide, step-by-step positive/negative scenarios, reference file hashes & expected figures, and the 4-category status summary. |
| `traceability.md` | Master 56-item audit disposition matrix (`P01`–`D04`) with owning phase, requirement mapping, current evidence, and 4-bucket employer classification. |
| `handoff.md` | Final A.7-P6 handoff summary with version identity, verification summary, residual limits, and employer sign-off boundary. |
| `evidence/package.json` | Machine-readable `EmployerDeliveryPackage` metadata (`version_id`, `environment_id`, `role_personas`, `summary_buckets`, `technical_readiness`, `employer_decision`). |
| `evidence/audit-disposition.json` | Machine-readable array of 56 `AuditDispositionRecord` objects. |
| `evidence/reconciliation.md` & `.json` | Reference schedule reconciliation ledger (`real-data/plan.mpp` and XML/XER fixtures: source vs preview vs job summary vs stored DB counts + repeat append result + warning codes). |
| `evidence/scenarios.md` & `.json` | Execution records for all 28 acceptance scenarios (`POS-01`–`POS-10`, `NEG-01`–`NEG-14`, `OPS-01`–`OPS-04`). |
| `evidence/accounts.md` | Secret-free 5-persona role matrix and repeatable seed/provisioning commands. |
| `evidence/defects.md` | Defect log (`DefectRecord` entries; empty or resolved for in-scope blocking items). |
| `evidence/minutes.md` | Unsigned employer acceptance minutes (`صورت‌جلسه پذیرش کارفرما`) with `decision: pending`, blank `employer_signer_role`, and blank `employer_signed_at`. |
| `evidence/verification.md` | Consolidated technical verification report linking API/DB pytest JUnit XML, P5 real worker/containment manifests, and P6 Playwright browser E2E results/screenshots. |
| `evidence/validate_package.py` | Deterministic validator verifying schema, 56-item completeness, 28-scenario completeness, `plan.mpp` hash/counts, secret-scan cleanliness, and unsigned employer fields. |

---

## 3. Required Acceptance Scenario Catalog (`D03` — 28 Scenarios)

### 3.1 Positive Reference Project Journey (`POS-01`–`POS-10`, `US2`)

- **`POS-01`**: Create project in `draft` (`پیش‌نویس`), populate required metadata, select active organizational unit, contract type, and measurement unit from governed reference catalogs, and author all 6 kickoff charter sections (`P01`, `P02`, `M01`, `M02`).
- **`POS-02`**: Submit charter and enforce Separation of Duties (creator blocked from self-approval) and activation gates (project manager assigned, scope defined, budget ceiling > 0) before independent approver transitions project to `active` (`P03`, `P04`).
- **`POS-03`**: Submit and decide a formal post-approval project change request (`ProjectChangeRequest`), verifying unchanged active fields while pending/rejected and atomic update + before/after audit record upon independent approval (`P05`).
- **`POS-04`**: Create >=3-level WBS hierarchy with code, name, parent, sort order, weight (100% sibling rule), `responsible_user`, and `completion_criterion`; move/renumber a node; save a WBS template and instantiate an independent copy into a second project proving zero mutation coupling (`W01`–`W03`, `W05`, `W06`, `M04`).
- **`POS-05`**: Run schedule preview on `real-data/plan.mpp` and XML/XER fixtures, inspecting discrepancy and row-level warning reports before confirmation (`I01`, `I12`, `I13`, `D01`).
- **`POS-06`**: Confirm `append` (`افزودن / به‌روزرسانی`) import of `real-data/plan.mpp` (`SHA-256: 3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553`) and XML/XER fixtures; reconcile stored DB counts (**6 WBS nodes, 72 activities, 72 relationships** for `plan.mpp`), milestones (`duration_days = 0`), converted workday lags (`480` min/day), and warning codes (`activity_without_parent` for `شروع`/`پایان`, `predecessor_is_summary` for `8055`/`8084`/`8102`/`8120`, `calendar_not_applied`) (`W07`, `S02`–`S04`, `I03`–`I05`, `I14`, `I21`, `I22`).
- **`POS-07`**: Re-import the same schedule file in `append` mode; verify `nothing_changed = true`, `0` duplicate WBS/activities/relations, and `0` redundant empty baseline snapshots (`I08`, `S05`).
- **`POS-08`**: Execute `replace` (`جایگزینی ایمن`) import on an unprotected project (soft-deleting old schedule rows and replacing while preserving import/audit history) and verify `baseline_replace_forbidden` refusal when protected execution history (approved baseline / progress / period report / change request / measurement) exists (`I06`, `S05`).
- **`POS-09`**: Inspect the 4 activity date sets (approved baseline, planned, actual, forecast), milestones, delay report against approved baseline, and critical-path validity gate across table, Gantt, and WBS summary views (`S01`, `S06`–`S08`).
- **`POS-10`**: Execute full project lifecycle transitions: `active` → `suspended` → `active` (with mandatory reason and confirmation), `active` → `completed` → `undo-complete` (system admin only, restoring exact `previous_status`), and `archive` → `restore` (system admin only, restoring exact `previous_status` with 100% preservation of WBS, activities, relations, baselines, and charter) (`P06`, `P07`, `P09`, `P10`, `M03`).

### 3.2 Independent Negative, Adverse, Concurrency & Access-Boundary Scenarios (`NEG-01`–`NEG-14`, `US3`)

- **`NEG-01`**: Reject duplicate/invalid project code or normalized duplicate WBS code across manual entry and import (`P01`, `W04`).
- **`NEG-02`**: Reject invalid or cross-project parent WBS node (`W01`, `W03`).
- **`NEG-03`**: Reject direct and indirect cycles in WBS hierarchy and activity predecessor-successor relations (`W03`, `S03`).
- **`NEG-04`**: Reject impossible activity dates (`finish < start`) and manual non-milestone activities with zero duration (`S01`, `S02`).
- **`NEG-05`**: Handle missing predecessor and summary predecessor links with explicit structured codes without partial schedule corruption (`S03`, `I05`, `I07`).
- **`NEG-06`**: Reject empty, corrupt XML (`msp_invalid_xml`), wrong-extension (`invalid_file_type`), truncated OLE (`mpp_unsupported`), password-protected (`mpp_password_protected`), and oversized (`> 50 MB`) uploads with zero job/schedule writes and single-step file re-selection (`I02`, `I15`).
- **`NEG-07`**: Cancel after schedule preview before confirming import; verify zero queued jobs and zero DB mutations (`I06`, `I15`).
- **`NEG-08`**: Recover active/completed import attempt state after connection drop or page reload without starting a second job (`I10`, `I15`).
- **`NEG-09`**: Block duplicate/concurrent submit and in-flight drag-and-drop across MSP and P6 pipelines (`import_already_active` / disabled UI controls) (`I11`, `I16`).
- **`NEG-10`**: Abort queued background import when actor permission is revoked or project is archived/deleted before worker execution/commit, leaving zero schedule writes (`I18`, `P08`).
- **`NEG-11`**: Enforce cross-project isolation between Project A and Project B across WBS, schedule, baseline, and import endpoints (`P11`, `I10`).
- **`NEG-12`**: Enforce Viewer (`view_only`) read-only restriction across project, WBS, baseline, and schedule import actions (`P11`).
- **`NEG-13`**: Verify non-member System Administrator read-only observation access (`A.6` exception) and restricted administrative lifecycle actions (`undo-complete`, `restore`) (`P07`, `P09`, `P11`).
- **`NEG-14`**: Enforce strict read-only lock on `archived` projects across all project, charter, WBS, activity, baseline, preview, and import endpoints (`P08`).

### 3.3 Bilingual, Responsive, Keyboard & Operational Continuity Scenarios (`OPS-01`–`OPS-04`, `US4`)

- **`OPS-01`**: Verify Persian (`fa`, RTL) and English (`en`, LTR) rendering of project lifecycle, WBS, and schedule import screens without raw translation keys (`I17`).
- **`OPS-02`**: Verify desktop (`1280x800`) and mobile (`390x844`) responsive viewports across project, WBS, and schedule import flows (`I17`).
- **`OPS-03`**: Verify keyboard-only navigation (`Tab`, `Shift+Tab`, `Enter`, `Escape`), focus management, and error recovery in project lifecycle and schedule import dialogs (`I15`, `I17`).
- **`OPS-04`**: Verify operational continuity with P5 real worker/containment/7-day byte retention evidence (`I09`, `I19`, `I20`, `D02`) bound to the exact candidate `schedule_tree_sha256` (`52669f25e2271f43a8fdd93501a7175d8bb695faa697618bcccdfe0a58b26e70`).
