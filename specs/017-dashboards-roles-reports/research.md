# Research: Dashboards, Roles & Reports

**Date**: 2026-10-10

## Findings

### Existing coverage (keep)

- Project membership + role permissions (`permissions.constants`, `HasProjectPermission`); `view_dashboard` already on PM / planning / finance / viewer.
- Unified `projects.kpi_service.build_project_kpis` composing EVM, cash, schedule counts, alerts (cached).
- Progress period reports with figure provenance: `source_type`, `source_id`, `source_path`, `source_approved`, `last_updated_at` (`schedule` period report models/services).
- Project capabilities (`ProjectCapabilitySetting`) for enable/disable modules.
- Soft SoD warn already on HR capacity exception approve (`soft_sod_warn` when creator == approver).
- Domain dashboards/lists: progress UI, portfolio liquidity, risk register, costs, etc.
- System roles today: `project_manager`, `planning_engineer`, `site_supervisor`, `field_supervisor`, `finance_manager`, `procurement_officer`, `document_controller`, `viewer`.

### Gaps to close

1. KPI payload lacks systematic **figure_key + drill** to source rows with approval + timestamps.
2. No **role dashboard packs** that filter indicators and projects by role.
3. SoD not **hard-enforced** on material final approves (IPC, cost/payment, budget-change / workflow, project change request).
4. FR minimum role set incomplete (executive/approver, project controls alias, site specialist, supervisor/consultant).
5. No unified **standard report catalog** + **export version** with extraction date + filters.
6. Disabled capabilities may still surface misleading zeros on some aggregates.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bounded context | Extend **`projects`** (packs, KPI drill, export versions) + **`permissions`** (roles, SoD helper); consume domain services read-only | Principle V; dashboards must not become SoR |
| Provenance contract | Reuse progress-report shape: `source_type`, `source_id`, `source_path`, `source_approved`, `last_updated_at` (+ `figure_key`, optional `label`) | Already tested pattern; SC-001 |
| KPI enrichment | Each numeric figure in pack/KPI response carries `figure_key` and `drill` descriptor (`{ path, params }` or relative API); drill list endpoint returns constituent rows | FR-002 |
| Role packs | Server builds pack by role codename(s) of member; indicator groups from static catalog in `dashboard_pack_service`; membership filters projects | FR-003–009 |
| Phase-1 packs | Deliver **executive** (portfolio strip), **project_manager**, **finance_manager** (+ map `planning_engineer` → controls pack indicators); HR/site + unit-manager stubs return inactive groups where data missing | Spec assumption |
| Disabled capability | If `ProjectCapabilitySetting.enabled=false` for dependency → indicator `status: inactive` (omit value or null), never `0` as success | SC-006 |
| Approved data default | Standard daily/weekly/monthly/portfolio reports default `approved_only=true`; unapproved rows excluded unless `include_unapproved=true` and each figure labeled | FR-016 |
| Export metadata | New `ReportExportVersion`: report_type, filters JSON, extracted_at, extracted_by, file_url/payload ref, project nullable for portfolio | FR-012, SC-004 |
| Confidential fields | Reuse `view_wage` / `view_sensitive_contacts` (and similar) on report serializers — redact when missing | FR-015 |
| SoD | `permissions.sod.assert_not_self_final_approve(created_by_id, actor)` raises `CodedValidationError` `sod_self_approve` on **final** approve; apply to IPC approve, cost/payment approve, project change-request approve, workflow instance final approve / budget_change; HR soft-warn may upgrade to hard for consistency on capacity exceptions marked material | FR-014, SC-003 |
| Sole member | No bypass for self-approve; another user or global admin required (admin still subject to product policy — default: global admin may override only if documented; v1 **no override** except `is_superuser` for break-glass) | Edge case |
| Role mapping | Keep existing codes; **add** system roles: `executive_approver`, `project_controls` (seed like planning_engineer + dashboard), `site_specialist` (alias/extend site_supervisor perms), `supervisor_consultant` (view-heavy); map FR names in docs; do not rename existing codes | FR-013 |
| Viewer | Packs readable with `view_dashboard`; no approve/export-of-confidential; no workflow actions from UI | Edge case |
| Catalog reports | Registry of report_type → builder function (wrap existing period/daily/portfolio/cash/risk summaries); v1 implement subset: weekly/monthly progress, portfolio cash summary, budget variance stub, risk/issue summary — expand to full FR-010 list iteratively with same export wrapper | FR-010 |
| Filters | Shared query params: `project`, `unit`, `date_from`/`date_to`, `contract`, `wbs`, `cbs`, `owner`, `status` — ignored when N/A to report type | FR-011 |
| UI | Project dashboard route shows PM/finance/controls pack by membership roles; portfolio/executive route for multi-project; standard reports page with export download; FigureDrillDrawer | Matches stories |

## Alternatives considered

- **New BI/analytics Django app with warehouse tables** — rejected (duplicates SoR, Principle V).
- **Soft SoD warn only** (HR pattern) — rejected for material final approve (SC-003 requires 0% self-approve success).
- **Client-only role packs** — rejected (authz must be server-side).
- **Require all six role packs + full FR-010 catalog in one release** — rejected; phase-1 subset with inactive stubs matches spec assumptions.
- **PDF-only exports without stored metadata** — rejected; SC-004 needs extraction date + filters on output/version.

## NEEDS CLARIFICATION

None remaining — Technical Context unknowns resolved above.
