## 2025-02-20 - [Add Loading Spinners to Async Submit Buttons]
**Learning:** [Users need immediate visual feedback when submitting forms that trigger async actions, otherwise they may assume the action failed or click the button multiple times. Adding a loading spinner next to the submit text provides clear, accessible confirmation that their action is being processed.]
**Action:** [Always include a visual loading indicator (like `lucide-react`'s `Loader2` with an `animate-spin` class) inside submit buttons when they are in a disabled/submitting state during async operations.]

## 2024-07-04 - Localized Password Toggle Aria Labels
**Learning:** Hardcoded ARIA labels for icon-only buttons like the password visibility toggle reduce accessibility for non-English speakers (like Persian users in this app).
**Action:** Always use i18n translation functions (`t("common.showPassword")`) for `aria-label` and `title` attributes on interactive elements, ensuring screen readers announce actions correctly in the user's selected language.
