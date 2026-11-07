## 2026-07-16 - Explicit Focus States for Keyboard Parity
**Learning:** Raw HTML buttons (like the NotificationBell) and custom components (like segmented-control) in this app often lack the global focus-visible outlines that standard design system components receive. This creates keyboard accessibility dead zones.
**Action:** Always manually apply the global focus ring utilities (`outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]`) to custom interactive elements to ensure visual parity for keyboard users.
## 2026-07-18 - Improve RiskBadge visual affordance and tooltip formatting

Replaced the native browser title tooltip with Shadcn UI's Tooltip component for better control over styling and accessibility. Added an `AlertTriangle` warning icon next to the "در خطر" text to improve visual affordance. Formatted the tooltip content as an unordered list instead of raw newline-separated text to make multiple risk reasons easier to read.

## 2026-07-25 - Improve horizontal scrollbar in Shadcn Table container
In `apps/web/src/components/ui/table.tsx`, added `[&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]` to the `overflow-x-auto` wrapper. This cleanly hides the scrollbar on mobile and web viewports to improve the UX on wide tables.

## 2026-07-28 - Logical Directional Classes for Form Middleware Elements
**Learning:** Inputs with forced `dir="ltr"` inside an RTL application layout (e.g. `PasswordInput`) will cause action buttons positioned with physical classes (`right-1`, `pr-10`) to overlap or misalign in RTL viewports.
**Action:** Use logical direction utilities (`end-1`, `pe-10`) so inner form elements align consistently across document text directions and language contexts.

## 2026-07-29 - Explicit Form Labels and Keyboard Focus Rings in Drawer Forms
**Learning:** Drawer form inputs relying solely on placeholders without explicit `<label>` tags and focus-visible rings degrade screen-reader usability and keyboard navigation clarity.
**Action:** Always wrap drawer form inputs with explicit `<label htmlFor="...">` elements and include `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring` classes for accessible focus management.
