## 2025-02-20 - [Add Loading Spinners to Async Submit Buttons]
**Learning:** [Users need immediate visual feedback when submitting forms that trigger async actions, otherwise they may assume the action failed or click the button multiple times. Adding a loading spinner next to the submit text provides clear, accessible confirmation that their action is being processed.]
**Action:** [Always include a visual loading indicator (like `lucide-react`'s `Loader2` with an `animate-spin` class) inside submit buttons when they are in a disabled/submitting state during async operations.]

## 2025-02-21 - [I18n for ARIA Labels]
**Learning:** [Hardcoding strings in `aria-label` attributes breaks accessibility for users not using that specific language, as screen readers will attempt to read the language poorly. It's crucial to use internationalization functions like `t()` for ARIA labels just as you would for visible text.]
**Action:** [Always verify that any `aria-label` or `aria-description` strings are routed through `react-i18next`'s `t()` function, rather than being hardcoded in components.]
