# Design System Master File

> **LOGIC:** When building a specific page, first check `design-system/pages/[page-name].md`.
> If that file exists, its rules **override** this Master file.
> If not, strictly follow the rules below.

---

**Project:** IPCAS (Integrated Project Control Automation System)
**Generated:** 2026-07-23
**Category:** Construction / project-control enterprise dashboard
**Design Dials:** Variance 4/10 (Balanced) | Motion 3/10 (Subtle) | Density 8/10 (Dense)

---

## Global Rules

### Color concept

IPCAS is a **civil/construction project-control** platform. Colors must feel like
steel structure, site safety, and operational status — not generic SaaS purple/blue.

| Role | Meaning | Token | Approx hex |
|------|---------|-------|------------|
| Brand / Primary | Steel slate — structure, authority | `--palette-brand-600` | `#334155` |
| Accent / CTA highlight | Safety orange — site signal | `--palette-accent-600` | `#EA580C` |
| Success | On-track / approved / inflow | `--palette-success-600` | `#059669` |
| Warning | At-risk / caution / pending | `--palette-warning-600` | `#D97706` |
| Danger | Critical / overdue / outflow | `--palette-danger-600` | `#DC2626` |
| Info | In-progress / informational | `--palette-info-600` | steel blue |
| Neutrals | Cool concrete surfaces | `--palette-neutral-*` | slate-tinted |

**Source of truth:** `apps/web/src/design/tokens/palette.css`  
**Semantic mapping:** `apps/web/src/app/app.css`  
**Charts:** `chartColor()` / `chartPalette()` from `@/design/tokens`

### Usage rules

1. Prefer semantic Tailwind utilities: `bg-primary`, `text-success-700`, `bg-danger-50`, `border-warning-300`.
2. Prefer palette scales for soft status chips: `bg-success-100 text-success-800`.
3. Never hardcode Tailwind default hues (`emerald-*`, `blue-*`, `red-*`, `#hex`) in UI or charts.
4. Charts must resolve colors via `chartColor("success" | "danger" | …)` or `var(--chart-N)`.
5. Avoid purple, neon glow, and off-palette decorative gradients.

### Typography

- Persian: Vazirmatn (`--font-persian`)
- Latin: Inter (`--font-latin`)
- Keep existing app fonts (do not switch to Fira for product UI)

### Spacing (dense dashboard)

| Token | Value |
|-------|-------|
| `--space-xs` | `2px` |
| `--space-sm` | `4px` |
| `--space-md` | `8px` |
| `--space-lg` | `12px` |
| `--space-xl` | `16px` |
| `--space-2xl` | `24px` |
| `--space-3xl` | `32px` |

### Style

- Soft UI Evolution: subtle depth, clear contrast, WCAG AA
- Motion: 150–300ms, subtle route/hover only
- Density: compact tables and KPI grids

### Avoid

- AI purple/pink gradients
- Hardcoded Tailwind palette colors outside the design tokens
- Emoji as icons
- Inset marketing-card heroes on product chrome
