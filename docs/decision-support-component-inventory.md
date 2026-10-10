# Component inventory — Decision Support (تصمیم‌یار)

**Purpose:** Map [decision-support](./decision-support/README.md) docs to **existing** reusable building blocks and **new** components/modules to create. Goal: avoid duplicate matrix/form/result UIs, keep calculation engines pure, and follow Velora clean-code patterns (thin routes, shared primitives, one responsibility per module).

**Scope:** Frontend (`apps/web`) and backend calculation/API seams (`apps/api/core`). This inventory is a design guide; it does not claim the module is implemented.

**Related docs:** [module scope](./decision-support/01-module-scope.md) · [inputs](./decision-support/02-decision-inputs.md) · [execution records](./decision-support/08-execution-records.md) · [acceptance](./decision-support/10-acceptance-checks.md)

---

## Design principles (prevent repetition)

1. **One matrix editor, many adapters** — SAW/TOPSIS performance, AHP pairwise, DEMATEL intensity, and ISM binary all share one numeric grid shell; only cell constraints and labels differ.
2. **Engines are pure and UI-free** — Port formulas from [ranking reference](./decision-support/09-ranking-reference.md) into services/helpers with no React/Django views inside. UI only maps form state ↔ engine DTOs.
3. **Case shell ≠ method panel** — Case metadata, method multi-select, run history, and immutable snapshots live once; each method mounts a panel that reuses shared input/result pieces.
4. **No silent merge of rankings** — SAW and TOPSIS result tables are separate instances of the same result-table component (different `method` prop), never one blended score (see AC03/AC25).
5. **Reuse shell chrome** — Page header, empty/error/loading, tabs, dialogs, toasts, i18n, and project nav stay on existing layout/UI kits.
6. **Validate once, surface once** — Shared input validators (names, dims ≤ 10, finite non-negative, benefit/cost) feed both client hints and server `CodedValidationError` with cell/field paths (AC07–AC12, AC26).

---

## Capability map (docs → UI surface)

| Doc | Product surface | Shared vs method-specific |
| --- | --- | --- |
| 01 scope | Method picker; independent run buttons | Shared case + picker |
| 02 inputs | Criteria/alternatives lists; weights; types; matrices | Shared editors + validators |
| 03 SAW | Run + ranked scores | Shared ranking form + SAW engine + ranking result |
| 04 TOPSIS | Run + scores + distances | Shared ranking form + TOPSIS engine + ranking result |
| 05 AHP | Pairwise matrix + weights + CR warning | Pairwise matrix mode + AHP engine + weight result |
| 06 DEMATEL | 0–4 effect matrix + prominence/relation | Intensity matrix mode + DEMATEL engine + criteria metrics result |
| 07 ISM | Binary relation matrix + layers | Binary matrix mode + ISM engine + layer result |
| 08 execution | Run history; immutable input snapshot; re-run | Case history list + snapshot viewer |
| 09 reference | Backend/port of `rank_options` (editable reference) | Pure Python engines (not a UI) |
| 10 acceptance | Tests against AC01–AC26 | Pytest + UI smoke; not extra components |

---

## Already available — reuse these

Prefer composition over new primitives. Paths are under `apps/web/src/` unless noted.

### Layout, chrome, feedback

| Component / module | Path | Reuse for decision support |
| --- | --- | --- |
| `PageHeader`, `PageSkeleton`, `Breadcrumb` | `components/layout/page-header.tsx` | Case / method page titles and loading shell |
| `EmptyState` | `components/layout/empty-state.tsx` | No cases, no runs, empty method selection |
| `QueryErrorState` | `components/layout/query-error-state.tsx` | Failed load of case or history |
| `AppShell` / sidebar | `components/navigation/app-shell.tsx`, `project-navigation.config.ts` | Register one project nav entry; do not invent a second shell |
| Tabs / Card / Badge / Alert / Dialog / Drawer / Toast | `components/ui/*` | Method tabs, CR warning (`Alert`), confirm re-run, cell detail drawer |
| Form kit | `components/form/*` (`Input`, `Select`, `Button`, `Label`, `TextArea`, `Field`) | Case title, names, weight fields, benefit/cost selects |
| `JalaliDatePicker` | `components/form/JalaliDatePicker.tsx` | Optional “as of” / decision date on case (if product wants it) |

