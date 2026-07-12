## 2024-07-12 - Breadcrumb Current Page Accessibility
**Learning:** In the `Breadcrumb` component (`apps/web/src/components/layout/page-header.tsx`), adding `aria-current="page"` to the last item improves screen-reader accessibility by explicitly marking the active page. Additionally, removing the `href` link for the last item prevents redundant and potentially confusing navigation.
**Action:** Always ensure breadcrumb patterns do not link the active page and use `aria-current="page"` to communicate state to assistive technologies.
