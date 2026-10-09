# Data Model: Risk, Quality & Safety

## Existing (extended): `risk.RiskEvent`

Project-scoped soft-delete register row. Discriminator `event_type` separates **risk** and **issue** from legacy barrier/delay/claim/change_order.

### New / clarified fields (risk & issue)

| Field | Type | Rules |
|-------|------|-------|
| event_type | enum | Add `issue`. Risk register UI/API treat `risk` and `issue` as separate paths |
| cause | text | Optional blank; recommended for risk |
| consequence | text | Optional blank |
| response | text | Response strategy (accept/mitigate/transfer/avoid narrative in v1) |
| probability_level | 1–5 \| null | FR probability scale |
| impact_severity_level | 1–5 \| null | FR impact severity scale |
| composite_score | 1–25 \| null | = product when both levels set; else null (**never** invent) |
| status | RiskStatus | `open`, `under_review`, `mitigated`, `closed`, `residual` |
| due_date | date \| null | Prefer over / alias `target_resolution_date` (keep legacy field synced or deprecate in serializer) |
| impact_on_quality | bool | default false |
| impact_on_safety | bool | default false |
| impact_on_contract | bool | default false |
| impact_on_liquidity | bool | default false |
| cost_item | FK → CostBreakdownNode \| null | Same project |
| contract | FK → Contract \| null | Same project |
| related_decision_ref | char/uuid \| null | Opaque until workflow 15 |
| related_decision_note | text | Optional |

**Retained**: `probability` (decimal), `severity` (enum), `impact_on_schedule`, `impact_on_cost`, `owner`, `corrective_action`, `activity`, audit soft-delete, claim links.

### Status migration

| Old (`BarrierStatus`) | New (`RiskStatus`) |
|-----------------------|--------------------|
| open | open |
| in_progress | under_review |
| resolved | closed |

Barrier UI may label `closed` as “resolved” via i18n.

### Score rules

- If `probability_level` **or** `impact_severity_level` is null → `composite_score = null`.
- On create/update when score incomplete and client omits status → default `under_review`.
- Matrix: open-like = `open` \| `under_review` \| `mitigated` \| `residual` (exclude `closed`).

### Close with open actions

Child **`RiskAction`** (optional v1 table):

| Field | Type | Rules |
|-------|------|-------|
| risk_event | FK RiskEvent | CASCADE |
| description | text | required |
| due_date | date \| null | |
| owner | FK User \| null | |
| status | open \| done | default open |

When transitioning parent to `closed` and any `RiskAction.status=open` (or non-empty unresolved corrective text policy—prefer child rows): require `acknowledge_open_actions=true` or reject with `open_actions_warning`.

---

## New: `Inspection`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | required |
| wbs | FK WBS | **required** |
| responsible_user | FK User | **required** |
| inspection_date | date | **required** |
| stage | plan \| request \| result | default result for simple capture |
| result | pass \| fail \| conditional \| pending \| null | |
| description | text | |
| activity | FK Activity \| null | optional same-project |

**Validation**: missing wbs, responsible_user, or inspection_date → 400 (SC-004).

---

## New: `Nonconformity`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | required |
| inspection | FK Inspection \| null | preferred link |
| wbs | FK WBS \| null | copy from inspection when linked |
| description | text | required |
| status | open \| closed | |
| raised_date | date | required |

---

## New: `CorrectiveAction`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | required |
| nonconformity | FK Nonconformity | required |
| description | text | required |
| responsible_user | FK User \| null | |
| due_date | date \| null | |
| status | open \| done | |
| completed_date | date \| null | |

---

## New: `HseEvent`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | **required** |
| wbs | FK WBS \| null | optional |
| kind | incident \| near_miss | required |
| event_date | date | **required** |
| description | text | required |
| severity | optional enum/text | |
| status | open \| closed | |

---

## New: `WorkPermit`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | required |
| permit_date | date | required |
| permit_type | char | |
| responsible_user | FK User \| null | |
| description | text | |
| status | active \| closed \| expired | |

---

## New: `SafetyTraining`

| Field | Type | Rules |
|-------|------|-------|
| project | FK Project | required |
| training_date | date | required |
| topic | char/text | required |
| trainer_or_responsible | FK User or char | |
| attendees_count | int \| null | |
| description | text | |

---

## Derived: Quality & Safety Period Report

Computed DTO for `(project_id, date_from, date_to)`:

| Section | Source filter |
|---------|----------------|
| inspections | `inspection_date` in range |
| nonconformities | `raised_date` in range |
| corrective_actions | `due_date` or created in range (document: `raised` via NCR date or CA due_date—v1: include if CA.due_date in range **or** NCR.raised_date in range) |
| incidents | HseEvent kind=incident, event_date in range |
| near_misses | kind=near_miss |
| work_permits | permit_date in range |
| trainings | training_date in range |

Empty section = `[]`. Do not invent summary rates that imply “zero incidents = perfect” unless counts are explicit and labeled.

---

## Relationships (overview)

```text
Project
├── RiskEvent (risk | issue | barrier | …)
│   ├── RiskAction*
│   ├── Activity?
│   ├── CostBreakdownNode?
│   └── Contract?
├── Inspection → WBS, User
│   └── Nonconformity → CorrectiveAction
├── HseEvent (incident | near_miss)
├── WorkPermit
└── SafetyTraining
```

## State transitions

**Risk status** (allowed freely in v1 except close warning):  
`open` ↔ `under_review` ↔ `mitigated` ↔ `residual` → `closed` (with acknowledge if open actions).

**Issue**: same status set; scoring fields optional (issues may omit probability).

**Inspection**: stage plan → request → result (soft progression; not workflow-engine enforced).

**NCR / CA / HSE**: open → closed/done.
