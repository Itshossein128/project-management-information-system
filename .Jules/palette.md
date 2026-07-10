## 2025-02-13 - [Hardcoded ARIA Labels in Notifications]
**Learning:** Found a hardcoded Persian string (`aria-label="اعلان‌ها"`) on the NotificationBell component. This breaks screen reader accessibility when a user switches the application to English, as the screen reader will still read the Persian text.
**Action:** Always use the `react-i18next` `t()` function for `aria-label`, `aria-description`, and `title` attributes on icon-only buttons to ensure proper localization for screen reader users. Also ensure `aria-expanded` and `aria-haspopup` are used for interactive toggles.
