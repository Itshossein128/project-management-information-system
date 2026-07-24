# IPCAS Brand Color Guidelines

## Product

**IPCAS** — Integrated Project Control Automation System for civil/construction projects.

## Palette story

| Signal | Color | Why it fits |
|--------|-------|-------------|
| Structure | Steel slate | Concrete, rebar, engineering drawings, control-room chrome |
| Attention | Safety orange | Construction site PPE / hazard marking; rare CTAs & accents |
| On track | Operational green | Progress, approvals, cash inflow |
| Caution | Amber | Delays, pending review, budget near limit |
| Critical | Safety red | Overdue, overruns, risk flags, cash outflow |
| In progress | Steel blue | Informational / active work (not brand chrome) |

## Implementation

- Primitives: `apps/web/src/design/tokens/palette.css`
- Semantics + Tailwind: `apps/web/src/app/app.css`
- TS helpers: `apps/web/src/design/tokens/colors.ts`, `chart-colors.ts`
- Master UX rules: `design-system/ipcas/MASTER.md`

## Do / Don't

**Do** use `bg-brand-*`, `bg-safety-*`, `bg-success-*`, `bg-warning-*`, `bg-danger-*`, `bg-info-*`, `bg-neutral-*`, and semantic tokens (`primary`, `destructive`, `muted`, …).

**Don't** introduce raw `emerald-*` / `blue-*` / `#hex` in components or Recharts series.
