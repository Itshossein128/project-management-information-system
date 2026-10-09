# Feature Specification: Earned Value & Project Control (EVM)

**Feature Branch**: `014-earned-value-control`

**Created**: 2026-10-09

**Status**: Draft

**Input**: User description: Implementation Spec `13-ارزش کسب‌شده و کنترل پروژه.md` (FR-EVM) — compute and report PV, EV, AC and variance/performance indices and finish forecasts at project, phase, and cost-center (CBS) levels with transparent handling of incomplete data.

**Source**: [13-ارزش کسب‌شده و کنترل پروژه.md](../../docs/طرح%20اولیه%20و%20نیازمندی‌های%20سیستم%20(System%20Requirements)/راهنمای%20پیاده‌سازی%20Velora%20(Velora%20Implementation%20Specs)/13-ارزش%20کسب‌شده%20و%20کنترل%20پروژه.md) (`FR-EVM`)  
**Depends on**: [002-core-domain-principles](../002-core-domain-principles/spec.md), [005-schedule-baseline](../005-schedule-baseline/spec.md), [009-progress-periodic-reports](../009-progress-periodic-reports/spec.md), [010-multi-level-budget](../010-multi-level-budget/spec.md), [012-cost-commitment-payment](../012-cost-commitment-payment/spec.md)

## Gap Analysis (current vs FR-EVM)

Project-level EVM KPIs already exist (planned/actual progress × budget for PV/EV, actual cost for AC, SPI/CPI/EAC/ETC/VAC with null indices when divisor is zero, progress UI cards, and economic inflation-adjusted forecast on top). This feature closes **only unmet** FR-EVM portions: multi-level reporting, baseline-lock gate, incomplete-data transparency (not misleading zeros), and EV tied to the approved measurement method—not to actual cost or invoice amounts.

| FR / SC | Intent | Current state | Gap (this feature) |
|---------|--------|---------------|--------------------|
| FR-EVM-001 | Schedule + budget baselines defined and locked for valid calculations | Schedule baseline lock exists; EVM does not require or warn on unlocked baseline | Gate or warn when schedule/budget baseline is unlocked |
| FR-EVM-002 | PV, EV, AC at report cut-off with source definitions | Project-level PV/EV/AC computed | Align definitions; ensure EV uses approved measurement method feed |
| FR-EVM-003 | SV, CV, SPI, CPI, EAC, ETC, VAC via common method | Present at project level; CPI/SPI null when AC/PV zero | Keep common method; surface “not computable” consistently in reports |
| FR-EVM-004 | Reportable and rollable at project, phase, and cost center (CBS) | Project (and global KPI) only | Phase and CBS slices + roll-up to project |
| FR-EVM-005 | When EV or AC is zero/absent, CPI/SPI show “not computable” | Backend returns null; UI often shows “—” / cost footer | Explicit not-computable labeling for dependent indices/forecasts |
| FR-EVM-006 | Missing or incomplete data is transparent in the report | Partial (cost missing footer); EV can look like zero progress | Distinguish unregistered / incomplete from numeric zero |
| FR-EVM-007 | EV from approved measurement method; not assumed equal to AC or IPC amount | EV ≈ BAC × progress %; not equated to AC | Enforce method-based EV; never substitute AC/invoice for EV |
| SC-EVM-001 | Correct PV/EV/AC/indices/forecasts at project/phase/CBS | Project only | Multi-level correctness |
| SC-EVM-002 | 100% insufficient-data cases → dependent index not computable | Partial null handling | Full transparency policy |
| SC-EVM-003 | Measurement-method change without version/approval must not create uncontrolled artificial variance | Depends on progress (08) versioning | Consume only approved/versioned method outputs |

**In scope**: PV/EV/AC definitions; CPI/SPI; EAC/ETC/VAC; “not computable” rules; multi-level reportability; incomplete-data transparency; baseline-lock warning/gate for validity.

**Out of scope**: Raw progress and budget capture (08, 09); quality/risk (14); redesign of inflation Monte Carlo / economic engine beyond consuming standard EVM outputs; company treasury systems.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View EVM indices at cut-off (Priority: P1)

As a project controller, with locked schedule and budget baselines, I open the EVM report for a cut-off date and see PV (budgeted work planned), EV (budgeted work performed per the approved measurement method), AC (recorded actual cost), and variances so I can report schedule and cost performance.

**Why this priority**: Core control loop; without correct PV/EV/AC and variances, indices and forecasts are meaningless (FR-EVM-001–003, FR-EVM-007, SC-EVM-001).

**Independent Test**: Sample project with locked baselines, approved progress for the measurement method, and posted actual cost → open EVM at cut-off → PV, EV, AC, SV, CV match the source definitions and roll up correctly at project level.

**Acceptance Scenarios**:

1. **Given** locked schedule and budget baselines, **When** the EVM report opens for a cut-off, **Then** PV is the budgeted value of work planned, EV is the budgeted value of work performed per the approved measurement method, and AC is recorded actual cost to date.
2. **Given** EV or AC is zero or absent, **When** CPI or SPI is shown, **Then** the system displays “not computable” (or equivalent localized label), not a meaningless number.
3. **Given** data available at phase and cost-center (CBS) levels, **When** aggregation is requested, **Then** project-level figures are also reportable as the roll-up of those levels.
4. **Given** actual cost or an invoice amount exists, **When** EV is computed, **Then** EV is never silently set equal to AC or the invoice amount.

---

### User Story 2 - Transparent incomplete data (Priority: P1)

As a project controller, when progress, cost, or baseline data is missing or incomplete, the EVM report makes that explicit so I do not take a wrong control decision from a misleading zero.

**Why this priority**: Misleading zeros are explicitly called out as unacceptable in the source (FR-EVM-005–006, SC-EVM-002); same priority as core indices.

**Independent Test**: Project with locked baselines but no approved progress → EV section shows unregistered / not computable (not a silent zero that looks like “no earned value by design”). Project with unlocked baseline → warning that baseline is not locked.

**Acceptance Scenarios**:

1. **Given** a project with no approved progress for the measurement method, **When** the EVM report opens, **Then** EV is shown as unregistered or not computable, not as a misleading numeric zero.
2. **Given** an unlocked (open) schedule or budget baseline, **When** EVM calculation is requested, **Then** a clear warning “baseline is not locked” (localized) is shown and calculations are marked as not fully valid.
3. **Given** AC exists but EV is absent/zero in the not-computable sense, **When** CPI is requested, **Then** CPI is not computable; CV may still be reportable only when the product definition allows a defined EV and AC pair (otherwise CV is also not computable).
4. **Given** SPI or CPI is not computable, **When** EAC/ETC/VAC that depend on that index are shown, **Then** those forecasts are also not computable, not invented from fallback math.

---

### User Story 3 - Finish forecasts (Priority: P2)

As a project manager, I see EAC, ETC, and VAC using the common performance-based method when CPI is valid, so I can judge expected cost at completion versus budget.

**Why this priority**: Forecasts build on trusted indices; valuable once P1 transparency and multi-level bases exist (FR-EVM-003, SC-EVM-001).

**Independent Test**: With valid CPI, EAC/ETC/VAC appear consistently with the common method; with not-computable CPI, dependent forecasts are not computable.

**Acceptance Scenarios**:

1. **Given** valid BAC and CPI, **When** finish forecasts are requested, **Then** EAC, ETC, and VAC are shown using the common method (EAC from BAC and CPI; ETC and VAC derived from EAC, AC, and BAC).
2. **Given** CPI is not computable, **When** finish forecasts are requested, **Then** EAC, ETC, and VAC that depend on CPI are marked not computable.
3. **Given** the same cut-off and inputs, **When** project, phase, and CBS reports are opened, **Then** forecast figures at each level are consistent with that level’s BAC/CPI (and project equals roll-up rules defined for the organization).

---

### User Story 4 - Multi-level EVM reporting (Priority: P2)

As a project controller, I produce EVM figures at project, phase, and cost-center (CBS) levels and roll them up without exporting to a spreadsheet as the only path.

**Why this priority**: Source requires multi-level reportability (FR-EVM-004, SC-EVM-001); builds on correct per-slice PV/EV/AC.

**Independent Test**: Seeded phase and CBS budget/progress/cost → open phase and CBS EVM → project report matches agreed roll-up.

**Acceptance Scenarios**:

1. **Given** budget, approved progress, and actual cost attributed to phases and cost centers, **When** EVM is opened at each level, **Then** PV, EV, AC and available indices appear for that slice.
2. **Given** multi-level data, **When** project roll-up is requested, **Then** project totals are consistent with the defined aggregation of child slices (no silent double count).
3. **Given** multiple currencies on cost lines, **When** cross-currency aggregation is requested, **Then** aggregation occurs only with an explicit conversion; otherwise the report states that mixed-currency totals are not available.

---

### Edge Cases