### Tables, grids, numeric entry

| Component / module | Path | Reuse for decision support |
| --- | --- | --- |
| `EditableGrid` | `components/daily_reports/EditableGrid.tsx` | **Inspiration / adapt**, not wholesale import: good for named rows + typed cells; pairwise/symmetric matrices need a dedicated square matrix (below). Prefer extracting shared cell rendering if duplication grows |
| `ui/table`, `ui/data-table` | `components/ui/table.tsx`, `data-table.tsx` | Read-only ranking / weight / prominence tables |
| `ScoreSlider` + `ui/slider` | `components/subcontractors/ScoreSlider.tsx` | AHP 1–9 or DEMATEL 0–4 entry in a cell popover; wrap with correct min/max/step rather than forking |
| TanStack Table usage in `components/grid/*` | `components/grid/` | Large result lists / history if volume grows |

### Charts & visual summaries (optional reuse)

| Component / module | Path | Reuse for decision support |
| --- | --- | --- |
| `PerformanceRadarChart` | `components/subcontractors/PerformanceRadarChart.tsx` | Optional alternative-profile view after ranking (do not require for MVP) |
| Dashboard figure grid / KPI card | `components/dashboard/DashboardFigureGrid.tsx`, `components/progress/KPICard.tsx` | Optional executive strip of last-run summaries; keep drill semantics separate from MCDM |
| Economic / cash charts | `components/economic/*`, `components/cashflow/*` | **Do not** reuse for MCDM math; only if a future portfolio viz is explicitly scoped |

### Patterns to copy (not domain UI)

| Pattern | Where | Apply as |
| --- | --- | --- |
| Thin route + domain panels | e.g. `routes/project-costs.tsx` + `components/costs/*` | `project-decision-support.tsx` + `components/decision-support/*` |
| API client module | `app/lib/api/*.ts` | New `app/lib/api/decision-support.ts` |
| Wizard / workbench composition | `costs/AllocationWizard.tsx`, `cashflow/allocation/AllocationWorkbench.tsx` | Multi-step case setup only if needed; prefer tabs over a second wizard framework |
| Approval / status bars | `daily_reports/ApprovalStatusBar.tsx`, `contracts/IPCWorkflowBar.tsx` | Visual pattern for “validation OK / CR warning / run locked” — do not couple to IPC/daily-report domain |
| Immutable export metadata | `projects` `ReportExportVersion` + report UI | Mental model for immutable run snapshots (AC24); new model, same idea |
| Coded validation errors | API `CodedValidationError` + toast mapping | Cell/field-keyed errors for AC26 |
| Workflow “management decision” | `routes/project-decisions-workflow.tsx` | **Separate product concept** (rationale log). Link optionally; do not overload that screen with SAW/TOPSIS matrices |

### Backend building blocks to reuse

| Piece | Path | Reuse |
| --- | --- | --- |
| Project membership + `HasProjectPermission` | `permissions/project.py` | All case/run endpoints |
| Soft patterns / UUID models | sibling domain apps | New `decision_support` (or `mcdm`) Django app |
| Pytest + fixtures style | e.g. `projects/tests/`, `risk/tests/` | AC14–AC22 numeric cases |
| Ranking reference function | [09-ranking-reference.md](./decision-support/09-ranking-reference.md) | Port into pure service modules; keep the markdown copy editable as the doc set requires |

---

## New components / modules to create

Create under a dedicated folder so method UIs stay cohesive:

```text
apps/web/src/components/decision-support/
apps/web/src/app/lib/api/decision-support.ts
apps/web/src/app/routes/project-decision-support.tsx   # or similar
apps/api/core/decision_support/                       # models, services, views, tests
```

