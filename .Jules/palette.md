## 2025-02-20 - [Add Loading Spinners to Async Submit Buttons]
**Learning:** [Users need immediate visual feedback when submitting forms that trigger async actions, otherwise they may assume the action failed or click the button multiple times. Adding a loading spinner next to the submit text provides clear, accessible confirmation that their action is being processed.]
**Action:** [Always include a visual loading indicator (like `lucide-react`'s `Loader2` with an `animate-spin` class) inside submit buttons when they are in a disabled/submitting state during async operations.]
## 2023-11-20 - Localized ARIA Labels for Screen Readers
**Learning:** Hardcoded english aria-labels on icon-only buttons severely degrade the experience for users on non-English locales (e.g. Persian screen readers).
**Action:** Always check `aria-label`s on icon-only buttons (like password toggles) to ensure they use `react-i18next` translations when localization is implemented.
