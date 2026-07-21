## 2025-02-20 - [Add Loading Spinners to Async Submit Buttons]
**Learning:** [Users need immediate visual feedback when submitting forms that trigger async actions, otherwise they may assume the action failed or click the button multiple times. Adding a loading spinner next to the submit text provides clear, accessible confirmation that their action is being processed.]
**Action:** [Always include a visual loading indicator (like `lucide-react`'s `Loader2` with an `animate-spin` class) inside submit buttons when they are in a disabled/submitting state during async operations.]

## 2025-02-21 - [I18n for ARIA Labels]
**Learning:** [Hardcoding strings in `aria-label` attributes breaks accessibility for users not using that specific language, as screen readers will attempt to read the language poorly. It's crucial to use internationalization functions like `t()` for ARIA labels just as you would for visible text.]
**Action:** [Always verify that any `aria-label` or `aria-description` strings are routed through `react-i18next`'s `t()` function, rather than being hardcoded in components.]

## 2024-07-04 - Localized Password Toggle Aria Labels
**Learning:** Hardcoded ARIA labels for icon-only buttons like the password visibility toggle reduce accessibility for non-English speakers (like Persian users in this app).
**Action:** Always use i18n translation functions (`t("common.showPassword")`) for `aria-label` and `title` attributes on interactive elements, ensuring screen readers announce actions correctly in the user's selected language.
## 2024-07-06 - Component Localization

**Learning:** When adding ARIA labels or updating UI strings in icon-only buttons, it's a good practice to localize the new strings at the same time if the project uses i18n, to ensure the UI is consistent across languages.

**Action:** When updating existing strings to include translation wrappers, always update all localized string resources (`en.json`, `fa.json`) to maintain parity.

## 2026-07-07 - Accessible Overlay Components
**Learning:** Custom overlay components like Drawers require specific ARIA attributes (`role="dialog"`, `aria-modal="true"`, and `aria-labelledby`) to be correctly identified and read by screen readers. Furthermore, decorative icons within buttons that already have an `aria-label` should be explicitly hidden from screen readers using `aria-hidden`.
**Action:** Always ensure custom overlays have `role="dialog"` and `aria-modal="true"`, map their titles using `aria-labelledby`, and add `aria-hidden` to redundant icons inside accessible buttons.
## 2026-07-09 - Added aria-labels to icon-only buttons in EditableGrid\n**Learning:** Icon-only buttons (like Save and Delete actions in grids) often miss accessibility attributes, making them difficult for screen reader users to identify.\n**Action:** Add `aria-label` alongside `title` on icon-only interactive elements to ensure both visual hover states and screen reader announcements are informative.

## 2024-07-12 - Breadcrumb Current Page Accessibility
**Learning:** In the `Breadcrumb` component (`apps/web/src/components/layout/page-header.tsx`), adding `aria-current="page"` to the last item improves screen-reader accessibility by explicitly marking the active page. Additionally, removing the `href` link for the last item prevents redundant and potentially confusing navigation.
**Action:** Always ensure breadcrumb patterns do not link the active page and use `aria-current="page"` to communicate state to assistive technologies.
## 2025-02-21 - [Added Loading States with aria-busy for Async Form Actions]
**Learning:** [Users need immediate visual feedback when submitting forms that trigger async actions, otherwise they may assume the action failed or click the button multiple times. Adding a loading spinner next to the submit text provides clear confirmation. Similarly, using the `aria-busy` attribute correctly announces this temporary transition state to screen readers.]
**Action:** [Always include a visual loading indicator (like `lucide-react`'s `Loader2` with an `animate-spin` class) inside submit buttons when they are in a busy state. Also, always add `aria-busy={busy}` for screen reader compatibility, and utilize flexbox layouts (`inline-flex items-center gap-2`) to keep text and spinner properly aligned.]
## 2024-07-19 - Password Input UX Improvement
Improved the `PasswordInput` component UX by:
1. Adding right padding (`pr-10`) to the input field so that long passwords don't overflow and hide beneath the visibility toggle icon.
2. Adding `onPointerDown={(e) => e.preventDefault()}` to the toggle button to prevent the input field from losing focus when the user toggles password visibility. This allows the user to seamlessly continue typing after clicking the toggle.
## 2026-07-21 - Added aria-busy and aria-hidden to loading buttons
**Learning:** For components that manage a loading state with an internal spinner, applying `aria-busy` to the root element accurately conveys the component's state to screen readers. In tandem, setting `aria-hidden="true"` on the internal spinner prevents redundant or confusing announcements.
**Action:** Always add `aria-busy` on the container and `aria-hidden` on the visual loading indicators (like `Loader2`) inside interactive elements that have a loading state.