### A. Shared case & orchestration (create once)

| New component / module | Responsibility | Do **not** duplicate by… |
| --- | --- | --- |
| `DecisionCaseHeader` | Title, project context, last-run summary chips | Copying `PageHeader` internals — compose it |
| `MethodPicker` | Multi-select SAW / TOPSIS / AHP / DEMATEL / ISM with independence copy | Hard-coding five separate pages with five nav items |
| `DecisionCaseWorkspace` | Tabs/panels for selected methods + shared criteria/alternatives | Embedding five full page copies |
| `NamedListEditor` | Add/remove/reorder unique non-empty names (criteria **or** alternatives), max 10 | Separate CriteriaEditor + AlternativesEditor with forked validation |
| `WeightVectorEditor` | `n` non-negative weights + live normalized preview | One weight UI per ranking method |
| `CriterionTypeToggle` | Per-criterion `benefit` \| `cost` | Duplicating selects inside SAW and TOPSIS forms |
| `ValidationIssueList` | Field/cell path + message from client/server | Ad-hoc `alert()` / toast-only without location (breaks AC26) |
| `RunActionBar` | Validate → Run selected method → show blocking errors | Per-method submit buttons with different validation pipelines |
| `ExecutionHistoryList` | Past runs: method, time, actor, open snapshot | Editing previous runs in place (forbidden by AC24) |
| `InputSnapshotViewer` | Read-only frozen inputs for a run | Reusing the live editable matrix for history |

### B. Shared matrix shell (create once, configure per method)

| New component | Responsibility | Config knobs |
| --- | --- | --- |
| `SquareMatrixEditor` | `n × n` labeled by criteria; cell focus + keyboard | `valueDomain`, `symmetricMode`, `diagonalPolicy` |
| `RectangularMatrixEditor` | `m × n` performance matrix (alternatives × criteria) | Non-negative finite; empty ≠ 0 (AC08) |
| `MatrixCellInput` | Single cell: number / discrete scale / binary | Used by both editors |
| Matrix presets (props, not forks) | | |
| → ranking performance | via `RectangularMatrixEditor` | dims `m×n`, empty invalid |
| → AHP pairwise | via `SquareMatrixEditor` | scale 1–9; auto-fill reciprocal; diagonal `1` |
| → DEMATEL direct effect | via `SquareMatrixEditor` | scale 0–4; `0` valid; empty invalid |
| → ISM binary | via `SquareMatrixEditor` | `0`/`1` toggle; self-reach handled in engine |

### C. Shared result presentations (create once)

| New component | Used by | Notes |
| --- | --- | --- |
| `RankingResultTable` | SAW, TOPSIS | Columns: name, score, rank (+ optional distance columns via `extraColumns`) |
| `CriteriaWeightTable` | AHP (+ optional paste target for manual transfer) | Weights + optional CR badge |
| `CriteriaMetricsTable` | DEMATEL | prominence, relation (D/R if useful) |
| `HierarchyLayerBoard` | ISM | Layers top→bottom; no fake weights |
| `MethodComparisonNote` | When both SAW & TOPSIS ran | Explains independence; **no** combined rank |

### D. Method panels (thin wrappers only)

Each panel owns **layout + wiring**, not a private matrix/table implementation.

| New component | Doc | Composes |
| --- | --- | --- |
| `SawMethodPanel` | 03 | Shared ranking inputs + `RankingResultTable` + SAW run |
| `TopsisMethodPanel` | 04 | Same inputs + TOPSIS extras in result |
| `AhpMethodPanel` | 05 | `SquareMatrixEditor` (pairwise) + CR `Alert` + `CriteriaWeightTable` |
| `DematelMethodPanel` | 06 | Intensity matrix + `CriteriaMetricsTable` |
| `IsmMethodPanel` | 07 | Binary matrix + `HierarchyLayerBoard` |
| `ManualWeightTransferAction` | 01 / AC04 | Explicit “copy weights into ranking inputs” — never auto |