- **AC present, EV absent/zero (not computable)**: CPI not computable; CV only if a defined EV exists under product rules—otherwise CV not computable.
- **PV zero or absent**: SPI not computable.
- **Unlocked baseline**: EVM report available with explicit “baseline is not locked” warning; figures marked not fully valid.
- **No approved progress**: EV unregistered / not computable—not a silent zero.
- **Measurement method changed without version/approval**: EVM continues to use the last approved/versioned method output; unapproved changes do not silently rewrite historical EV (SC-EVM-003).
- **Multi-currency**: No silent sum across currencies; only with explicit conversion.
- **Empty phase/CBS slice**: Slice shows incomplete/unregistered rather than fake perfect performance (SPI/CPI = 1.0 invented).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: For EVM figures to be considered fully valid, the project MUST have defined and locked schedule and budget baselines; if either is unlocked, the system MUST show a clear “baseline is not locked” warning and MUST NOT present the report as fully valid.
- **FR-002**: At a report cut-off (period or as-of date), the system MUST compute or present PV, EV, and AC using the source definitions: PV = budgeted value of work planned; EV = budgeted value of work performed per the approved measurement method; AC = recorded actual cost.
- **FR-003**: The system MUST present variances and indices including SV, CV, SPI, CPI, and finish forecasts EAC, ETC, VAC using the common performance-based method when inputs allow.
- **FR-004**: EVM numbers MUST be reportable at project, phase, and cost-center (CBS) levels and MUST support roll-up to project without silent double counting.
- **FR-005**: When EV or AC is zero or absent in a way that makes a ratio meaningless, CPI and/or SPI MUST be shown as “not computable” (localized), never as a fabricated numeric index.
- **FR-006**: Missing or incomplete inputs (progress, cost, baseline, conversion) MUST be transparent in the EVM report—unregistered / incomplete / not computable—rather than a misleading numeric zero that implies measured performance.
- **FR-007**: EV MUST be based on the approved measurement method from progress/periodic reporting and MUST NOT be assumed equal to actual cost or invoice (IPC) amounts.
- **FR-008**: When SPI or CPI is not computable, dependent forecasts (EAC, ETC, VAC that rely on that index) MUST also be not computable.
- **FR-009**: Changing the measurement method without the versioning/approval rules of progress reporting MUST NOT silently rewrite EVM history or create uncontrolled artificial variance; EVM MUST consume only approved/versioned progress outputs.
- **FR-010**: Multi-currency aggregation MUST require explicit conversion; without it, the system MUST refuse silent cross-currency totals and state that clearly.

### Key Entities

- **EVM Report Point**: A cut-off period or as-of date for which EVM is evaluated, scoped to project and optionally phase or cost center.
- **EVM Measures (PV / EV / AC)**: Budgeted planned work, budgeted performed work (method-based), and actual cost at the report point, with validity/completeness flags.
- **Performance Indices & Variances**: SV, CV, SPI, CPI—each either a defined value or explicitly not computable.
- **Finish Forecast**: EAC, ETC, VAC derived from the common method when CPI (and related inputs) are valid; otherwise not computable.
- **Baseline Validity State**: Whether schedule and budget baselines are locked for the cut-off used by the report.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a seeded project with locked baselines, approved progress, and actual cost, a project controller can open the EVM report at project level and see correct PV, EV, AC, SV, CV, and available SPI/CPI in under 2 minutes without a spreadsheet.
- **SC-002**: In 100% of test cases with insufficient data for a ratio (missing/zero EV or AC as defined), the dependent index is labeled not computable—never a misleading numeric value.
- **SC-003**: Controllers can produce EVM at project, phase, and cost-center (CBS) levels in the same product session, with project roll-up consistent with child slices under the defined aggregation rules.
- **SC-004**: In 100% of test cases with an unlocked required baseline, the report shows the baseline-not-locked warning and does not claim full validity.
- **SC-005**: In 100% of tested cases, EV is not equal to AC or an invoice amount solely because those amounts exist; EV follows the approved measurement method feed.
- **SC-006**: When the measurement method changes without approval/versioning, historical EVM at prior cut-offs does not jump from an uncontrolled rewrite of progress inputs (verified by regression scenarios tied to progress versioning).

## Assumptions

- “Common method” for finish forecast means the standard performance factor form: EAC = BAC / CPI when CPI is valid; ETC = EAC − AC; VAC = BAC − EAC (same family already used for project-level KPIs). Alternate EAC formulas (e.g., SPI×CPI composite) are out of scope for v1 unless planning adds them.
- Phase means the project’s established phase / high-level WBS grouping used elsewhere in schedule and budget; CBS means cost-center nodes from multi-level budget / cost control.
- Approved measurement method and progress feeds come from feature `009-progress-periodic-reports`; budget BAC and CBS structure from `010-multi-level-budget`; actual cost from `012-cost-commitment-payment`; schedule baseline lock from `005-schedule-baseline`.
- Existing project-level EVM KPI computation and progress/economic UI remain the starting point; this feature extends them for multi-level reporting, baseline validity, and incomplete-data semantics rather than inventing a parallel control product.
- Localized “not computable” / “unregistered” / “baseline is not locked” strings follow bilingual constitution rules (Persian and English).
- Project-scoped authorization follows server-enforced membership and permissions; EVM is readable by roles that already may view progress/cost KPIs (exact codenames left to planning).
- Inflation-adjusted EAC and Monte Carlo remain in the economic analysis surface; this feature guarantees the underlying standard EVM inputs and labels those surfaces can trust.
- Single-currency projects are the default path; multi-currency uses the organization’s existing explicit conversion policy when present, otherwise mixed totals are withheld (FR-010).
- This capability is primarily a later delivery phase in the implementation roadmap, except that a minimal correct PV/EV/AC report with not-computable rules may ship earlier if product prioritizes it.
