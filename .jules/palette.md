## 2026-07-16 - Explicit Focus States for Keyboard Parity
**Learning:** Raw HTML buttons (like the NotificationBell) and custom components (like segmented-control) in this app often lack the global focus-visible outlines that standard design system components receive. This creates keyboard accessibility dead zones.
**Action:** Always manually apply the global focus ring utilities (`outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]`) to custom interactive elements to ensure visual parity for keyboard users.
## 2026-07-18 - Improve RiskBadge visual affordance and tooltip formatting

Replaced the native browser title tooltip with Shadcn UI's Tooltip component for better control over styling and accessibility. Added an `AlertTriangle` warning icon next to the "در خطر" text to improve visual affordance. Formatted the tooltip content as an unordered list instead of raw newline-separated text to make multiple risk reasons easier to read.

## 2026-07-25 - Improve horizontal scrollbar in Shadcn Table container
In `apps/web/src/components/ui/table.tsx`, added `[&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]` to the `overflow-x-auto` wrapper. This cleanly hides the scrollbar on mobile and web viewports to improve the UX on wide tables.

## 2026-07-25 - Replace native title attributes on LanguageSwitcher toggle items with Shadcn Tooltips
**Learning:** Native `title` tooltips on interactive controls like `ToggleGroupItem` suffer from inconsistent delayed display and lack styled branding and screen-reader parity across different OS/browsers.
**Action:** Wrap `ToggleGroupItem` interactive elements with Radix/Shadcn `Tooltip` and `TooltipTrigger asChild` components to provide consistent visual affordances and accessibility.
