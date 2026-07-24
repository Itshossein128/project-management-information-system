# Data Test IDs

## Auth / Login
- `login-phone-input`
- `login-password-input`
- `login-submit-btn`
- `login-global-error`
- `login-error`: For displaying login error messages (apps/web/src/app/routes/login.tsx).

## Projects
- `create-project-btn`
- `project-code-input`
- `project-name-input`
- `project-employer-input`
- `project-submit-btn`
- `project-card`

## WBS / Schedule (Sprint 3)
- `wbs-node-{code}` — tree node wrapper (`data-wbs-id`)
- `wbs-row-{code}` — draggable row
- `msp-import-btn` — open MSP/P6 import wizard

## Daily Reports (Sprint 4)
- `daily-reports-list` — list page shell
- `daily-report-new-btn` — create report CTA
- `daily-report-row-{id}` — list row
- `daily-report-edit-{id}` — edit link
- `daily-report-form` — create/edit form shell
- `daily-report-save-header` — save/create header button
- `report-tab-{activities|labor|equipment|materials|concrete|labor_camp|incidents}`
- `grid-add-row-btn` — add child row in editable grids
- `approval-status-bar` — workflow action bar
- `report-status-badge` — current status
- `report-submit-btn` / `report-review-btn` / `report-approve-btn` / `report-reject-btn`
- `report-reject-reason` / `report-reject-confirm-btn`
- `photo-cell` / `photo-upload-input` / `photo-preview-link`

## Physical Progress & S-Curve (Sprint 6)
- `progress-kpi-grid` — KPI grid section
- `progress-s-curve` — S-Curve chart section
- `progress-manual-btn` — Button to enter progress manually
- `progress-behind-checkbox` — Checkbox to filter behind-schedule activities

## Budget & Cost (Sprint 7)
- `costs-kpi-grid` / `costs-tabs` / `costs-tab-{budget|actual|variance|pools}`
- `budget-grid` / `budget-matrix` / `budget-cell-{code}-{category}` / `budget-input-{code}-{category}` / `budget-save-btn`
- `actual-costs-tab` / `actual-cost-add-btn` / `actual-cost-drawer` / `actual-cost-category` / `actual-cost-amount` / `actual-cost-wbs` / `actual-cost-save-btn`
- `variance-tab` / `variance-group-{wbs|category|activity}`
- `cost-pool-tab` / `cost-pool-new-btn` / `cost-pool-create-form` / `cost-pool-name-input` / `cost-pool-category` / `cost-pool-amount-input` / `cost-pool-create-btn`
- `cost-pool-table` / `cost-pool-row-{id}` / `cost-pool-allocate-btn-{id}`
- `cost-pool-allocation-wizard` / `cost-pool-auto-method` / `cost-pool-auto-allocate` / `cost-pool-allocate-activity` / `cost-pool-allocate-amount` / `cost-pool-allocate-confirm`

## Offline Sync (Sprint 5)
- `offline-indicator` — shell connectivity / pending / conflict badge
- `daily-reports-sync-now` — list page manual sync CTA
- `conflict-card-{n}` / `conflict-option-server|local|merge` / `conflict-apply-btn`
- `conflict-merge-editor` / `conflict-merge-save-btn` / `conflict-merge-cancel-btn`

