# Contract: Daily Report Summary UI

**Feature**: `028-auto-daily-report-summary`

## 1. Project daily reports list (`/projects/:projectId/daily-reports`)

| Requirement | Behavior |
|-------------|----------|
| Create control | **Must not** show «گزارش جدید», Plus, or link to `/daily-reports/new` |
| Open day | Date filter + row click / «مشاهده» opens summary for that date (ensure-by-date then view) |
| Empty project | Empty state explains that summaries appear after specialty reports (or invite to open a date / go to رشته reports)—**not** a create-blank CTA |
| Offline blank create | Do not offer offline “new project daily” from this page |

## 2. Open by date

Provide a date control (Jalali) “نمایش گزارش روز” that calls ensure-by-date and navigates to the summary **view** route (preferred over edit form).

If no specialty data: show the Excel-like shell with empty sections + banner «هنوز گزارش واحد تخصصی برای این روز ثبت نشده است».

## 3. Summary view layout (Excel sectional parity)

Single scrollable (or tabbed) day view with sections labeled to match the reference workbook:

1. Header — title گزارش روزانه, date, weekday, project name, contract number  
2. Work hours / shifts  
3. Site status (فعال / غیرفعال)  
4. Weather  
5. Indirect (ستادی) labor — job title, present, leave  
6. Direct labor — job title, present, leave + totals  
7. Incoming materials  
8. Concrete poured  
9. Executed site activities — description, shift, contractor, headcount, zone/block/floor, qty, unit, notes  
10. General site activities  
11. Issues / remarks  
12. Visits  
13. Confirmations / approval bar (reuse existing approval UI where possible)  
14. Management opinion (editable when permitted)

Derived tables are **read-only**. Show discipline badge/attribution on rows when useful.

**Partial banner**: when `aggregation.is_partial`, show missing disciplines (localized labels).

## 4. Retire blank create / free-form edit of derived data

| Route / UI | Change |
|------------|--------|
| `/daily-reports/new` | Remove from nav; redirect to list or by-date |
| Edit form tabs that mutate derived children | Hide or read-only for auto-summary reports; link to رشته entry |
| Approval / management opinion | Remain on summary view |

## 5. Specialty entry (`/projects/:projectId/sub-reports` and related)

Unchanged responsibility: **create/submit** specialty daily reports here (and extended contribution sections). Success toast may note that the project daily summary will update.

## 6. Localization

- Section titles, banners, read-only hints, and errors in **fa** and **en**
- Discipline codes mapped to labels (ابنیه / برق / مکانیک / …)
- Dates via existing Jalali display helpers

## 7. Accessibility

- Banner not color-only (text + role/status)
- Tables keyboard-scrollable; approval controls remain operable
- No reliance on removed create button for primary task completion
