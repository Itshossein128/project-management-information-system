# Research: Contractor Stakeholder Select

**Feature**: `027-contractor-stakeholder-select`  
**Date**: 2026-10-17

## Decision 1 — Source of contractor identity

**Decision**: Project `Stakeholder` rows classified as contractors are the sole source for in-scope پیمانکار pickers.

**Rationale**: Spec FR-002/FR-003 name ذینفعان explicitly. The separate `subcontractors` app and `contracts.Contract` lists are different domains (performance / commercial), not the stakeholder register.

**Alternatives considered**:
- Reuse `subcontractors.Subcontractor` — rejected; product intent is ذینفعان.
- Reuse `contracts.Contract` (current daily-report combo) — rejected for this feature; mismatches FR-002.
- Free-text creatable select — rejected; violates FR-007.

## Decision 2 — How a stakeholder is classified as contractor

**Decision**: Canonical `role` value `contractor` on `projects.Stakeholder`. Writes that use Persian label `پیمانکار` (or common English synonyms) normalize to `contractor`. List/filter uses `role=contractor` plus `status=active` (and soft-delete exclusion). ذینفعان UI exposes a role control that includes contractor.

**Rationale**: `role` already exists on the model and serializer; no new column required for classification. Stable English code keeps API/filter language-independent (constitution III). Normalization avoids duplicate spellings breaking FR-008 filters.

**Alternatives considered**:
- New `is_contractor` boolean — clearer but extra field/migration for something role already expresses.
- Free-text role match only (`icontains`) — fragile; misspellings leak non-contractors or hide real ones.
- New `party_kind` enum — heavier than needed for v1.

## Decision 3 — Durable link + display name

**Decision**: In-scope operational models gain a nullable FK to `projects.Stakeholder` (SET_NULL on delete). Existing CharField name columns remain as a denormalized display snapshot written on save from the stakeholder’s `name`. New writes require a valid active contractor FK (except warehouse department rows that already clear contractor). Reads always prefer snapshot name for history (FR-006).

**Rationale**: Satisfies FR-005 (identity) and FR-006 (stable display after inactive/delete). Avoids JOIN-only display that would blank after soft-delete if names were not snapshotted.

**Alternatives considered**:
- FK only, no CharField — breaks historical display and Excel export parity.
- CharField only with server-side allow-list validation — no durable identity; rename drift and ambiguous duplicates.

## Decision 4 — Department activity (P1 surface)

**Decision**: Add `contractor_ref` → `Stakeholder` on `DepartmentActivityRecord`. Serializer accepts `contractor_ref` (UUID); validates same-project, role=contractor, active, not soft-deleted; sets `contractor` from stakeholder name. Filter query param may accept stakeholder UUID and/or name contains for backward compat. Import resolves پیمانکار cell to an existing contractor by exact name (case-trimmed) or UUID; otherwise row fails validation.

**Rationale**: Primary reported UI (`department-activity-record-modal`) today is a required free-text Input. This is the P1 path.

## Decision 5 — Daily report / labor (P2 surfaces)

**Decision**: Stop using `contracts` list for the پیمانکار combo. Add `contractor_ref` → `Stakeholder` on `DailyReportActivity` and labor-camp entry models that expose `subcontractor_name`. Keep legacy `subcontractor_ref` → `Contract` nullable and unused by the new picker (no destructive drop in v1). On save, set `subcontractor_name` from the chosen stakeholder. UI options come from the same contractors endpoint/filter as department activity.

**Rationale**: Spec FR-009 includes these labels. Changing the existing Contract FK type would break migrations and any stored links; additive Stakeholder FK is safer (constitution II/V).

**Alternatives considered**:
- Repoint `subcontractor_ref` to Stakeholder — cleaner long-term but high migration/risk cost for v1.
- Leave daily reports on Contract — fails FR-002/P2 consistency.

## Decision 6 — Project settings / create wizard پیمانکار

**Decision**: Treat as in-scope party picker: add optional `contractor_ref` → Stakeholder on `Project`; sync `Project.contractor` CharField from selected name. Empty selection clears the FK and may clear or leave CharField empty per existing blank rules.

**Rationale**: Matches spec assumption default; same control pattern as operational forms.

## Decision 7 — API shape for options

**Decision**: Extend existing `GET /api/v1/projects/{id}/stakeholders/?role=contractor&status=active` (paginated `results` already). Frontend shared helper `fetchProjectContractors(projectId)` wraps that filter. No new micro-resource required for v1; optional thin alias endpoint may be added later if list payload is too heavy (contacts redaction already applies).

**Rationale**: Minimal coherent change (constitution V); reuses ACL and redaction rules.

## Decision 8 — UI control

**Decision**: Shared non-creatable select/combobox (existing `Select` or searchable non-add combobox). Do **not** use `CreatableSelect` for پیمانکار (that component’s Add path violates FR-007). Empty state copy points users to ذینفعان. Role field added on stakeholders create/edit form with contractor option labeled پیمانکار.

**Rationale**: Constitution VII requires accessible selects; creatable “Add” is explicitly wrong for this field.

## Decision 9 — Out of scope for this plan

**Decision**: Do not merge or replace `subcontractors` / پیمانکار فرعی performance register. Do not change decision-support alternative free-text samples. No inline create-from-picker.

## Decision 10 — Verification approach

**Decision**: pytest for stakeholder filter, department activity write/filter/import validation, project isolation; frontend typecheck; browser check of department activity modal + ذینفعان role + at least one P2 surface; fa/en labels for role and empty state.

**Rationale**: Constitution VI — domain field change spans models, API, UI, import.