### E. Backend modules (not React, but required for clean architecture)

| New module | Responsibility | Keep pure |
| --- | --- | --- |
| `services/validators.py` | Shared rules from doc 02 | No HTTP |
| `services/saw_service.py` | SAW formulas (doc 03) | No HTTP |
| `services/topsis_service.py` | TOPSIS formulas (doc 04) | No HTTP |
| `services/ahp_service.py` | Geometric mean weights + CR (doc 05; CR details after open items) | No HTTP |
| `services/dematel_service.py` | T, prominence, relation (doc 06) | No HTTP |
| `services/ism_service.py` | Reachability + layering (doc 07) | No HTTP |
| `services/execution_service.py` | Snapshot + persist run (doc 08) | Orchestration only |
| Models e.g. `DecisionCase`, `DecisionRun` | Case + immutable run payload | No update-in-place of past runs |
| Thin `views` / serializers | AuthZ + DTO | Delegate to services |

Reference port: start SAW/TOPSIS from [09-ranking-reference.md](./decision-support/09-ranking-reference.md); split the sample’s combined `rank_options` into **independent** callables so AC01 holds.

---

## Suggested composition (no duplication)

```text
ProjectDecisionSupportPage
├── PageHeader
├── DecisionCaseHeader
├── MethodPicker
├── NamedListEditor (criteria)
├── NamedListEditor (alternatives)     # hidden for AHP/DEMATEL/ISM-only
├── WeightVectorEditor + CriterionTypeToggle   # ranking methods
├── DecisionCaseWorkspace
│   ├── SawMethodPanel ── RectangularMatrixEditor + RunActionBar + RankingResultTable
│   ├── TopsisMethodPanel ── (same editors) + RankingResultTable
│   ├── AhpMethodPanel ── SquareMatrixEditor + CriteriaWeightTable
│   ├── DematelMethodPanel ── SquareMatrixEditor + CriteriaMetricsTable
│   └── IsmMethodPanel ── SquareMatrixEditor + HierarchyLayerBoard
├── ManualWeightTransferAction
├── ExecutionHistoryList
└── InputSnapshotViewer / ValidationIssueList
```

---

## Explicit non-goals / anti-patterns

| Avoid | Why |
| --- | --- |
| Five route files each with its own matrix table markup | Diverges validation and a11y |
| Reusing `project-decisions-workflow` as the MCDM UI | Different domain (management rationale vs MCDM engines) |
| Auto-feeding AHP/DEMATEL weights into SAW/TOPSIS | Violates 01 scope and AC04 |
| Treating empty matrix cells as `0` | Violates 02 / AC08 (except where `0` is an explicit judgment) |
| Fabricating inactive zeros on dashboards for missing engines | Same spirit as FR-RPT inactive figures — show unavailable/inactive |
| Putting NumPy-heavy logic in React | Engines stay on API (or shared pure TS only if dual-run is required; prefer one SoR) |
| New chart library solely for ISM layers | Start with `HierarchyLayerBoard`; add graph viz only if UX demands |

---

## Implementation checklist (for `/speckit-*` or tickets)

- [ ] Add `components/decision-support/` shared shell (A + B + C) before method panels (D)
- [ ] Add API app + pure engines (E); pytest AC14–AC22 first (TDD-friendly)
- [ ] Wire one project route + `decision-support.ts` client + nav + `en.json` / `fa.json`
- [ ] History/snapshots for AC23–AC24 before polish charts
- [ ] Keep open items from [11-source-review.md](./decision-support/11-source-review.md) out of hard-coded engine claims until decided

---

## Maintenance

When a new UI need appears, update this file **before** adding a sibling component: either extend an existing row (shared) or justify a new method-specific panel. Prefer props/configuration on `SquareMatrixEditor` / `RankingResultTable` over copy-paste.
