# Reference Schedule Reconciliation Ledger (A.7-P6)

**Phase**: `A.7-P6` (`specs/056-a7-p6-delivery-acceptance`)  
**Machine-Readable Ledger**: `specs/056-a7-p6-delivery-acceptance/evidence/reconciliation.json`  
**Audit Coverage**: `D01`, `D03`, `I01`, `I03`, `I04`, `I05`, `I08`, `I12`, `I13`, `I21`, `I22`, `W07`, `S01`–`S08`

---

## 1. Employer Reference File (`real-data/plan.mpp`)

| Attribute | Value |
| --- | --- |
| **Fixture ID** | `real_data_plan_mpp` |
| **File Path** | `real-data/plan.mpp` |
| **SHA-256** | `3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553` |
| **Size (Bytes)** | `777216` (`777,216` bytes — unchanged) |
| **Container Type** | `Composite Document File V2 Document, Little Endian, Os: Windows, Version 10.0` (Microsoft Project) |

### 1.1 Stage-by-Stage Count Reconciliation

| Stage | WBS Nodes | Activities | Predecessor Relationships | Baselines | Notes |
| --- | --- | --- | --- | --- | --- |
| **Parsed Source (`MPXJ -> MSPDI`)** | `6` summary tasks (`Summary=1`) | `74` leaf tasks (`Summary=0`) | `83` raw `PredecessorLink` rows | N/A | Total `80` tasks in source (`6 + 74`). |
| **Governed Contract Adjustments (`T034` Decision 2026-11-12)** | `0` omitted | `-2` omitted (`شروع` and `پایان` have no valid parent WBS node -> `activity_without_parent`) | `-4` summary predecessors (`8055`, `8084`, `8102`, `8120` -> `predecessor_is_summary`) and `-7` links targeting omitted parentless milestones | N/A | Zero duration (`0`) is stored only for activities with a valid parent; parentless rows are never attached to an arbitrary WBS node. |
| **Preview Output (`/import/msp/preview/`)** | `6` | `72` | `72` | `0` (preview is read-only) | Reports structured warning codes: `activity_without_parent`, `predecessor_is_summary`, `calendar_not_applied`. |
| **First `append` Import (`replace=false`)** | `6` | `72` | `72` | `1` (working baseline snapshot) | 100% match between preview and stored database rows (`POS-05`, `POS-06`). |
| **Repeat `append` Import (`replace=false`)** | `6` (`+0` duplicates) | `72` (`+0` duplicates) | `72` (`+0` duplicates) | `1` (`+0` extra baselines) | Returns `nothing_changed: true` (`POS-07`, `I08`, `S05`). |

### 1.2 Explicit Reconciliation of Historical Probe (`80 / 83 / 79`) vs Approved Target (`6 / 72 / 72`)

- **Why `72` activities instead of `74` (or `80` total tasks)**:
  - Out of `80` total MSP tasks, `6` are summary tasks (`Summary=1`) mapped to `WBS` nodes (`6` WBS nodes).
  - Out of `74` leaf tasks (`Summary=0`), `2` rows (`شروع` and `پایان`) sit at the root level without any parent summary task. Per stakeholder/user decision (`2026-11-12`, `specs/053-a7-p3-import-fidelity/handoff.md`), parentless activities are omitted with structured `activity_without_parent` warnings, yielding `74 - 2 = 72` stored `Activity` rows.
- **Why `72` relationships instead of `83` (or `79`)**:
  - Out of `83` raw `PredecessorLink` entries, `4` reference summary tasks (`UID` `8055`, `8084`, `8102`, `8120`), which are skipped with structured `predecessor_is_summary` warnings (`83 - 4 = 79`).
  - Of the remaining `79` links, `7` reference the omitted parentless `شروع`/`پایان` rows and are skipped along with those omitted rows (`79 - 7 = 72` stored `ActivityRelation` rows).

---

## 2. Valid MSP XML & Primavera P6 Fixtures

| Fixture ID | File Path | SHA-256 | Size (Bytes) | Stored Counts (`WBS / Activities / Relations`) | Repeat `append` (`nothing_changed`) | Expected Warning Codes |
| --- | --- | --- | --- | --- | --- | --- |
| `valid_msp_xml` | `specs/051-a7-p1-project-reference/evidence/fixtures/branch.xml` | `c91d4f6e92bf5b0e201f3229e6ca177ab2b25464611b08398e0b22026ee80778` | `662` | `1 / 2 / 0` | `true` (`0` duplicates, `0` extra baselines) | `calendar_not_applied` |
| `valid_p6_xer` | `specs/051-a7-p1-project-reference/evidence/fixtures/branch.xer` | `4c992c7a4971605906a116f0a54e8d2081067ff5ec0d10ab6d87ca087272e602` | `265` | `3 / 2 / 0` | `true` (`0` duplicates, `0` extra baselines) | `calendar_not_applied` |
| `valid_p6_xml` | `apps/api/core/schedule/tests/fixtures/mpp/duration-test9.xml` | `5d790c14cbeb86fa9c9647fb960a3c19272b859781f90f5616dc47926386bc05` | `26458` | `1 / 5 / 0` | `true` (`0` duplicates, `0` extra baselines) | `calendar_not_applied` |
