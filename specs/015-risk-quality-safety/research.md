# Research: Risk, Quality & Safety

**Date**: 2026-10-09

## Findings

### Existing coverage (keep)

- `risk.RiskEvent`: project-scoped soft-delete event with `event_type` ∈ {delay, barrier, risk, claim, change_order}, probability (decimal), severity enum (low→critical), barrier-style status (open / in_progress / resolved), owner, corrective_action, activity FK, impact_on_schedule/cost booleans, barrier category, claim-related daily report / correspondence links.
- Barriers filtered ViewSet (`event_type=barrier`) + general risk-events CRUD + probability×severity **matrix** for open events.
- Web: `project-risk-register.tsx` + `lib/api/risk-events.ts`; nav capability `risk`.
- Daily-report `DailyReportIncident` (quality/safety/other notes on a report day) — field capture only; not a project HSE register.
- Permissions in use: `view_reports` / `edit_reports` on risk ViewSets.

### Gaps to close

1. No first-class **issue** type; realized problems mix with uncertain risks / barriers.
2. Missing FR risk fields: cause, consequence, response strategy, numeric composite score, due-date semantics aligned with FR, impact dimensions beyond schedule/cost (quality, safety, contract, liquidity).
3. Status vocabulary is barrier-centric (`open` / `in_progress` / `resolved`), not FR set (`open`, `under_review`, `mitigated`, `closed`, `residual`).
4. No optional links to cost item, contract, or related decision.
5. No inspection / NCR / corrective action / work permit / training / project-level incident & near-miss entities.
6. No project + period quality/safety report.

## Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Bounded context | Extend **`risk` app** with quality/HSE models | Principle V; FR-RSK is one implementation spec; avoids a second parallel app |
| Risk vs issue | Same table `RiskEvent`, hard discriminator `event_type` ∈ {`risk`, `issue`, …}; issue list/API filters exclude risk and vice versa | Spec allows “clearly separated record types”; preserves UUID history and barrier/claim paths |
| Barrier / delay / claim | Remain on `RiskEvent`; not redesign in this feature; barrier ViewSet unchanged except shared field/status migrations where needed | Minimal coherent change; FR-RSK focus is risk/issue + quality/HSE |
| Status vocabulary | Introduce FR `RiskStatus` choices; **data-migrate**: `open`→`open`, `in_progress`→`under_review`, `resolved`→`closed`; barriers may keep presenting “resolved” label via i18n on `closed` or retain barrier-specific display mapping in Barrier serializer | Align FR-RSK-003 without breaking open rows |
| Probability / severity scale | Add `probability_level` (1–5, nullable) and `impact_severity_level` (1–5, nullable); composite = product when both set; keep legacy `probability` decimal and `severity` enum for matrix backward compat; sync helpers map level→bucket/enum when possible | Spec assumption; FR-010 no fabricated score |
| Composite score storage | Persist `composite_score` as nullable PositiveSmallInteger (1–25); recompute on save in service/serializer; never invent when either level missing; default status to `under_review` when score inputs incomplete unless client sets another allowed status | FR-002, FR-010, edge case |
| Impact dimensions | Boolean (or M2M flags) for schedule, cost, quality, safety, contract, liquidity; list filter `?impact=quality` etc. | FR-008; extend existing schedule/cost flags |
| Cost / contract links | Optional FK `cost_item` → `cost_control.CostBreakdownNode` (or Budget line if node missing—prefer CBS node); optional FK `contract` → contracts model; validate same project | FR-004 |
| Decision link | Optional `related_decision_ref` CharField/UUID + optional note; no FK until workflow (15) | Spec assumption |
| Close with open actions | If `corrective_action`/action rows still open and status→`closed`, require `acknowledge_open_actions=true` query/body flag; else 400 with warning code | FR-009 warn+acknowledge |
| Actions model | v1: keep text `corrective_action` + due date on risk; add lightweight `RiskAction` child rows (description, due_date, status open/done, owner) for warn-on-close; quality side uses `CorrectiveAction` linked to NCR | Supports FR action tracking without workflow engine |
| Inspection | New `Inspection` model: project, wbs (required), responsible_user (required), date (required), stage (plan/request/result), result, notes | FR-005, FR-006, SC-004 |
| NCR / CA | `Nonconformity` FK inspection (nullable for ad-hoc later—v1 prefer linked); `CorrectiveAction` FK nonconformity with due_date + responsible | FR-005 |
| Incident / near miss | `HseEvent` with `kind` ∈ {incident, near_miss}; project required; wbs optional; date required | FR-005, edge case |
| Permit / training | `WorkPermit`, `SafetyTraining` with project + date (+ responsible when applicable); included in period report | P3 sequencing, still in scope |
| Period report | Computed read `GET .../quality-safety/report/?date_from=&date_to=`; sections per entity; empty sections = empty arrays, not fake zero KPIs | FR-007, SC-003, edge case |
| Daily-report incidents | Out of scope to migrate; optional future link; period report does **not** auto-merge daily-report rows in v1 | Spec assumption |
| Permissions | Reuse `view_reports` / `edit_reports` for v1; do not add new permission codes unless product later splits HSE roles | Minimal; matches current risk module |
| Matrix | Continue for `event_type=risk` with open-like statuses (`open`, `under_review`, `mitigated`, `residual`); prefer level-based axes when levels present, else legacy probability buckets | Preserve dashboard value |
| UI surfaces | Extend risk-register for risk/issue; new project route for Quality & HSE + period report | Matches user stories |

## Alternatives considered

- **New `quality` Django app** — clearer long-term split; rejected for v1 (Principle V; one FR-RSK delivery).
- **Separate `ProjectRisk` / `ProjectIssue` tables with data copy** — cleaner domain; higher migration cost and dual APIs; rejected in favor of discriminator on `RiskEvent`.
- **Hard-block close when actions open** — stricter than spec default; rejected for warn+acknowledge.
- **Fold quality into daily reports only** — fails FR project/period register and inspection WBS rules.
- **Compute composite only in API response, never store** — possible; rejected for filter/sort convenience and matrix stability (store derived, recompute on write).
- **Require WBS on incidents** — rejected by FR edge case (project required, WBS recommended).

## NEEDS CLARIFICATION

None remaining — Technical Context unknowns resolved above.
