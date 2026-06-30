## 2024-03-24 - Translate aria-labels
**Learning:** Hardcoded strings in `aria-label` attributes on icon-only buttons will be read by screen readers in the wrong language if the application's locale changes. This creates a confusing experience for internationalized applications.
**Action:** Always use i18n translation functions (like `t()` from `react-i18next`) for `aria-label` and `aria-description` attributes, just like visible text.
