# رجیستر بندهای اصلی نیازمندی و معیار پذیرش

۳۷۰ بند از مشخصات منتخب A.1 و وابستگی‌هایش؛ این تعداد، نیازهای مستقل و هم‌وزن نیست. شناسه معتبر از ترکیب مسیر منبع و FR/SC تشکیل می‌شود. وضعیت پیاده‌سازی زیر، ارزیابی گروه مرتبط است؛ به معنی اثبات تک‌تک اجزای بند نیست. SCها بدون شواهد کامل فعلی پذیرفته علامت نخورده‌اند.


## specs/007-daily-report-gaps/spec.md

### FR-001 — H01

منبع: [specs/007-daily-report-gaps/spec.md:120](../../specs/007-daily-report-gaps/spec.md#L120) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-001**: A daily report MUST capture project, work front or site location (header-level), report date (Jalali in UI), shift, preparer, and weather condition.

### FR-002 — D04

منبع: [specs/007-daily-report-gaps/spec.md:121](../../specs/007-daily-report-gaps/spec.md#L121) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-002**: Activity rows MUST support linked schedule activity (hence WBS), description, quantity, unit, location, responsible person, and optional photo/attachment.

### FR-003 — D06

منبع: [specs/007-daily-report-gaps/spec.md:122](../../specs/007-daily-report-gaps/spec.md#L122) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-003**: Labor rows MUST record headcount by group/job title (or contractor grouping as available), work hours, and absence distinctly from headcount.

### FR-004 — D09

منبع: [specs/007-daily-report-gaps/spec.md:123](../../specs/007-daily-report-gaps/spec.md#L123) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-004**: Equipment rows MUST continue to record identity, productive hours, idle/stoppage hours, and idle reason.

### FR-005 — D12

منبع: [specs/007-daily-report-gaps/spec.md:124](../../specs/007-daily-report-gaps/spec.md#L124) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-005**: Material rows MUST support receipt, consumption, return, and waste, each with quantity and unit; consumption location MUST be capturable when relevant.

### FR-006 — D14

منبع: [specs/007-daily-report-gaps/spec.md:125](../../specs/007-daily-report-gaps/spec.md#L125) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-006**: Site events (incident, stoppage, site instruction, barrier) MUST support description, follow-up owner, and due date (plus existing type/corrective notes as applicable).

### FR-007 — W01

منبع: [specs/007-daily-report-gaps/spec.md:126](../../specs/007-daily-report-gaps/spec.md#L126) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-007**: Lifecycle MUST include draft, supervisor confirmation (submit/review), and lock by designated approver; locked means approved and immutable except via correction request.

### FR-008 — W02

منبع: [specs/007-daily-report-gaps/spec.md:127](../../specs/007-daily-report-gaps/spec.md#L127) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-008**: Amending a locked report MUST require a correction request with mandatory reason; the previous locked version MUST be retained; the new version MUST re-enter the approval path before becoming the current locked version.

### FR-009 — W06

منبع: [specs/007-daily-report-gaps/spec.md:128](../../specs/007-daily-report-gaps/spec.md#L128) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-009**: Report date, registration/created time, and approval/lock time MUST remain separate fields.

### FR-010 — D05

منبع: [specs/007-daily-report-gaps/spec.md:129](../../specs/007-daily-report-gaps/spec.md#L129) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: For required measured fields (at least activity quantity and material quantity), “not recorded” MUST be distinguishable from zero; submit validation MUST not treat blank as zero.

### FR-011 — Q03

منبع: [specs/007-daily-report-gaps/spec.md:130](../../specs/007-daily-report-gaps/spec.md#L130) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-011**: Users MUST be able to complete the report on mobile-width and desktop layouts with attachments supported.

### FR-012 — D12

منبع: [specs/007-daily-report-gaps/spec.md:131](../../specs/007-daily-report-gaps/spec.md#L131) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-012**: When a material consumption row is linked to project material/inventory data, the product MUST offer a reconciliation indication usable for SC-DR-002 (match / mismatch / insufficient data)—without requiring a full warehouse redesign.

### FR-013 — W03

منبع: [specs/007-daily-report-gaps/spec.md:132](../../specs/007-daily-report-gaps/spec.md#L132) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-013**: Direct edit of locked reports MUST be denied in all cases; only draft and rejected (unlocked) reports remain freely editable by authorized authors.

### SC-001 — Q03

منبع: [specs/007-daily-report-gaps/spec.md:149](../../specs/007-daily-report-gaps/spec.md#L149) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: An authorized user can create a draft with header work front, weather, one complete activity row (including responsible), and save successfully on both a narrow (mobile-width) and a wide layout.

### SC-002 — W03

منبع: [specs/007-daily-report-gaps/spec.md:150](../../specs/007-daily-report-gaps/spec.md#L150) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: In 100% of automated checks, direct edit of a locked report is rejected; a correction request with reason is the only path that yields a new editable version while retaining the prior locked version.

### SC-003 — D12

منبع: [specs/007-daily-report-gaps/spec.md:151](../../specs/007-daily-report-gaps/spec.md#L151) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-003**: Material return, labor absence, and a site event with owner + due date are each visible on report detail after save (verified in acceptance tests).

### SC-004 — D05

منبع: [specs/007-daily-report-gaps/spec.md:152](../../specs/007-daily-report-gaps/spec.md#L152) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: For activity and material quantities, blank/unset is never coerced to zero on save or submit in 100% of automated checks.

### SC-005 — D12

منبع: [specs/007-daily-report-gaps/spec.md:153](../../specs/007-daily-report-gaps/spec.md#L153) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-005**: When linked inventory data exists for a consumed material, a reconciliation indication (match, mismatch, or insufficient data) is available to the user without blocking report save.

### SC-006 — Q02

منبع: [specs/007-daily-report-gaps/spec.md:154](../../specs/007-daily-report-gaps/spec.md#L154) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-006**: A typical shift report that already has reference data loaded can still be completed in under 5 minutes after these gaps close (no extra mandatory screens beyond the correction path when amending).


## specs/028-auto-daily-report-summary/spec.md

### FR-001 — D01

منبع: [specs/028-auto-daily-report-summary/spec.md:92](../../specs/028-auto-daily-report-summary/spec.md#L92) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-001**: System MUST treat the project-level daily report as an automatic summary of that project’s specialty-unit (واحد تخصصی / رشته) daily reports for the same calendar date—not as a separately authored blank daily report.

### FR-002 — D03

منبع: [specs/028-auto-daily-report-summary/spec.md:93](../../specs/028-auto-daily-report-summary/spec.md#L93) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-002**: System MUST update the project daily report summary automatically when contributing specialty-unit reports for that date are created, updated, submitted, or removed, without requiring the user to press a “create new” or “rebuild” control on the project daily-report page.

### FR-003 — D01

منبع: [specs/028-auto-daily-report-summary/spec.md:94](../../specs/028-auto-daily-report-summary/spec.md#L94) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-003**: The project daily-report user interface MUST NOT offer a “گزارش جدید” / “New report” (or equivalent) control to manually create a project-level daily report.

### FR-004 — E02

منبع: [specs/028-auto-daily-report-summary/spec.md:95](../../specs/028-auto-daily-report-summary/spec.md#L95) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-004**: System MUST present the project daily report in a layout equivalent to the reference Excel daily sheet, including at least these sections when data exists:
  - Header (report title, date, weekday, project name, contract number)
  - Work hours / shifts
  - Site status (active / inactive)
  - Weather conditions
  - Indirect (staff) labor by job title with present/leave counts
  - Direct labor by job title with present/leave counts
  - Incoming materials
  - Concrete poured volumes
  - Executed site activities (description, shift, contractor, headcount, location fragment/block/floor, quantity, unit, notes)
  - General site activities
  - Issues / remarks
  - Project visits
  - Confirmation / approval and management opinion areas

### FR-005 — H06

منبع: [specs/028-auto-daily-report-summary/spec.md:109](../../specs/028-auto-daily-report-summary/spec.md#L109) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-005**: System MUST organize project daily reports by calendar date (one logical report per project per day), analogous to one Excel sheet per day in the reference workbook.

### FR-006 — D01

منبع: [specs/028-auto-daily-report-summary/spec.md:110](../../specs/028-auto-daily-report-summary/spec.md#L110) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-006**: Users MUST continue to author day-level operational detail through specialty-unit daily report flows; the project daily-report page is for viewing the consolidated summary (plus allowed summary-level metadata per FR-009).

### FR-007 — D06

منبع: [specs/028-auto-daily-report-summary/spec.md:111](../../specs/028-auto-daily-report-summary/spec.md#L111) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-007**: System MUST aggregate quantitative fields that share the same category key (e.g. same job title present/leave counts) by summing across contributing specialty reports for that date, unless a field is explicitly non-additive (e.g. narrative notes), in which case values are concatenated or listed with source attribution.

### FR-008 — D04

منبع: [specs/028-auto-daily-report-summary/spec.md:112](../../specs/028-auto-daily-report-summary/spec.md#L112) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-008**: System MUST list activity and material line items contributed by specialty reports in the summary (union of rows), preserving enough attribution (e.g. contractor, location, originating unit) for a reviewer to understand the source.

### FR-009 — W05

منبع: [specs/028-auto-daily-report-summary/spec.md:113](../../specs/028-auto-daily-report-summary/spec.md#L113) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-009**: Authorized users MUST be able to record project-level confirmation/approval and management opinion on the aggregated daily report without re-entering aggregated labor/activity rows.

### FR-010 — E09

منبع: [specs/028-auto-daily-report-summary/spec.md:114](../../specs/028-auto-daily-report-summary/spec.md#L114) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: System MUST restrict viewing and summary-level actions on project daily reports to users with the appropriate project permissions; lack of specialty-entry permission MUST NOT by itself block viewing an aggregated report they are otherwise allowed to see.

### FR-011 — H06

منبع: [specs/028-auto-daily-report-summary/spec.md:115](../../specs/028-auto-daily-report-summary/spec.md#L115) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-011**: When no specialty-unit reports exist for a date, the system MUST NOT require or invite manual creation of an empty project daily report; it MUST show a clear empty or “no specialty data” state for that date.

### FR-012 — D02

منبع: [specs/028-auto-daily-report-summary/spec.md:116](../../specs/028-auto-daily-report-summary/spec.md#L116) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-012**: System MUST make incompleteness visible when expected specialty units have not yet submitted for the day (e.g. missing-unit indicator or partial-summary banner).

### SC-001 — D01

منبع: [specs/028-auto-daily-report-summary/spec.md:134](../../specs/028-auto-daily-report-summary/spec.md#L134) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-001**: In usability checks, 100% of testers can open a day’s project daily report and identify it as the consolidated view of specialty reports without using any “create new project daily report” control.

### SC-002 — D01

منبع: [specs/028-auto-daily-report-summary/spec.md:135](../../specs/028-auto-daily-report-summary/spec.md#L135) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-002**: After specialty reports for a date are submitted, the project daily summary for that date is available without an extra manual create step (observable on first open/refresh of that date’s summary).

### SC-003 — E02

منبع: [specs/028-auto-daily-report-summary/spec.md:136](../../specs/028-auto-daily-report-summary/spec.md#L136) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: Side-by-side review against the reference Excel day sheet: at least 90% of the named sections in FR-004 are present and correctly labeled on the project daily report view.

### SC-004 — D06

منبع: [specs/028-auto-daily-report-summary/spec.md:137](../../specs/028-auto-daily-report-summary/spec.md#L137) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-004**: When two specialty units each report the same job-title present count for a day, the summary shows the correct summed total in spot checks (sample of ≥5 aggregation cases pass).

### SC-005 — D01

منبع: [specs/028-auto-daily-report-summary/spec.md:138](../../specs/028-auto-daily-report-summary/spec.md#L138) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-005**: Removing the project-level “new report” control does not prevent specialty-unit users from completing their own daily entry flows (specialty create/submit still succeeds in test scenarios).

### SC-006 — Q02

منبع: [specs/028-auto-daily-report-summary/spec.md:139](../../specs/028-auto-daily-report-summary/spec.md#L139) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-006**: Authorized approvers can complete summary-level confirmation or management opinion in under 2 minutes once the aggregated report is open.

### SC-007 — H06

منبع: [specs/028-auto-daily-report-summary/spec.md:140](../../specs/028-auto-daily-report-summary/spec.md#L140) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-007**: For a date with zero specialty submissions, users never reach a blank “create project daily report” form via a new-report button; they see an empty/no-data state instead.


## specs/030-daily-header-weather/spec.md

### FR-001 — H02

منبع: [specs/030-daily-header-weather/spec.md:87](../../specs/030-daily-header-weather/spec.md#L87) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-001**: The comprehensive daily report MUST use exactly five non-empty weather values: `clear`, `cloudy`, `rainy`, `snowy`, and `stormy`.

### FR-002 — H02

منبع: [specs/030-daily-header-weather/spec.md:88](../../specs/030-daily-header-weather/spec.md#L88) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-002**: User-facing labels MUST communicate `clear` as آفتابی / صاف, `cloudy` as ابری, `rainy` as بارانی, `snowy` as برفی, and `stormy` as طوفانی / گرد و غبار in Persian, with equivalent labels in English.

### FR-003 — H02

منبع: [specs/030-daily-header-weather/spec.md:89](../../specs/030-daily-header-weather/spec.md#L89) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-003**: Retired values `sunny`, `partly_cloudy`, and `foggy` MUST NOT be offered for new entry or accepted in new saves.

### FR-004 — H02

منبع: [specs/030-daily-header-weather/spec.md:90](../../specs/030-daily-header-weather/spec.md#L90) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-004**: Existing `sunny` values MUST be normalized to `clear` without deleting the owning report or changing unrelated report data.

### FR-005 — H02

منبع: [specs/030-daily-header-weather/spec.md:91](../../specs/030-daily-header-weather/spec.md#L91) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-005**: Existing `partly_cloudy` and `foggy` values MUST be normalized to `cloudy` without deleting the owning report or changing unrelated report data.

### FR-006 — H02

منبع: [specs/030-daily-header-weather/spec.md:92](../../specs/030-daily-header-weather/spec.md#L92) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-006**: When daily-summary weather is derived from multiple contributing approved values and no explicit project-level override applies, the system MUST select the most severe value using this descending order: `stormy`, `snowy`, `rainy`, `cloudy`, `clear`.

### FR-007 — H02

منبع: [specs/030-daily-header-weather/spec.md:93](../../specs/030-daily-header-weather/spec.md#L93) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-007**: All daily-report input, stored-data, readback, summary, and user-interface representations of non-empty weather MUST share the same five-value vocabulary.

### FR-008 — H02

منبع: [specs/030-daily-header-weather/spec.md:94](../../specs/030-daily-header-weather/spec.md#L94) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-008**: `temp_min` and `temp_max` MUST remain optional Celsius values, and each supplied value MUST be within -40°C through +60°C inclusive.

### FR-009 — H02

منبع: [specs/030-daily-header-weather/spec.md:95](../../specs/030-daily-header-weather/spec.md#L95) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-009**: When both current temperatures are known, `temp_max` MUST be greater than or equal to `temp_min`.

### FR-010 — H02

منبع: [specs/030-daily-header-weather/spec.md:96](../../specs/030-daily-header-weather/spec.md#L96) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: A violation of FR-009 MUST be reported on `temp_max` with the stable error code `temp_max_must_be_gte_temp_min` and clear localized recovery guidance.

### FR-011 — H02

منبع: [specs/030-daily-header-weather/spec.md:97](../../specs/030-daily-header-weather/spec.md#L97) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-011**: Temperature bounds and ordering rules MUST be enforced for every supported create, full-update, and partial-update path so that bypassing the interactive header cannot persist invalid temperatures.

### FR-012 — H02

منبع: [specs/030-daily-header-weather/spec.md:98](../../specs/030-daily-header-weather/spec.md#L98) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-012**: The interactive header MUST constrain each temperature input to the inclusive -40°C to +60°C range and MUST provide immediate, field-specific feedback for an out-of-range value or a maximum below the minimum before an invalid save completes.

### FR-013 — H02

منبع: [specs/030-daily-header-weather/spec.md:99](../../specs/030-daily-header-weather/spec.md#L99) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-013**: The daily report MUST support optional `weather_impact_notes` for operational and contractual weather impacts.

### FR-014 — H02

منبع: [specs/030-daily-header-weather/spec.md:100](../../specs/030-daily-header-weather/spec.md#L100) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-014**: Authorized editors MUST be able to enter and edit `weather_impact_notes` through a multi-line control in the daily-report header.

### FR-015 — H02

منبع: [specs/030-daily-header-weather/spec.md:101](../../specs/030-daily-header-weather/spec.md#L101) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-015**: Saved `weather_impact_notes` MUST be returned consistently in both header and detailed report views and MUST preserve Persian, English, mixed-language, and multi-line content.

### FR-016 — H02

منبع: [specs/030-daily-header-weather/spec.md:102](../../specs/030-daily-header-weather/spec.md#L102) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-016**: The official daily-report PDF MUST contain a header-table row labeled «توضیحات و اثرات شرایط جوی» and MUST reproduce the saved note exactly when present.

### FR-017 — H02

منبع: [specs/030-daily-header-weather/spec.md:103](../../specs/030-daily-header-weather/spec.md#L103) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-017**: All new user-facing weather labels and validation guidance MUST be available in Persian and English, while stable weather values, field names, and error codes remain language-independent.

### SC-001 — H02

منبع: [specs/030-daily-header-weather/spec.md:137](../../specs/030-daily-header-weather/spec.md#L137) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: Across a complete weather-value test matrix, 100% of the five approved values are available and accepted, while 100% of retired or unknown values are unavailable for selection and rejected when directly submitted.

### SC-002 — H02

منبع: [specs/030-daily-header-weather/spec.md:138](../../specs/030-daily-header-weather/spec.md#L138) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: After historical normalization, 100% of sampled reports containing `sunny`, `partly_cloudy`, or `foggy` remain accessible, preserve unrelated data, and contain only an approved weather value.

### SC-003 — H02

منبع: [specs/030-daily-header-weather/spec.md:139](../../specs/030-daily-header-weather/spec.md#L139) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: For every tested combination of approved contributing conditions, the displayed daily-summary weather matches the documented five-level severity order.

### SC-004 — H02

منبع: [specs/030-daily-header-weather/spec.md:140](../../specs/030-daily-header-weather/spec.md#L140) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: In temperature boundary testing, -40°C and +60°C are accepted, values immediately outside the range are rejected, and 100% of maximum-below-minimum cases identify `temp_max` with code `temp_max_must_be_gte_temp_min`.

### SC-005 — H02

منبع: [specs/030-daily-header-weather/spec.md:141](../../specs/030-daily-header-weather/spec.md#L141) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-005**: In interactive testing, 100% of invalid temperature entries are identified at the relevant field before an invalid header save completes, while valid boundary and equal-temperature cases save successfully.

### SC-006 — H02

منبع: [specs/030-daily-header-weather/spec.md:142](../../specs/030-daily-header-weather/spec.md#L142) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-006**: For every tested report with weather-impact notes, the complete saved text is visible after reopening and is reproduced in the official PDF; reports without notes still generate a valid PDF with the labeled row and no invented content.

### SC-007 — Q03

منبع: [specs/030-daily-header-weather/spec.md:143](../../specs/030-daily-header-weather/spec.md#L143) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-007**: At least 90% of representative Persian- and English-language editors can select weather, enter valid temperatures, correct one invalid temperature, and record weather-impact notes on the first attempt without external assistance.


## specs/031-site-inactivity-security/spec.md

### FR-001 — H03

منبع: [specs/031-site-inactivity-security/spec.md:83](../../specs/031-site-inactivity-security/spec.md#L83) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-001**: The daily report MUST support an `inactivity_reason` value drawn from exactly five standard reasons: `weather` (unfavorable weather), `holiday` (official/calendar holiday), `strike_or_dispute` (labor dispute or strike), `client_stop_order` (stop order by the client or the consultant), and `safety_incident` (safety incident).

### FR-002 — H03

منبع: [specs/031-site-inactivity-security/spec.md:84](../../specs/031-site-inactivity-security/spec.md#L84) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-002**: When the daily report's site status is inactive, `inactivity_reason` MUST be filled; saving an inactive report with an empty reason MUST be rejected with the stable error code `inactivity_reason_required` attached to the `inactivity_reason` field.

### FR-003 — H03

منبع: [specs/031-site-inactivity-security/spec.md:85](../../specs/031-site-inactivity-security/spec.md#L85) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-003**: When the daily report's site status is active, `inactivity_reason` MUST NOT be required, and a previously recorded reason MUST be cleared or ignored on save of an active report.

### FR-004 — H03

منبع: [specs/031-site-inactivity-security/spec.md:86](../../specs/031-site-inactivity-security/spec.md#L86) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-004**: In the report header editing surface, the closure-reason selector MUST appear dynamically while the selected site status is inactive and MUST offer exactly the five approved reasons in both Persian and English catalogs.

### FR-005 — H03

منبع: [specs/031-site-inactivity-security/spec.md:87](../../specs/031-site-inactivity-security/spec.md#L87) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-005**: User-facing closure and reason labels and the inactive-day warning message MUST be available in Persian and English, while the stable reason values, field names, and error code remain language-independent.

### FR-006 — H03

منبع: [specs/031-site-inactivity-security/spec.md:88](../../specs/031-site-inactivity-security/spec.md#L88) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-006**: When the daily report's site status is inactive, the official daily-report PDF MUST show both the inactive status and the recorded inactivity reason in the header table, using the same localized label chosen at save time.

### FR-007 — H03

منبع: [specs/031-site-inactivity-security/spec.md:89](../../specs/031-site-inactivity-security/spec.md#L89) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-007**: When the daily report's site status is active, the official PDF MUST show the active status and MUST NOT render a fabricated closure reason.

### FR-008 — H03

منبع: [specs/031-site-inactivity-security/spec.md:90](../../specs/031-site-inactivity-security/spec.md#L90) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-008**: When the daily report's site status is inactive, entering or editing an activity row with a done quantity strictly greater than zero MUST require an explicit confirmation warning before the row is accepted, with the exact localized warning text «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟».

### FR-009 — H03

منبع: [specs/031-site-inactivity-security/spec.md:91](../../specs/031-site-inactivity-security/spec.md#L91) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-009**: Confirming the inactive-day warning MUST persist the activity row as entered, and canceling MUST leave the record unchanged with the unsaved entry still in the editor.

### FR-010 — H03

منبع: [specs/031-site-inactivity-security/spec.md:92](../../specs/031-site-inactivity-security/spec.md#L92) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: The inactivity-reason requirement MUST be enforced on every supported create, full-update, and partial-update path so bypassing the interactive header cannot persist an inactive report without a reason.

### FR-011 — H06

منبع: [specs/031-site-inactivity-security/spec.md:93](../../specs/031-site-inactivity-security/spec.md#L93) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-011**: The daily-report shell creation operation behind the existing by-date endpoint MUST be denied to members whose effective permissions lack report-edit permission, and MUST remain available to members who hold it.

### FR-012 — H06

منبع: [specs/031-site-inactivity-security/spec.md:94](../../specs/031-site-inactivity-security/spec.md#L94) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-012**: Reading existing daily reports by date or by identifier MUST continue to work for members with report-view permission without any change in behavior.

### SC-001 — H03

منبع: [specs/031-site-inactivity-security/spec.md:113](../../specs/031-site-inactivity-security/spec.md#L113) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: Across a complete closure-reason test matrix, 100% of the five approved reasons are available, accepted, and read back in header, detail, and PDF, and 100% of unknown or retired reason strings are rejected on new saves.

### SC-002 — H03

منبع: [specs/031-site-inactivity-security/spec.md:114](../../specs/031-site-inactivity-security/spec.md#L114) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: 100% of tested inactive-save attempts without a reason are rejected with the code `inactivity_reason_required` attached to `inactivity_reason`, across create, full update, and partial update.

### SC-003 — H03

منبع: [specs/031-site-inactivity-security/spec.md:115](../../specs/031-site-inactivity-security/spec.md#L115) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: In closure-reason testing, every tested report switched back to active saves successfully with its reason requirement lifted, and no stale reason remains on the saved active record.

### SC-004 — H03

منبع: [specs/031-site-inactivity-security/spec.md:116](../../specs/031-site-inactivity-security/spec.md#L116) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: In inactive-day activity testing, 100% of positive-quantity creates and edits trigger the warning; confirming proceeds 100% of the time and canceling saves nothing 100% of the time; zero-quantity and blank-quantity entries never trigger the warning.

### SC-005 — H06

منبع: [specs/031-site-inactivity-security/spec.md:117](../../specs/031-site-inactivity-security/spec.md#L117) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-005**: In permission testing, 100% of shell-creation attempts by view-only members are denied with the standard forbidden outcome, 100% of attempts by editing members succeed as before, and read-by-date behavior for viewers is unchanged.

### SC-006 — H03

منبع: [specs/031-site-inactivity-security/spec.md:118](../../specs/031-site-inactivity-security/spec.md#L118) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-006**: In official PDF verification, 100% of inactive reports display the recorded reason in the header table and 100% of active reports show no fabricated closure-reason text.

### SC-007 — Q03

منبع: [specs/031-site-inactivity-security/spec.md:119](../../specs/031-site-inactivity-security/spec.md#L119) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-007**: At least 90% of representative Persian- and English-language editors can mark a site closed, choose a reason, record the closure cycle, and acknowledge or cancel the inactive-day warning on the first attempt without external assistance.


## specs/032-unit-report-source-truth/spec.md

### FR-001 — D02

منبع: [specs/032-unit-report-source-truth/spec.md:144](../../specs/032-unit-report-source-truth/spec.md#L144) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-001**: The product MUST use one canonical set of unit identifiers across Specialty Units navigation, unit-report ownership, permissions, project templates, completeness, provenance, and project daily summaries:

  | Canonical identifier | Display meaning |
  |---|---|
  | `buildings` | Buildings / ابنیه |
  | `electrical` | Electrical / برق |
  | `mechanical` | Mechanical / مکانیک |
  | `machinery` | Machinery / ماشین‌آلات |
  | `warehouse` | Warehouse / انبار |
  | `security` | Security/HSE / حراست و HSE |

### FR-002 — Q03

منبع: [specs/032-unit-report-source-truth/spec.md:155](../../specs/032-unit-report-source-truth/spec.md#L155) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-002**: Stable identifiers MUST remain language-independent, while unit names, states, validation feedback, and workflow actions MUST be presented correctly in Persian and English.

### FR-003 — D02

منبع: [specs/032-unit-report-source-truth/spec.md:156](../../specs/032-unit-report-source-truth/spec.md#L156) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-003**: Project templates MUST declare which canonical units are required for dates on which that template is effective; required units MUST NOT be inferred from a hard-coded three-discipline default.

### FR-004 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:157](../../specs/032-unit-report-source-truth/spec.md#L157) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8/A.12

- **FR-004**: Legacy discipline values MUST map as follows for migration: `civil` and `finishing` to `buildings`; `plumbing` and `hvac` to `mechanical`; `electrical` to `electrical`; and legacy `mechanical` to `mechanical`. The remaining canonical units MUST be populated only from their matching unit data or an explicitly reviewed migration decision, never by guessing.

### FR-005 — D02

منبع: [specs/032-unit-report-source-truth/spec.md:158](../../specs/032-unit-report-source-truth/spec.md#L158) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-005**: Legacy discipline labels MUST NOT remain selectable as additional product units after migration.

### FR-006 — H06

منبع: [specs/032-unit-report-source-truth/spec.md:162](../../specs/032-unit-report-source-truth/spec.md#L162) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-006**: Each unit report MUST be owned by exactly one project, one report date, and one canonical unit.

### FR-007 — H06

منبع: [specs/032-unit-report-source-truth/spec.md:163](../../specs/032-unit-report-source-truth/spec.md#L163) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-007**: For each project, date, and canonical unit, the product MUST expose at most one current active version while retaining all superseded versions and state history.

### FR-008 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:164](../../specs/032-unit-report-source-truth/spec.md#L164) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-008**: Unit report authoring and workflow actions MUST be available only on the corresponding unit page under the top-level Specialty Units menu.

### FR-009 — H06

منبع: [specs/032-unit-report-source-truth/spec.md:165](../../specs/032-unit-report-source-truth/spec.md#L165) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-009**: An authorized user MUST be able to select a date on a unit page and open the current report or create a draft when no current version exists.

### FR-010 — W01

منبع: [specs/032-unit-report-source-truth/spec.md:166](../../specs/032-unit-report-source-truth/spec.md#L166) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: Unit reports MUST support `draft`, `submitted`, `approved`, and `rejected` states.

### FR-011 — W03

منبع: [specs/032-unit-report-source-truth/spec.md:167](../../specs/032-unit-report-source-truth/spec.md#L167) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-011**: Only current reports in `draft` or `rejected` state MAY be edited; submitted and approved content MUST be immutable unless an authorized correction action establishes a new current editable version while preserving history.

### FR-012 — W01

منبع: [specs/032-unit-report-source-truth/spec.md:168](../../specs/032-unit-report-source-truth/spec.md#L168) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-012**: Submission, approval, rejection, correction, and current-version replacement MUST record the acting user and time; rejection MUST additionally require and retain a reason.

### FR-013 — W02

منبع: [specs/032-unit-report-source-truth/spec.md:169](../../specs/032-unit-report-source-truth/spec.md#L169) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-013**: The unit page MUST show current state, last-change time, preparer, submitter, approver when applicable, rejection actor and reason when applicable, and access to authorized version history.

### FR-014 — E09

منبع: [specs/032-unit-report-source-truth/spec.md:170](../../specs/032-unit-report-source-truth/spec.md#L170) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-014**: View, create/edit, submit, approve, and reject actions MUST each enforce the corresponding project permission at the trusted authorization boundary.

### FR-015 — E09

منبع: [specs/032-unit-report-source-truth/spec.md:171](../../specs/032-unit-report-source-truth/spec.md#L171) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-015**: Every unit-report lookup and mutation MUST enforce project membership and project scope; knowing a report or source identifier MUST NOT enable cross-project access.

### FR-016 — E09

منبع: [specs/032-unit-report-source-truth/spec.md:172](../../specs/032-unit-report-source-truth/spec.md#L172) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-016**: Approval MUST enforce the project’s active segregation-of-duties policy and MUST NOT allow a prohibited preparer, submitter, or other conflicted actor to approve their own report.

### FR-017 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:176](../../specs/032-unit-report-source-truth/spec.md#L176) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-017**: Current unit-report data authored on Specialty Units pages MUST be the sole operational source for unit-derived content in the project daily summary.

### FR-018 — D03

منبع: [specs/032-unit-report-source-truth/spec.md:177](../../specs/032-unit-report-source-truth/spec.md#L177) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-018**: A current unit report MAY contribute only when it belongs to the same project and date as the summary, has state `submitted` or `approved`, and is not deleted.

### FR-019 — D03

منبع: [specs/032-unit-report-source-truth/spec.md:178](../../specs/032-unit-report-source-truth/spec.md#L178) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-019**: Draft, rejected, deleted, superseded, different-project, and different-date reports MUST contribute no rows, totals, narratives, or completeness credit.

### FR-020 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:179](../../specs/032-unit-report-source-truth/spec.md#L179) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-020**: The project daily summary MUST remain an automatically obtained, read-only consolidation for its date; product users MUST NOT create a raw project-level daily report or directly edit unit-derived rows there.

### FR-021 — W04

منبع: [specs/032-unit-report-source-truth/spec.md:180](../../specs/032-unit-report-source-truth/spec.md#L180) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-021**: Every current derived row MUST retain the source unit-report identifier, canonical unit identifier, and source-row identifier.

### FR-022 — W04

منبع: [specs/032-unit-report-source-truth/spec.md:181](../../specs/032-unit-report-source-truth/spec.md#L181) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-022**: Every derived total or combined value with more than one source MUST retain the complete set of contributing report and row references; source attribution MUST NOT use a last-source-wins rule.

### FR-023 — W04

منبع: [specs/032-unit-report-source-truth/spec.md:182](../../specs/032-unit-report-source-truth/spec.md#L182) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-023**: Summary rebuilding MUST be deterministic, repeatable, and idempotent: the same current eligible sources and project-level overrides MUST produce the same derived content, provenance, and completeness result without duplicates.

### FR-024 — W04

منبع: [specs/032-unit-report-source-truth/spec.md:183](../../specs/032-unit-report-source-truth/spec.md#L183) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-024**: A rebuild after rejection, deletion, correction, resubmission, approval, or current-version replacement MUST remove obsolete contributions before applying the current eligible contribution.

### FR-025 — W05

منبع: [specs/032-unit-report-source-truth/spec.md:184](../../specs/032-unit-report-source-truth/spec.md#L184) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-025**: Rebuilding derived content MUST preserve authorized summary-owned information, including management opinion and explicit project-level site-status or weather overrides.

### FR-026 — D02

منبع: [specs/032-unit-report-source-truth/spec.md:185](../../specs/032-unit-report-source-truth/spec.md#L185) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-026**: Each summary MUST report the canonical units expected by the template effective for its date, the units with current eligible contributions, the required units still missing, and whether the summary is partial.

### FR-027 — D02

منبع: [specs/032-unit-report-source-truth/spec.md:186](../../specs/032-unit-report-source-truth/spec.md#L186) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-027**: A summary MUST be marked non-partial only when every unit required by the effective template has a current eligible report; non-required contributors MUST NOT be reported as missing.

### FR-028 — D02

منبع: [specs/032-unit-report-source-truth/spec.md:187](../../specs/032-unit-report-source-truth/spec.md#L187) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-028**: If no effective project template can establish expected units, the summary MUST expose a configuration-incomplete state and MUST NOT claim completeness.

### FR-029 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:191](../../specs/032-unit-report-source-truth/spec.md#L191) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-029**: The product MUST remove the standalone `/projects/{projectId}/sub-reports` authoring experience from routes, navigation, calls to action, empty states, translations, and user-workflow tests.

### FR-030 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:192](../../specs/032-unit-report-source-truth/spec.md#L192) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-030**: Direct navigation to the legacy `/sub-reports` route MUST show the standard not-found experience and MUST NOT disclose reports or render any data-entry form.

### FR-031 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:193](../../specs/032-unit-report-source-truth/spec.md#L193) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-031**: The project daily-report experience MUST contain neither a “New Report” control nor a link to the legacy specialty-report route.

### FR-032 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:194](../../specs/032-unit-report-source-truth/spec.md#L194) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-032**: A temporarily retained legacy service or data structure MAY exist only as an internal compatibility detail, MUST NOT provide a parallel user authoring workflow, and MUST have an explicit retirement milestone recorded during planning.

### FR-033 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:195](../../specs/032-unit-report-source-truth/spec.md#L195) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8/A.12

- **FR-033**: Migration MUST preserve every valid legacy report, its stable identifier where possible, content, state and workflow history, original discipline evidence, actors, timestamps, rejection reason, source-row identity, and existing summary relationships.

### FR-034 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:196](../../specs/032-unit-report-source-truth/spec.md#L196) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8/A.12

- **FR-034**: Migration MUST normalize legacy taxonomy and duplicate-current inconsistencies before enforcing canonical taxonomy or one-current-version rules.

### FR-035 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:197](../../specs/032-unit-report-source-truth/spec.md#L197) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8/A.12

- **FR-035**: When multiple non-identical legacy reports map to the same canonical project/date/unit key, migration MUST preserve all as history and select the current version by latest business change time, using the stable legacy identifier as the deterministic tie-breaker; the choice and all displaced current markers MUST be recorded in an auditable migration trace.

### FR-036 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:198](../../specs/032-unit-report-source-truth/spec.md#L198) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8/A.12

- **FR-036**: Exact duplicate legacy records MAY be consolidated for current-state purposes only if every original identifier remains resolvable through the migration trace and no content or workflow evidence is lost.

### FR-037 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:199](../../specs/032-unit-report-source-truth/spec.md#L199) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8/A.12

- **FR-037**: Unknown or invalid legacy categories MUST be quarantined for explicit review rather than silently mapped or discarded.

### FR-038 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:200](../../specs/032-unit-report-source-truth/spec.md#L200) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8/A.12

- **FR-038**: Migration MUST define and verify a rollback that reconstructs original category values, current-version relationships, and summary links from the migration trace before irreversible cleanup occurs.

### SC-001 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:218](../../specs/032-unit-report-source-truth/spec.md#L218) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-001**: In end-to-end acceptance checks, all six canonical unit pages allow an authorized user to open or create that unit’s report for a date, and zero supported product flows offer a second specialty-report authoring location.

### SC-002 — E09

منبع: [specs/032-unit-report-source-truth/spec.md:219](../../specs/032-unit-report-source-truth/spec.md#L219) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: Across the mandatory permission matrix, 100% of unauthorized and cross-project attempts to view, create, edit, submit, approve, or reject unit reports are denied without report-content disclosure.

### SC-003 — D03

منبع: [specs/032-unit-report-source-truth/spec.md:220](../../specs/032-unit-report-source-truth/spec.md#L220) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-003**: For representative dates containing eligible, draft, rejected, deleted, superseded, cross-project, and cross-date reports, 100% of summary contributions come only from current submitted or approved reports for the matching project and date.

### SC-004 — W04

منبع: [specs/032-unit-report-source-truth/spec.md:221](../../specs/032-unit-report-source-truth/spec.md#L221) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: Rebuilding the same summary at least three consecutive times with unchanged inputs produces identical content, row counts, provenance sets, completeness metadata, and project-level overrides, with zero duplicate derived items.

### SC-005 — W04

منبع: [specs/032-unit-report-source-truth/spec.md:222](../../specs/032-unit-report-source-truth/spec.md#L222) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-005**: In correction tests, 100% of obsolete source contributions disappear after rebuild and 100% of current resubmitted contributions appear exactly once with correct provenance.

### SC-006 — D02

منبع: [specs/032-unit-report-source-truth/spec.md:223](../../specs/032-unit-report-source-truth/spec.md#L223) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-006**: For projects with different required-unit templates, expected, contributing, and missing unit sets match the effective template in every acceptance case; a date is never reported complete while any required unit lacks an eligible report.

### SC-007 — D01

منبع: [specs/032-unit-report-source-truth/spec.md:224](../../specs/032-unit-report-source-truth/spec.md#L224) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-007**: Product-wide navigation and direct-route checks in Persian and English find zero links, calls to action, empty-state prompts, or forms that expose `/sub-reports`; direct access displays the standard not-found state.

### SC-008 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:225](../../specs/032-unit-report-source-truth/spec.md#L225) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8/A.12

- **SC-008**: A migration rehearsal over representative legacy and inconsistent data accounts for 100% of source reports and source rows as migrated, historically retained, or explicitly quarantined; no valid record is silently dropped.

### SC-009 — X08

منبع: [specs/032-unit-report-source-truth/spec.md:226](../../specs/032-unit-report-source-truth/spec.md#L226) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8/A.12

- **SC-009**: After migration, 100% of sampled legacy identifiers and existing summary links remain directly resolvable or traceable through the migration record, and the rehearsed rollback reconstructs their prior categories and relationships.

### SC-010 — Q03

منبع: [specs/032-unit-report-source-truth/spec.md:227](../../specs/032-unit-report-source-truth/spec.md#L227) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-010**: In usability checks, at least 90% of representative unit users can select a date, locate report status, submit a draft, and find rejection feedback on their first attempt without visiting the project daily-report page.


## specs/033-daily-sections-grid/spec.md

### FR-001 — D04

منبع: [specs/033-daily-sections-grid/spec.md:186](../../specs/033-daily-sections-grid/spec.md#L186) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-001**: Each executed-activity row MUST include an approved, active project WBS activity, an activity description, a shift, an active project contractor, headcount, parcel, block, floor, location, a completed quantity, a unit, and optional notes; aggregation MUST reproduce all of these columns.

### FR-002 — D05

منبع: [specs/033-daily-sections-grid/spec.md:187](../../specs/033-daily-sections-grid/spec.md#L187) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-002**: When a completed quantity is provided, it MUST be positive; zero and negative quantities MUST be rejected with an explicit, localized error.

### FR-003 — D04

منبع: [specs/033-daily-sections-grid/spec.md:188](../../specs/033-daily-sections-grid/spec.md#L188) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-003**: The submitted WBS activity and contractor MUST belong to the same project as the report; identifiers from another project MUST be rejected with a permission or validation error.

### FR-004 — D04

منبع: [specs/033-daily-sections-grid/spec.md:189](../../specs/033-daily-sections-grid/spec.md#L189) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-004**: Crew name and contractor MUST be recorded and displayed as separate concepts, and aggregation MUST NOT substitute one for the other.

### FR-005 — H04

منبع: [specs/033-daily-sections-grid/spec.md:190](../../specs/033-daily-sections-grid/spec.md#L190) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-005**: An unrecognized shift value MUST NOT be silently remapped to another shift; it MUST be rejected or clearly marked as unknown.

### FR-006 — D06

منبع: [specs/033-daily-sections-grid/spec.md:194](../../specs/033-daily-sections-grid/spec.md#L194) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-006**: Labor rows MUST record, per job title, the category (indirect or direct), present count, leave/absence count, associated contractor, and overtime.

### FR-007 — D06

منبع: [specs/033-daily-sections-grid/spec.md:195](../../specs/033-daily-sections-grid/spec.md#L195) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-007**: Labor counts MUST be non-negative integers; negative counts MUST be rejected with an explicit error.

### FR-008 — D07

منبع: [specs/033-daily-sections-grid/spec.md:196](../../specs/033-daily-sections-grid/spec.md#L196) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-008**: Man-hours MUST be reproducibly calculated using the project-approved rule associated with the project's reporting template; the same inputs MUST always yield the same result.

### FR-009 — D06

منبع: [specs/033-daily-sections-grid/spec.md:197](../../specs/033-daily-sections-grid/spec.md#L197) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-009**: Indirect category totals, direct category totals, and an overall total MUST be calculable for output at any time.

### FR-010 — D08

منبع: [specs/033-daily-sections-grid/spec.md:198](../../specs/033-daily-sections-grid/spec.md#L198) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-010**: The job-title catalog MUST be versioned and configurable at the project-template level; no fixed title counts (such as 34/32, 33/32, or 32/36) MAY be hard-coded as universal truth.

### FR-011 — D08

منبع: [specs/033-daily-sections-grid/spec.md:199](../../specs/033-daily-sections-grid/spec.md#L199) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-011**: The catalog MUST support migration of legacy titles, explicit display order, and project-specific titles without losing historical title evidence.

### FR-012 — W04

منبع: [specs/033-daily-sections-grid/spec.md:200](../../specs/033-daily-sections-grid/spec.md#L200) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-012**: When one job title contributes from multiple unit reports, the aggregate MUST retain every contributing source and MUST NOT attribute the total solely to the last unit.

### FR-013 — D09

منبع: [specs/033-daily-sections-grid/spec.md:204](../../specs/033-daily-sections-grid/spec.md#L204) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-013**: For every equipment type or stable equipment identifier, the product MUST record or derive total, active, ready-to-work, inactive, and under-repair counts for the reporting day.

### FR-014 — D09

منبع: [specs/033-daily-sections-grid/spec.md:205](../../specs/033-daily-sections-grid/spec.md#L205) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-014**: Where operationally needed, operating, stoppage, and repair hours and the stoppage reason MUST be recorded with the equipment row.

### FR-015 — D09

منبع: [specs/033-daily-sections-grid/spec.md:206](../../specs/033-daily-sections-grid/spec.md#L206) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-015**: A stoppage reason MUST be provided whenever stoppage hours exceed zero; rows without it MUST be rejected with an explicit error.

### FR-016 — D09

منبع: [specs/033-daily-sections-grid/spec.md:207](../../specs/033-daily-sections-grid/spec.md#L207) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-016**: The total recorded time for one equipment item MUST NOT exceed 24 hours in a single day.

### FR-017 — D09

منبع: [specs/033-daily-sections-grid/spec.md:208](../../specs/033-daily-sections-grid/spec.md#L208) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-017**: Stoppage reasons MUST be controlled, translatable values; values outside the controlled vocabulary MUST be rejected.

### FR-018 — D09

منبع: [specs/033-daily-sections-grid/spec.md:209](../../specs/033-daily-sections-grid/spec.md#L209) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-018**: An equipment item with a stable identity MUST NOT be counted twice in one day's aggregation.

### FR-019 — D12

منبع: [specs/033-daily-sections-grid/spec.md:213](../../specs/033-daily-sections-grid/spec.md#L213) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-019**: Material records MUST preserve receipts, issues/consumption, units, consumption location, supplier, and warehouse-document reference independently and simultaneously.

### FR-020 — D11

منبع: [specs/033-daily-sections-grid/spec.md:214](../../specs/033-daily-sections-grid/spec.md#L214) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-020**: The main project daily-report materials table MUST display only real receipts, matching the reference output form.

### FR-021 — D11

منبع: [specs/033-daily-sections-grid/spec.md:215](../../specs/033-daily-sections-grid/spec.md#L215) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-021**: The aggregation engine MUST mark an item as received only when it is a real receipt and MUST NOT blindly convert generic material rows into receipts.

### FR-022 — D12

منبع: [specs/033-daily-sections-grid/spec.md:216](../../specs/033-daily-sections-grid/spec.md#L216) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-022**: Consumption and reconciliation MUST remain available in visible details or a drill-down from the daily report.

### FR-023 — D12

منبع: [specs/033-daily-sections-grid/spec.md:217](../../specs/033-daily-sections-grid/spec.md#L217) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-023**: Reconciliation MUST compare against the specific warehouse document a record references, not merely the total historical inventory balance.

### FR-024 — D12

منبع: [specs/033-daily-sections-grid/spec.md:218](../../specs/033-daily-sections-grid/spec.md#L218) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-024**: Reconciliation MUST produce explicit, traceable statuses — match, mismatch, and insufficient data — with the comparison anchored to the referenced document.

### FR-025 — D13

منبع: [specs/033-daily-sections-grid/spec.md:222](../../specs/033-daily-sections-grid/spec.md#L222) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-025**: Each concrete record MUST include description or grade, a positive volume, structural element or location, parcel, block, floor, batching plant, truck or delivery-note number, laboratory sample code, sampling state, and test-sheet count.

### FR-026 — D13

منبع: [specs/033-daily-sections-grid/spec.md:223](../../specs/033-daily-sections-grid/spec.md#L223) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-026**: When sampling is declared, the required test information MUST be present and a traceable link to the corresponding quality-control work MUST be created.

### FR-027 — D13

منبع: [specs/033-daily-sections-grid/spec.md:224](../../specs/033-daily-sections-grid/spec.md#L224) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-027**: Negative volumes and references to data belonging to another project MUST be rejected.

### FR-028 — D14

منبع: [specs/033-daily-sections-grid/spec.md:228](../../specs/033-daily-sections-grid/spec.md#L228) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-028**: A general activity MUST remain a structured row — description, location/building, quantity/volume, unit, and notes — and MUST NOT be converted into formatted text for storage.

### FR-029 — D16

منبع: [specs/033-daily-sections-grid/spec.md:229](../../specs/033-daily-sections-grid/spec.md#L229) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-029**: Issues/barriers and project visits MUST be structured records with source unit, date, text, and display order.

### FR-030 — D14

منبع: [specs/033-daily-sections-grid/spec.md:230](../../specs/033-daily-sections-grid/spec.md#L230) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-030**: A barrier MUST include an owner and a due date.

### FR-031 — D15

منبع: [specs/033-daily-sections-grid/spec.md:231](../../specs/033-daily-sections-grid/spec.md#L231) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-031**: An HSE incident MUST include a severity and an immediate action and MUST create the required notification or follow-up task.

### FR-032 — D14

منبع: [specs/033-daily-sections-grid/spec.md:232](../../specs/033-daily-sections-grid/spec.md#L232) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-032**: A general note MUST NOT be automatically classified as an issue unless it is explicitly typed as one.

### FR-033 — D17

منبع: [specs/033-daily-sections-grid/spec.md:236](../../specs/033-daily-sections-grid/spec.md#L236) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-033**: Units MAY attach JPEG/PNG images up to 10 MB to a related activity.

### FR-034 — D17

منبع: [specs/033-daily-sections-grid/spec.md:237](../../specs/033-daily-sections-grid/spec.md#L237) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-034**: Each attachment MUST preserve capture date, work front, source activity, source unit, and the file's project.

### FR-035 — D17

منبع: [specs/033-daily-sections-grid/spec.md:238](../../specs/033-daily-sections-grid/spec.md#L238) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-035**: Files that are not valid JPEG/PNG within the size limit — including ZIP, EXE, and other invalid types or mis-declared types — MUST be rejected with explicit errors, and files MUST NOT be attached across projects.

### FR-036 — D17

منبع: [specs/033-daily-sections-grid/spec.md:239](../../specs/033-daily-sections-grid/spec.md#L239) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-036**: The project daily report MUST offer an accessible image count with links per relevant section; the specification MUST NOT require a large gallery in the printable form without an approved need.

### FR-037 — D03

منبع: [specs/033-daily-sections-grid/spec.md:243](../../specs/033-daily-sections-grid/spec.md#L243) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-037**: Only data from unit reports in the permitted workflow states for the same project and date — as established by the unit source-of-truth feature — MAY contribute to the summary; draft, rejected, superseded, other-project, and other-date data MUST contribute nothing.

### FR-038 — W04

منبع: [specs/033-daily-sections-grid/spec.md:244](../../specs/033-daily-sections-grid/spec.md#L244) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-038**: Rebuilding MUST be atomic and idempotent: a mid-process failure MUST leave the prior valid summary intact, and repeated rebuilds with unchanged inputs MUST produce identical results without duplicate rows.

### FR-039 — W04

منبع: [specs/033-daily-sections-grid/spec.md:245](../../specs/033-daily-sections-grid/spec.md#L245) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-039**: Every section MUST preserve row-level provenance, and every total or combined value from more than one source MUST preserve the complete multi-source provenance set.

### FR-040 — D10

منبع: [specs/033-daily-sections-grid/spec.md:246](../../specs/033-daily-sections-grid/spec.md#L246) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-040**: Empty data, an actual zero, and an unknown value MUST remain distinct everywhere in the summary; missing data MUST NOT become a fabricated zero.

### FR-041 — D14

منبع: [specs/033-daily-sections-grid/spec.md:247](../../specs/033-daily-sections-grid/spec.md#L247) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-041**: General activities, issues, and visits MUST be transferred into structured project-report records; markup or markers embedded in free text MUST NOT be the source of truth for structure.

### FR-042 — W05

منبع: [specs/033-daily-sections-grid/spec.md:248](../../specs/033-daily-sections-grid/spec.md#L248) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-042**: Rebuilding MUST preserve project-level overrides and the management opinion.

### FR-043 — W03

منبع: [specs/033-daily-sections-grid/spec.md:249](../../specs/033-daily-sections-grid/spec.md#L249) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-043**: Derived rows in the project report MUST be read-only to product users; content corrections MUST be made only in the source unit report and then flow through rebuild.

### FR-044 — W04

منبع: [specs/033-daily-sections-grid/spec.md:250](../../specs/033-daily-sections-grid/spec.md#L250) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-044**: Rejecting or replacing a unit report MUST remove or replace only that unit's previous contribution in the current summary, leaving other units' contributions untouched.

### FR-045 — D16

منبع: [specs/033-daily-sections-grid/spec.md:251](../../specs/033-daily-sections-grid/spec.md#L251) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-045**: Structure and display order of transferred general activities, issues, and visits MUST be preserved across rebuilds, including when multiple units contribute.

### SC-001 — Q03

منبع: [specs/033-daily-sections-grid/spec.md:269](../../specs/033-daily-sections-grid/spec.md#L269) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: Every mandatory acceptance scenario of this feature passes end to end — from unit-page entry through aggregation to project-report viewing — with zero undocumented extrapolations.

### SC-002 — W04

منبع: [specs/033-daily-sections-grid/spec.md:270](../../specs/033-daily-sections-grid/spec.md#L270) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: Rebuilding the same summary at least three consecutive times with unchanged inputs yields identical content, row counts, ordering of structured records, provenance sets, and project-level overrides, with zero duplicate or stale derived items.

### SC-003 — E09

منبع: [specs/033-daily-sections-grid/spec.md:271](../../specs/033-daily-sections-grid/spec.md#L271) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: Across the permission and validation matrix, 100% of identifiers, rows, and attachments that belong to another project — activities, contractors, equipment, concrete references, and files — are rejected without storing any cross-project reference.

### SC-004 — D05

منبع: [specs/033-daily-sections-grid/spec.md:272](../../specs/033-daily-sections-grid/spec.md#L272) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: 100% of contractually invalid inputs — zero or negative completed quantities, negative counts, negative volumes, a stoppage without a reason, equipment time exceeding 24 hours, uncontrolled stoppage reasons, unrecognized shifts, unknown job titles, and invalid or oversized files — are rejected with explicit, localized errors and leave no partial data.

### SC-005 — W04

منبع: [specs/033-daily-sections-grid/spec.md:273](../../specs/033-daily-sections-grid/spec.md#L273) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-005**: For every combined total with more than one contributing source, the drill-down lists 100% of contributing rows and reports; no total is ever attributed solely to its most recent source.

### SC-006 — D09

منبع: [specs/033-daily-sections-grid/spec.md:274](../../specs/033-daily-sections-grid/spec.md#L274) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-006**: In machinery aggregation, every equipment item with a stable identity appears exactly once, and the five-status table values match the Machinery unit report for the day in 100% of acceptance cases.

### SC-007 — D12

منبع: [specs/033-daily-sections-grid/spec.md:275](../../specs/033-daily-sections-grid/spec.md#L275) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-007**: The main materials table contains only confirmed real receipts; 100% of consumption records remain retrievable through visible details or drill-down, and every reconciliation result is anchored to a specific referenced warehouse document with a match, mismatch, or insufficient-data status.

### SC-008 — D14

منبع: [specs/033-daily-sections-grid/spec.md:276](../../specs/033-daily-sections-grid/spec.md#L276) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-008**: After any rebuild, 100% of transferred general activities, issues, and visits retain their fieldwise structure, source attribution, and display order, with zero conversions to formatted text for storage.

### SC-009 — W03

منبع: [specs/033-daily-sections-grid/spec.md:277](../../specs/033-daily-sections-grid/spec.md#L277) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-009**: In usability checks, a user who spots an error in a derived project-report row can reach the responsible source unit report through provenance in a single attempt, and every derived row is confirmed read-only in the project report.

### SC-010 — Q03

منبع: [specs/033-daily-sections-grid/spec.md:278](../../specs/033-daily-sections-grid/spec.md#L278) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-010**: Acceptance criteria are executed in a test-first manner: for each mandatory scenario, a failing behavioral check exists before the smallest production change that makes it pass, covering validation, authorization, idempotent aggregation, and the unit-to-summary browser end-to-end path.


## specs/034-daily-lifecycle-lock/spec.md

### FR-001 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:87](../../specs/034-daily-lifecycle-lock/spec.md#L87) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-001**: The system MUST create a correction draft only from the permitted current approved report and preserve its lineage identity while assigning the next version number.

### FR-002 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:88](../../specs/034-daily-lifecycle-lock/spec.md#L88) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-002**: When creating a correction draft, the system MUST preserve all active activity-row values, including crew name, foreman count, worker count, parcel, and referenced contractor.

### FR-003 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:89](../../specs/034-daily-lifecycle-lock/spec.md#L89) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-003**: When creating a correction draft, the system MUST preserve all active machinery, general-activity, and visit rows, plus applicable incident severity and source-discipline values.

### FR-004 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:90](../../specs/034-daily-lifecycle-lock/spec.md#L90) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-004**: The system MUST refuse a concurrent correction request with status 400 and the stable error code `correction_already_open`, without creating or changing a report version.

### FR-005 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:91](../../specs/034-daily-lifecycle-lock/spec.md#L91) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-005**: The system MUST offer authorized users a confirmed self-service cancellation action only for an open correction draft that is the current report and has a version number greater than one.

### FR-006 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:92](../../specs/034-daily-lifecycle-lock/spec.md#L92) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-006**: On a successful correction cancellation, the system MUST remove the temporary draft, restore the preceding approved version as current, and direct the user to that restored version.

### FR-007 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:93](../../specs/034-daily-lifecycle-lock/spec.md#L93) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-007**: The system MUST expose every version in a report lineage with version number, status, current state, lock state, modifier full name, correction reason, and formal approval timestamp.

### FR-008 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:94](../../specs/034-daily-lifecycle-lock/spec.md#L94) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-008**: The version-history experience MUST show the modifier, correction reason, and a readable Jalali approval date-and-time for each applicable version; absent values MUST be shown without inventing lineage information.

### FR-009 — W01

منبع: [specs/034-daily-lifecycle-lock/spec.md:95](../../specs/034-daily-lifecycle-lock/spec.md#L95) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-009**: The system MUST refuse submission from a state other than draft or rejected with the stable error code `report_not_in_submittable_state`.

### FR-010 — W01

منبع: [specs/034-daily-lifecycle-lock/spec.md:96](../../specs/034-daily-lifecycle-lock/spec.md#L96) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: The system MUST refuse a missing rejection reason with `rejection_reason_required` and a trimmed rejection reason shorter than 10 characters with `rejection_reason_min_length_10`; each outcome MUST provide its corresponding localized user message.

### FR-011 — D05

منبع: [specs/034-daily-lifecycle-lock/spec.md:97](../../specs/034-daily-lifecycle-lock/spec.md#L97) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-011**: The system MUST refuse submission when an activity is marked measured and has no quantity, using `quantity_unset_invalid` and the exact approved message: «مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود».

### FR-012 — D05

منبع: [specs/034-daily-lifecycle-lock/spec.md:98](../../specs/034-daily-lifecycle-lock/spec.md#L98) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-012**: The system MUST treat an explicitly recorded numeric zero as a valid quantity and MUST keep it distinct from an unset or not-measured quantity throughout editing, read-only reporting, and summary views.

### FR-013 — D05

منبع: [specs/034-daily-lifecycle-lock/spec.md:99](../../specs/034-daily-lifecycle-lock/spec.md#L99) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-013**: Every requested activity-table view MUST render an unset or not-measured quantity as the visually distinct muted warning label «ثبت‌نشده», rather than as numeric zero or a plain dash.

### FR-014 — Q03

منبع: [specs/034-daily-lifecycle-lock/spec.md:100](../../specs/034-daily-lifecycle-lock/spec.md#L100) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-014**: The delivered behavior MUST have automated coverage for correction-data preservation, concurrent-correction refusal, cancellation restoration, lineage metadata, lifecycle error contracts, measured-but-unset quantity validation, explicit zero acceptance, and the requested unset presentation.

### SC-001 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:115](../../specs/034-daily-lifecycle-lock/spec.md#L115) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: In an acceptance dataset containing every listed activity attribute and child-row type, 100% of active records and applicable values are preserved in a newly opened correction version.

### SC-002 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:116](../../specs/034-daily-lifecycle-lock/spec.md#L116) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: In 100% of tested cancellation flows, one confirmation returns the user to the preceding approved current version and leaves no temporary correction draft.

### SC-003 — W01

منبع: [specs/034-daily-lifecycle-lock/spec.md:117](../../specs/034-daily-lifecycle-lock/spec.md#L117) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: In 100% of tested invalid submit, reject, concurrent-correction, and measured-but-unset cases, the user receives the specified stable error code; the concurrent-correction response has status 400.

### SC-004 — D05

منبع: [specs/034-daily-lifecycle-lock/spec.md:118](../../specs/034-daily-lifecycle-lock/spec.md#L118) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: In every requested editable, read-only, and summary activity-table state, unset quantities display «ثبت‌نشده» and explicit zero quantities display a numeric zero, with no ambiguous substitution observed in acceptance checks.

### SC-005 — W02

منبع: [specs/034-daily-lifecycle-lock/spec.md:119](../../specs/034-daily-lifecycle-lock/spec.md#L119) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-005**: A reviewer can identify the modifier, correction reason, and approval date for each applicable version from one version-history view, without opening another report screen or consulting a separate audit record.


## specs/035-correction-lineage-cloning/spec.md

### FR-001 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:89](../../specs/035-correction-lineage-cloning/spec.md#L89) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-001**: The system MUST create a new sequential draft version when an authorized user submits a correction request for a current approved report with a justification reason of at least 10 characters.

### FR-002 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:90](../../specs/035-correction-lineage-cloning/spec.md#L90) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-002**: The system MUST copy 100% of active child rows and their domain attributes into the successor draft upon correction, specifically including:
  - Activities: contractor reference, crew name, foreman count, worker count, parcel, zone, block, floor, location detail, quantity, quantity measured flag, and unit.
  - Machinery: machinery type summaries, counts, operating hours, stoppage hours, and stoppage reason codes.
  - General activities: activity descriptions, shifts, and notes.
  - Site visits: visitor names, affiliations, purposes, and arrival/departure notes.
  - Incidents: incident descriptions, severity levels, source disciplines, injured counts, and actions taken.

### FR-003 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:96](../../specs/035-correction-lineage-cloning/spec.md#L96) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-003**: The system MUST NOT clone soft-deleted child rows into the successor draft.

### FR-004 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:97](../../specs/035-correction-lineage-cloning/spec.md#L97) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-004**: The system MUST reject any correction request on a lineage that already contains an active correction draft, returning a client validation error with error code `correction_already_open`.

### FR-005 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:98](../../specs/035-correction-lineage-cloning/spec.md#L98) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-005**: The system MUST provide an explicit "Cancel Correction" action on any draft report whose version number is greater than one.

### FR-006 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:99](../../specs/035-correction-lineage-cloning/spec.md#L99) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-006**: The system MUST require explicit user confirmation before cancelling an open correction, clearly stating that draft modifications will be lost and the prior approved version will be reinstated.

### FR-007 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:100](../../specs/035-correction-lineage-cloning/spec.md#L100) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-007**: Upon confirmed cancellation, the system MUST remove the in-progress correction draft, restore the immediately preceding approved version as the current active version, and navigate the user to the restored approved version.

### FR-008 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:101](../../specs/035-correction-lineage-cloning/spec.md#L101) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-008**: The system MUST NOT render or allow the correction cancellation action on initial draft reports (version 1) or on approved/locked reports.

### FR-009 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:102](../../specs/035-correction-lineage-cloning/spec.md#L102) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-009**: The system MUST provide an accessible version history listing for every daily report, presenting all versions in chronological order with version number, current/locked status, modifier name, version-bound correction reason, and approval timestamp.

### FR-010 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:103](../../specs/035-correction-lineage-cloning/spec.md#L103) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-010**: The system MUST display approval timestamps in the version history formatted in the localized calendar system (Persian Jalali format with date and time in Persian locale).

### FR-011 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:104](../../specs/035-correction-lineage-cloning/spec.md#L104) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-011**: The system MUST associate each correction justification reason strictly with the resulting correction version, ensuring the initial version (version 1) displays no correction reason.

### FR-012 — E09

منبع: [specs/035-correction-lineage-cloning/spec.md:105](../../specs/035-correction-lineage-cloning/spec.md#L105) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-012**: The system MUST enforce strict server-side authorization: only users with edit permissions on the specific project can initiate or cancel corrections, and cross-project operations MUST be rejected.

### SC-001 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:118](../../specs/035-correction-lineage-cloning/spec.md#L118) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: 100% of active child rows and specialized attributes (contractor, crew, headcounts, parcel, machinery summaries, visits, general tasks, incident severity) are preserved without data loss when generating a correction draft.

### SC-002 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:119](../../specs/035-correction-lineage-cloning/spec.md#L119) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: Zero duplicate correction drafts can be spawned for any report lineage while a correction draft is already open.

### SC-003 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:120](../../specs/035-correction-lineage-cloning/spec.md#L120) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: Authorized users can cancel an unwanted correction draft in 2 interactions (click trigger, confirm dialog) and have the prior approved report restored in under 2 seconds.

### SC-004 — W02

منبع: [specs/035-correction-lineage-cloning/spec.md:121](../../specs/035-correction-lineage-cloning/spec.md#L121) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: 100% of historical report versions in the version history view display complete provenance (modifier name, version-bound reason, localized approval timestamp).

### SC-005 — E09

منبع: [specs/035-correction-lineage-cloning/spec.md:122](../../specs/035-correction-lineage-cloning/spec.md#L122) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-005**: 100% of unauthorized, read-only, or cross-project correction and cancellation attempts are rejected server-side.


## specs/036-validation-codes-unset-semantics/spec.md

### FR-001 — W01

منبع: [specs/036-validation-codes-unset-semantics/spec.md:79](../../specs/036-validation-codes-unset-semantics/spec.md#L79) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-001**: The system MUST allow the existing submit workflow only when the report is in draft or rejected state.

### FR-002 — W01

منبع: [specs/036-validation-codes-unset-semantics/spec.md:80](../../specs/036-validation-codes-unset-semantics/spec.md#L80) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-002**: A submit attempt from any other state MUST be refused with the language-independent code `report_not_in_submittable_state`; the Persian feedback MUST be exactly `فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند`, and English feedback MUST communicate the same corrective meaning.

### FR-003 — W01

منبع: [specs/036-validation-codes-unset-semantics/spec.md:81](../../specs/036-validation-codes-unset-semantics/spec.md#L81) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-003**: A missing, null, empty, or whitespace-only rejection reason MUST be refused with the language-independent code `rejection_reason_required`; the Persian feedback MUST be exactly `دلیل رد الزامی است`, and English feedback MUST communicate the same corrective meaning.

### FR-004 — W01

منبع: [specs/036-validation-codes-unset-semantics/spec.md:82](../../specs/036-validation-codes-unset-semantics/spec.md#L82) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-004**: A non-empty rejection reason whose trimmed content is shorter than 10 characters MUST be refused with the language-independent code `rejection_reason_min_length_10`; the Persian feedback MUST be exactly `دلیل رد باید حداقل ۱۰ کاراکتر باشد`, and English feedback MUST communicate the same minimum.

### FR-005 — W01

منبع: [specs/036-validation-codes-unset-semantics/spec.md:83](../../specs/036-validation-codes-unset-semantics/spec.md#L83) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-005**: A rejection reason whose trimmed content contains at least 10 characters MUST satisfy the reason-length rule and allow the existing authorized rejection workflow to proceed.

### FR-006 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:84](../../specs/036-validation-codes-unset-semantics/spec.md#L84) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-006**: Submission MUST be refused when any activity is marked measured and its quantity is unset, using the language-independent code `quantity_unset_invalid` and the exact Persian feedback `مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود`; English feedback MUST communicate the same corrective instruction.

### FR-007 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:85](../../specs/036-validation-codes-unset-semantics/spec.md#L85) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-007**: An explicitly recorded numeric zero, including decimal representations such as `0.00`, MUST be accepted as a valid measured quantity and MUST NOT trigger `quantity_unset_invalid`.

### FR-008 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:86](../../specs/036-validation-codes-unset-semantics/spec.md#L86) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-008**: The system MUST preserve the semantic distinction between an explicitly recorded zero and an unset quantity throughout submission validation and every requested activity-quantity presentation.

### FR-009 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:87](../../specs/036-validation-codes-unset-semantics/spec.md#L87) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-009**: In the requested read-only activity-row views and daily-report activity summary, a null quantity MUST be rendered as the localized unset label rather than as a blank cell, plain dash, or numeric zero.

### FR-010 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:88](../../specs/036-validation-codes-unset-semantics/spec.md#L88) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: In the requested read-only activity-row views, an activity marked not measured MUST use the same localized unset presentation even if an inconsistent legacy row also contains a numeric quantity.

### FR-011 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:89](../../specs/036-validation-codes-unset-semantics/spec.md#L89) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-011**: An activity marked measured with an explicitly recorded zero MUST be rendered as numeric zero in every requested activity-row and summary view.

### FR-012 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:90](../../specs/036-validation-codes-unset-semantics/spec.md#L90) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-012**: The unset presentation MUST use the localized text `ثبت‌نشده` in Persian and `Unset` in English, compact text, a muted neutral background, and a clearly visible low-severity caution border.

### FR-013 — Q03

منبع: [specs/036-validation-codes-unset-semantics/spec.md:91](../../specs/036-validation-codes-unset-semantics/spec.md#L91) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-013**: Persian and English localization MUST cover `report_not_in_submittable_state`, `rejection_reason_required`, `rejection_reason_min_length_10`, `quantity_unset_invalid`, and the daily-report unset-quantity label.

### FR-014 — Q03

منبع: [specs/036-validation-codes-unset-semantics/spec.md:92](../../specs/036-validation-codes-unset-semantics/spec.md#L92) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-014**: Validation identifiers MUST remain stable and language-independent; changing locale MUST change only the user-facing message or label, not the code used to identify the outcome.

### FR-015 — Q03

منبع: [specs/036-validation-codes-unset-semantics/spec.md:93](../../specs/036-validation-codes-unset-semantics/spec.md#L93) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-015**: The specified invalid submit, missing-reason, short-reason, measured-but-unset, explicit-zero, and localized unset-display outcomes MUST have automated regression coverage.

### FR-016 — E09

منبع: [specs/036-validation-codes-unset-semantics/spec.md:94](../../specs/036-validation-codes-unset-semantics/spec.md#L94) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-016**: All behavior in this feature MUST remain within the existing project membership, report viewing, editing, submission, and approval authorization boundaries.

### SC-001 — W01

منبع: [specs/036-validation-codes-unset-semantics/spec.md:108](../../specs/036-validation-codes-unset-semantics/spec.md#L108) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: In 100% of acceptance cases covering non-submittable states, missing rejection reasons, and short rejection reasons, users receive the specified stable validation code and the correct locale-appropriate corrective message.

### SC-002 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:109](../../specs/036-validation-codes-unset-semantics/spec.md#L109) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: In 100% of acceptance cases, a measured activity with no quantity prevents submission with `quantity_unset_invalid`, while explicit `0` and `0.00` quantities pass this rule without being changed or misclassified.

### SC-003 — D05

منبع: [specs/036-validation-codes-unset-semantics/spec.md:110](../../specs/036-validation-codes-unset-semantics/spec.md#L110) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: Across every requested read-only activity-table and summary state in both Persian and English, 100% of null or not-measured quantities show the localized unset label and 100% of measured explicit-zero quantities show numeric zero.

### SC-004 — Q03

منبع: [specs/036-validation-codes-unset-semantics/spec.md:111](../../specs/036-validation-codes-unset-semantics/spec.md#L111) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: Automated regression checks cover all four stable validation codes, the 10-character rejection boundary, explicit-zero acceptance, measured-but-unset refusal, and both locale variants of the unset label.

### SC-005 — Q03

منبع: [specs/036-validation-codes-unset-semantics/spec.md:112](../../specs/036-validation-codes-unset-semantics/spec.md#L112) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-005**: During acceptance review, a reviewer can correctly distinguish unset, explicit-zero, and positive activity quantities on first inspection without opening an editor or consulting raw data.


## specs/037-daily-offline-sync/spec.md

### FR-001 — X01

منبع: [specs/037-daily-offline-sync/spec.md:104](../../specs/037-daily-offline-sync/spec.md#L104) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-001**: سیستم MUST ثبت محلی ایجاد، ویرایش و حذف مجاز را در صفحات فعلی شش واحد `buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security` برای بخش‌های ساخت‌یافته فعال و قابل ویرایش در پیکربندی مؤثر فراهم کند؛ فعالیت، نیروی انسانی، مصالح و هر بخش فعال فعلی مشمول‌اند. [US1, US2]

### FR-002 — X01

منبع: [specs/037-daily-offline-sync/spec.md:105](../../specs/037-daily-offline-sync/spec.md#L105) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-002**: منبع معتبر داده عملیاتی MUST گزارش واحد تخصصی باشد؛ draft جدید فقط برای واحد، پروژه و تاریخ مجاز است و هنگام اتصال با گزارش جاری تطبیق می‌یابد، نه ایجاد منبع موازی یا گزارش خام پروژه. [US1.4, US4.4, US6.3]

### FR-003 — X01

منبع: [specs/037-daily-offline-sync/spec.md:106](../../specs/037-daily-offline-sync/spec.md#L106) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-003**: هر ردیف جدید MUST `client_id` مستقل UUIDv4 پایدار، هر تغییر `operation_id` مستقل، و هر draft شناسه محلی گزارش مستقل داشته باشد. retry payload بدون تغییر همان `operation_id` را حفظ و اصلاح payload نامعتبر نسخه عملیات جدید با ارتباط به قبلی ایجاد می‌کند. [US1.2, US3.4, US5.3]

### FR-004 — X01

منبع: [specs/037-daily-offline-sync/spec.md:107](../../specs/037-daily-offline-sync/spec.md#L107) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-004**: ذخیره محلی MUST پیش از اعلام موفقیت پایدار باشد و همه محتوا، حذف‌ها، شناسه‌ها، وابستگی‌ها، خطاها و وضعیت‌ها را در refresh و restart همان پروفایل قابل بازیابی کند؛ شکست ذخیره ورودی را برای بازیابی نگه می‌دارد. [US1.3, US2.2]

### FR-005 — X01

منبع: [specs/037-daily-offline-sync/spec.md:108](../../specs/037-daily-offline-sync/spec.md#L108) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-005**: کاربر MUST draft محلی را در همان واحد باز، مشاهده و اصلاح کند؛ بارگذاری سرور یا بازسازی جدول تغییر محلی ذخیره‌شده را بی‌صدا جایگزین نمی‌کند. [US2.3–4]

### FR-006 — X01

منبع: [specs/037-daily-offline-sync/spec.md:109](../../specs/037-daily-offline-sync/spec.md#L109) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-006**: ردیف pending MUST ابر زرد و متن قابل دسترس داشته باشد؛ pending، syncing، synced، failed و conflict با متن و تعامل دسترس‌پذیر در فارسی و انگلیسی متمایز باشند. [US2.1, SC-07]

### FR-007 — X01

منبع: [specs/037-daily-offline-sync/spec.md:110](../../specs/037-daily-offline-sync/spec.md#L110) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-007**: با بازگشت اتصال و نشست معتبر، sync MUST خودکار آغاز شود و هر عملیات، از جمله POST collection با slash پایانی، بدون حذف خاموش منتقل یا با خطای مشخص محفوظ بماند. [US3.1–2]

### FR-008 — X01

منبع: [specs/037-daily-offline-sync/spec.md:111](../../specs/037-daily-offline-sync/spec.md#L111) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-008**: تأیید MUST به `operation_id` و هدف مربوط تطبیق‌پذیر باشد؛ `synced_ids` یعنی شناسه عملیات تأییدشده و نگاشت `client_id` به شناسه سرور قابل تشخیص است. نتیجه نامعتبر، مفقود یا نامرتبط باعث حذف عملیات تأییدنشده نمی‌شود و ترتیب پاسخ ملاک تطبیق نیست. [US3.3]

### FR-009 — X01

منبع: [specs/037-daily-offline-sync/spec.md:112](../../specs/037-daily-offline-sync/spec.md#L112) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-009**: نتیجه هر عملیات MUST موفق، خطای اعتبارسنجی، تعارض یا شکست قابل تلاش مجدد را متمایز کند؛ برای approved، کد پایدار `conflict_report_approved` و وضعیت قابل تشخیص `sync_conflict` مستقل از زبان ارائه شود. [US5.2, US6.1]

### FR-010 — X01

منبع: [specs/037-daily-offline-sync/spec.md:113](../../specs/037-daily-offline-sync/spec.md#L113) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-010**: قرارداد موجود `results/summary` و status `conflict` MUST برای مصرف‌کننده موجود سازگار بماند یا گذار نسخه‌دار صریح داشته باشد؛ تغییر خاموش ممنوع است. جزئیات گذار به plan واگذار می‌شود. [US3.3, US6.1]

### FR-011 — X01

منبع: [specs/037-daily-offline-sync/spec.md:114](../../specs/037-daily-offline-sync/spec.md#L114) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-011**: هر عملیات هدف‌دار MUST تماماً پذیرفته شود یا هیچ اثر کسب‌وکاری از آن باقی نماند؛ عملیات مستقل همان batch می‌توانند موفق شوند و وابسته‌ها پیش از موفقیت پیش‌نیاز ناقص اعمال یا موفق اعلام نمی‌شوند. [US3.5–6, US5.1]

### FR-012 — X01

منبع: [specs/037-daily-offline-sync/spec.md:115](../../specs/037-daily-offline-sync/spec.md#L115) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-012**: ارسال مجدد، بازیابی پس از commit، و sync همپوشان MUST اثر کسب‌وکاری، ردیف، نسخه یا contribution تکراری ایجاد نکنند و شناسه سرور، provenance و تاریخچه حفظ شوند. [US3.4, US7.5, US8.2–3]

### FR-013 — X01

منبع: [specs/037-daily-offline-sync/spec.md:116](../../specs/037-daily-offline-sync/spec.md#L116) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-013**: تغییر و حذف MUST فقط هدف صریح مجاز را تحت تأثیر قرار دهد؛ omission، snapshot خالی یا cache قدیمی مجوز جایگزینی یا حذف کل بخش نیست؛ تغییر مستقل دیگران محفوظ و تغییر همزمان همان هدف تعارض است. [US4.1–2]

### FR-014 — W03

منبع: [specs/037-daily-offline-sync/spec.md:117](../../specs/037-daily-offline-sync/spec.md#L117) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-014**: ردیف‌ها، totals، ساختارهای تجمیعی و provenance خلاصه پروژه MUST در تمام مسیرهای موجود، legacy و batch derived و غیرقابل تألیف باشند؛ درخواست مستقیم تغییر، شامل آرایه خالی، با `derived_readonly` رد شود. [US4.3]

### FR-015 — W04

منبع: [specs/037-daily-offline-sync/spec.md:118](../../specs/037-daily-offline-sync/spec.md#L118) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-015**: خلاصه پروژه MUST طبق قواعد موجود فقط از گزارش‌های جاری واجد شرایط همان پروژه و روز ساخته شود؛ گزارش‌های واحد `SUBMITTED` یا `APPROVED` واجد شرایط‌اند و draft، rejected، غیرجاری، تاریخ یا پروژه دیگر و draft محلی نیستند. بازسازی باید provenance، تاریخچه، ارجاعات پیوست و overrideهای مجاز را حفظ و از تکرار جلوگیری کند. [US4.4–5]

### FR-016 — W05

منبع: [specs/037-daily-offline-sync/spec.md:119](../../specs/037-daily-offline-sync/spec.md#L119) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-016**: تغییر متادیتای مجاز واحد و اطلاعات متعلق به خلاصه پروژه MUST فقط در محدوده مالکیت، اعتبارسنجی و گردش کار فعلی پشتیبانی شود؛ فهرست و حدود آن در تصمیم‌های دامنه زیر مشخص است و شامل derived نیست. [US1, US4, US7]

### FR-017 — X01

منبع: [specs/037-daily-offline-sync/spec.md:120](../../specs/037-daily-offline-sync/spec.md#L120) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-017**: submit، review، approve، reject و تصمیم رسمی ایجاد یا لغو اصلاحیه MUST به حالت معتبر و مجوز فعلی سرور نیاز داشته باشند و آفلاین یا ضمن sync انجام نشوند؛ کار محلی محفوظ بماند. [US6, US7]

### FR-018 — X01

منبع: [specs/037-daily-offline-sync/spec.md:121](../../specs/037-daily-offline-sync/spec.md#L121) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-018**: اعتبار وضعیت، نسخه جاری، عضویت پروژه و مجوز MUST در زمان ارسال و هنگام اعمال mutation سمت سرور بررسی شوند؛ cache مجوز به تنهایی کافی نیست. نتیجه رقابت MUST از داده و تاریخچه قفل‌شده حفاظت کند. [US6.1–4, US8.4]

### FR-019 — X01

منبع: [specs/037-daily-offline-sync/spec.md:122](../../specs/037-daily-offline-sync/spec.md#L122) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-019**: برخورد با نسخه قفل‌شده یا غیرجاری MUST تعارض صریح ایجاد کند و مقصد دیگری خودکار انتخاب نشود؛ انتقال به draft یا اصلاحیه مجاز نیازمند انتخاب آگاهانه و اعتبارسنجی سرور است. [US6, US7]

### FR-020 — X01

منبع: [specs/037-daily-offline-sync/spec.md:123](../../specs/037-daily-offline-sync/spec.md#L123) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-020**: خطا MUST به واحد، گزارش، بخش، ردیف، عملیات و فیلد قابل ردیابی و با کد پایدار و پیام دوزبانه پس از refresh باقی بماند. retry کاربر MUST فقط نسخه اصلاح‌شده هدف را ارسال و موفقیت را فقط پس از تأیید واقعی اعلام کند. [US5]

### FR-021 — X01

منبع: [specs/037-daily-offline-sync/spec.md:124](../../specs/037-daily-offline-sync/spec.md#L124) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-021**: رسیدگی تعارض MUST علت و نسخه‌های کامل هدر و ردیف‌های بخش مربوط را نمایش دهد؛ انتخاب سرور پس از تأیید فقط دامنه انتخاب‌شده را reconcile و عملیات کنارگذاشته‌شده را از ارسال مجدد خارج کند. [US7.1–2]

### FR-022 — X01

منبع: [specs/037-daily-offline-sync/spec.md:125](../../specs/037-daily-offline-sync/spec.md#L125) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-022**: حفظ کار محلی MUST مرور مقصد و مقادیر، استفاده از جریان رسمی اصلاح متناسب با مالکیت، حفظ lineage و دلیل، و نگهداری داده تا تأیید قابل تطبیق مقصد را تضمین کند؛ خطا، عدم مجوز یا قطعی موفقیت نیست. [US7.3–5]

### FR-023 — X01

منبع: [specs/037-daily-offline-sync/spec.md:126](../../specs/037-daily-offline-sync/spec.md#L126) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-023**: عملیات نیمه‌تمام MUST بعد از توقف مرورگر قابل بازیابی و retry باشد؛ قطعی، انقضا یا لغو مجوز داده را حذف نمی‌کند و ادامه فقط با مجوز معتبر انجام می‌شود. [US8.1–4]

### FR-024 — X01

منبع: [specs/037-daily-offline-sync/spec.md:127](../../specs/037-daily-offline-sync/spec.md#L127) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-024**: داده و صف محلی MUST به کاربر، پروژه و واحد درست محدود شوند؛ تغییر حساب نباید داده حساب قبلی را افشا یا با هویت جدید ارسال کند. [US8.5]

### FR-025 — X01

منبع: [specs/037-daily-offline-sync/spec.md:128](../../specs/037-daily-offline-sync/spec.md#L128) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-025**: داده محلی قدیمی MUST بدون پاکسازی اجباری حفظ و بررسی شود؛ فقط آیتم قابل تطبیق به مقصد مجاز هدایت و آیتم مبهم با همه داده‌ها برای تصمیم کاربر نگهداری می‌شود. [US8.6]

### FR-026 — X01

منبع: [specs/037-daily-offline-sync/spec.md:129](../../specs/037-daily-offline-sync/spec.md#L129) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-026**: حذف محلی MUST دامنه و پیامد روشن و تأیید صریح داشته باشد؛ پاک کردن cache یا کل صف روش رفع خطا یا ارتقا نیست. [Edge Cases]

### FR-027 — X01

منبع: [specs/037-daily-offline-sync/spec.md:130](../../specs/037-daily-offline-sync/spec.md#L130) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-027**: همه پیام‌ها، خطاها، بازیابی، retry و انتخاب تعارض MUST در فارسی و انگلیسی و با تعامل صفحه‌کلید و نام قابل دسترس عمل کنند؛ شناسه و کدها وابسته به زبان نباشند. [US2.1, US5.2, US7, SC-07]

### FR-028 — X01

منبع: [specs/037-daily-offline-sync/spec.md:131](../../specs/037-daily-offline-sync/spec.md#L131) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ سازگاری با A.1 الزامی

- **FR-028**: تحویل MUST شواهد مستقل مشخص‌شده در «الزامات اثبات» را ارائه کند؛ تست قدیمی، probe مشاهده نقص، وضعیت task و وجود زیرساخت به تنهایی اثبات پذیرش نیستند. [G13, SC-01–07]

### SC-01 — X01

منبع: [specs/037-daily-offline-sync/spec.md:155](../../specs/037-daily-offline-sync/spec.md#L155) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ سازگاری با A.1 الزامی

- **SC-01**: از ۱۰ عملیات مستقل معتبر، هر ۱۰ نتیجه دقیقاً تطبیق‌پذیر باشند؛ عملیات گم‌شده، تأیید کاذب، ردیف تکراری و حذف نامرتبط صفر است.

### SC-02 — X01

منبع: [specs/037-daily-offline-sync/spec.md:156](../../specs/037-daily-offline-sync/spec.md#L156) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ سازگاری با A.1 الزامی

- **SC-02**: پس از refresh و بستن/بازکردن مرورگر، ۱۰۰٪ داده ذخیره‌شده، شناسه‌ها و وضعیت‌های سناریوی پذیرش بازیابی شود.

### SC-03 — X01

منبع: [specs/037-daily-offline-sync/spec.md:157](../../specs/037-daily-offline-sync/spec.md#L157) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ سازگاری با A.1 الزامی

- **SC-03**: در ۹ معتبر و یک نامعتبر، هر ۹ موفق حفظ و همان ردیف نامعتبر پس از اصلاح بدون ارسال دوباره موفق‌ها ثبت شود.

### SC-04 — X01

منبع: [specs/037-daily-offline-sync/spec.md:158](../../specs/037-daily-offline-sync/spec.md#L158) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ سازگاری با A.1 الزامی

- **SC-04**: در تمام سناریوهای رقابت با تأیید، تغییر غیرمجاز وضعیت، داده قفل‌شده و تاریخچه صفر باشد.

### SC-05 — X01

منبع: [specs/037-daily-offline-sync/spec.md:159](../../specs/037-daily-offline-sync/spec.md#L159) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ سازگاری با A.1 الزامی

- **SC-05**: پس از انتخاب سرور، عملیات کنارگذاشته‌شده دوباره ظاهر یا ارسال نشود؛ در انتخاب اصلاحیه، داده محلی تا تأیید مقصد محفوظ بماند.

### SC-06 — X01

منبع: [specs/037-daily-offline-sync/spec.md:160](../../specs/037-daily-offline-sync/spec.md#L160) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ سازگاری با A.1 الزامی

- **SC-06**: در اختلال پیش و پس از ثبت سرور، هیچ عملیات برای همیشه غیرقابل retry نماند و اثر تکراری صفر باشد.

### SC-07 — X01

منبع: [specs/037-daily-offline-sync/spec.md:161](../../specs/037-daily-offline-sync/spec.md#L161) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ سازگاری با A.1 الزامی

- **SC-07**: مسیر ثبت، pending، اصلاح خطا و بازیابی تعارض از همان صفحات واحد به‌طور کامل در هر دو زبان قابل انجام باشد.


## specs/038-discipline-sub-reports/spec.md

### FR-001 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:156](../../specs/038-discipline-sub-reports/spec.md#L156) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-001**: The system MUST support entering a daily execution percentage (`execution_percentage` / `daily_percent`) on activity rows for all discipline sub-reports.

### FR-002 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:157](../../specs/038-discipline-sub-reports/spec.md#L157) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-002**: The system MUST enforce that `execution_percentage` is within the closed interval `[0.00, 100.00]`. Any value outside this range MUST be rejected with error code `percent_must_be_between_0_and_100`.

### FR-003 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:158](../../specs/038-discipline-sub-reports/spec.md#L158) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-003**: The system MUST allow `execution_percentage` to be null/empty, treating it as unmeasured progress without blocking physical quantity or description.

### FR-004 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:159](../../specs/038-discipline-sub-reports/spec.md#L159) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-004**: When submitting a sub-report (transitioning from `DRAFT` to `SUBMITTED`), the system MUST verify that the report contains at least one active row in activities, workforce, or materials.

### FR-005 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:160](../../specs/038-discipline-sub-reports/spec.md#L160) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-005**: If a sub-report contains zero active rows, the submission request MUST fail with HTTP status 400 and error code `cannot_submit_empty_sub_report`, leaving the report in `DRAFT` status and preventing daily summary rollup execution.

### FR-006 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:161](../../specs/038-discipline-sub-reports/spec.md#L161) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-006**: Sub-report submission rejection for empty content MUST return bilingual error messages ("امکان ارسال گزارش خالی وجود ندارد" / "Cannot submit an empty sub-report").

### FR-007 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:162](../../specs/038-discipline-sub-reports/spec.md#L162) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-007**: The system MUST provide discipline-specific UI layouts where civil-specific sections (concrete grades, slump test, batching) are hidden from the electrical (`electrical`) reporting panel.

### FR-008 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:163](../../specs/038-discipline-sub-reports/spec.md#L163) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-008**: The electrical reporting view MUST offer electrical-appropriate units of measurement (linear meter, point/outlet, panel unit, branch) in quick selectors.

### FR-009 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:164](../../specs/038-discipline-sub-reports/spec.md#L164) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-009**: The system MUST enable the consumable materials section for the `mechanical` unit, allowing mechanical and plumbing supervisors to record daily installed and consumed materials.

### FR-010 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:165](../../specs/038-discipline-sub-reports/spec.md#L165) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-010**: The mechanical materials interface MUST supply quick-selection items for high-frequency mechanical materials, including:
  - لوله ۵ لایه (5-layer composite pipe)
  - لوله پلیکا / فاضلابی (PVC pipe)
  - اتصالات جوشی (Welding fittings)
  - عایق الاستومری حرارتی و برودتی (Elastomeric insulation)
  - لوله گالوانیزه (Galvanized pipe)

### FR-011 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:171](../../specs/038-discipline-sub-reports/spec.md#L171) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-011**: The system MUST support recording hydrostatic and pressure test data on mechanical and plumbing activity rows, including:
  - Test performed toggle (`is_hydrostatic_tested`)
  - Test pressure in Bar (`test_pressure_bar`) with at least one decimal digit precision
  - Test duration / holding period
  - Test outcome (`PASSED`, `FAILED`)

### FR-012 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:176](../../specs/038-discipline-sub-reports/spec.md#L176) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-012**: When a sub-report containing a successful hydrostatic test (`PASSED`) is submitted, the system MUST create or link a Quality Inspection record in the quality management module (`risk.Inspection`) with reference to the sub-report, date, zone, and test pressure.

### FR-013 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:177](../../specs/038-discipline-sub-reports/spec.md#L177) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-013**: The system MUST reject any hydrostatic test record where the entered pressure is less than or equal to zero Bar with error code `invalid_test_pressure_value`.

### FR-014 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:178](../../specs/038-discipline-sub-reports/spec.md#L178) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-014**: When an activity row specifies a referenced subcontractor (`contractor_ref`), the system MUST compute the total crew person-hours as `(foreman_count + worker_count) * shift_duration_hours`.

### FR-015 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:179](../../specs/038-discipline-sub-reports/spec.md#L179) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-015**: Upon sub-report approval, computed subcontractor person-hours MUST be logged to the contractor daily labor ledger for billing and audit verification.

### FR-016 — D02

منبع: [specs/038-discipline-sub-reports/spec.md:180](../../specs/038-discipline-sub-reports/spec.md#L180) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-016**: The system MUST maintain the 6 canonical reporting units (`buildings`, `electrical`, `mechanical`, `machinery`, `warehouse`, `security`) as the primary architectural boundary.

### FR-017 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:181](../../specs/038-discipline-sub-reports/spec.md#L181) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **مرتبط؛ خارج از تحویل مستقیم A.1** · فاز: A.8؛ خروجی مرتبط A.1

- **FR-017**: The system MUST allow tagging activities and sub-reports with granular sub-disciplines:
  - Under `mechanical`: `MECHANICAL`, `PLUMBING`, `HVAC`
  - Under `buildings`: `CIVIL`, `FINISHING`

### FR-018 — D01

منبع: [specs/038-discipline-sub-reports/spec.md:184](../../specs/038-discipline-sub-reports/spec.md#L184) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-018**: All sub-report views and actions MUST be consistently discoverable and navigable from both the Project Overview / Daily Reports section and the Specialty Units navigation sidebar, ensuring no orphaned routes or disconnected components exist.

### FR-019 — Q03

منبع: [specs/038-discipline-sub-reports/spec.md:185](../../specs/038-discipline-sub-reports/spec.md#L185) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-019**: All user-visible validation errors, table headers, quick-pick labels, and status badges MUST be localized in Persian and English in compliance with the system Constitution.

### FR-020 — W03

منبع: [specs/038-discipline-sub-reports/spec.md:186](../../specs/038-discipline-sub-reports/spec.md#L186) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-020**: Sub-reports in `SUBMITTED` or `APPROVED` status MUST be immutable to standard edits; modifications MUST require reopening a tracked correction lineage per Feature 034 specifications.

---

### SC-001 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:218](../../specs/038-discipline-sub-reports/spec.md#L218) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ خروجی مرتبط A.1

- **SC-001**: 100% of activity row inputs with execution percentages outside `[0.00, 100.00]` are rejected at API and UI boundaries with error code `percent_must_be_between_0_and_100`.

### SC-002 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:219](../../specs/038-discipline-sub-reports/spec.md#L219) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ خروجی مرتبط A.1

- **SC-002**: 100% of attempts to submit an empty sub-report (zero activity, workforce, or material rows) are blocked with error code `cannot_submit_empty_sub_report`, achieving zero empty-report pollution in daily master summaries.

### SC-003 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:220](../../specs/038-discipline-sub-reports/spec.md#L220) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ خروجی مرتبط A.1

- **SC-003**: 100% of submitted sub-reports containing valid hydrostatic test certificates automatically link or generate a valid Quality Inspection entry in `risk.Inspection`.

### SC-004 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:221](../../specs/038-discipline-sub-reports/spec.md#L221) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ خروجی مرتبط A.1

- **SC-004**: Mechanical and plumbing supervisors can locate, select, and record standard plumbing materials (e.g. 5-layer pipe, PVC) in under 15 seconds using quick-pick suggestions.

### SC-005 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:222](../../specs/038-discipline-sub-reports/spec.md#L222) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ خروجی مرتبط A.1

- **SC-005**: 100% of activity rows associated with a subcontractor automatically yield verifiable person-hour labor records calculated from crew headcount and shift duration upon sub-report approval.

### SC-006 — X02

منبع: [specs/038-discipline-sub-reports/spec.md:223](../../specs/038-discipline-sub-reports/spec.md#L223) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.8؛ خروجی مرتبط A.1

- **SC-006**: Electrical supervisors report zero civil/concrete noise or extraneous fields when filling out the electrical daily report.

### SC-007 — D01

منبع: [specs/038-discipline-sub-reports/spec.md:224](../../specs/038-discipline-sub-reports/spec.md#L224) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-007**: 100% of sub-report authoring screens are reachable within 2 clicks from either the Project Reports menu or the Specialty Units workspace navigation.

### SC-008 — Q03

منبع: [specs/038-discipline-sub-reports/spec.md:225](../../specs/038-discipline-sub-reports/spec.md#L225) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-008**: All user-facing error messages, field labels, and action notifications maintain 100% Persian and English bilingual coverage.

---


## specs/039-auto-daily-rollup/spec.md

### FR-001 — H06

منبع: [specs/039-auto-daily-rollup/spec.md:179](../../specs/039-auto-daily-rollup/spec.md#L179) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-001**: System MUST return HTTP 200 OK with a newly initialized, valid draft daily report shell (`is_auto_summary=True`, `status="DRAFT"`) upon `GET /api/v1/projects/{project_pk}/daily-reports/by-date/?date={YYYY-MM-DD}&shift={1|2|3}` if no daily report currently exists for the requested project, date, and shift.

### FR-002 — H06

منبع: [specs/039-auto-daily-rollup/spec.md:180](../../specs/039-auto-daily-rollup/spec.md#L180) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-002**: System MUST permit users with standard read authorization (`view_reports`) to retrieve and view the auto-generated daily report shell via the by-date endpoint without requiring report creation or edit permissions.

### FR-003 — H04

منبع: [specs/039-auto-daily-rollup/spec.md:181](../../specs/039-auto-daily-rollup/spec.md#L181) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-003**: System MUST support the optional `shift` query parameter on `GET .../by-date/`, defaulting to `ReportShift.FULL` (or Shift 1 if multi-shift) when omitted.

### FR-004 — D01

منبع: [specs/039-auto-daily-rollup/spec.md:182](../../specs/039-auto-daily-rollup/spec.md#L182) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: وابستگی A.1 / عملیات A.8

- **FR-004**: System MUST reject direct creation of blank, unrolled daily reports via `POST /api/v1/projects/{project_pk}/daily-reports/` without sub-report payload, responding with HTTP 400 Bad Request and error code `auto_summary_only`.

### FR-005 — D06

منبع: [specs/039-auto-daily-rollup/spec.md:183](../../specs/039-auto-daily-rollup/spec.md#L183) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-005**: System MUST aggregate labor records into summary buckets using the composite key `(labor_category, resolved_job_title, contractor_ref)`.

### FR-006 — D06

منبع: [specs/039-auto-daily-rollup/spec.md:184](../../specs/039-auto-daily-rollup/spec.md#L184) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-006**: System MUST persist and expose `contractor_ref` and `contractor_name` on each `DailyReportLabor` record in the database model, serializer, and UI presentation, ensuring headcounts from different contractors are never merged into a single row.

### FR-007 — W03

منبع: [specs/039-auto-daily-rollup/spec.md:185](../../specs/039-auto-daily-rollup/spec.md#L185) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-007**: System MUST lock all derived child collections (activities, labor, materials, machinery, concrete) of daily reports having `is_auto_summary=True` against direct creation or deletion through child endpoints, returning HTTP 400 Bad Request with error code `derived_collection_read_only` and bilingual message: «این ردیف‌ها از ساب‌ریپورت‌های دیسیپلین مشتق شده‌اند؛ لطفاً از طریق ساب‌ریپورت مربوطه اقدام نمایید».

### FR-008 — W03

منبع: [specs/039-auto-daily-rollup/spec.md:186](../../specs/039-auto-daily-rollup/spec.md#L186) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-008**: Frontend UI MUST prevent manual row modification on auto-summary reports (`is_auto_summary=True`) within `DailyReportForm.tsx` and route `/projects/:projectId/daily-reports/:reportId/edit`, redirecting to `DailyReportSummaryView` or hiding "Add Row" and "Delete Row" actions.

### FR-009 — E11

منبع: [specs/039-auto-daily-rollup/spec.md:187](../../specs/039-auto-daily-rollup/spec.md#L187) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: پشتیبان A.1 / عملیات A.8

- **FR-009**: System MUST serialize the Project Activity Master Log (`/projects/:projectId/activity-log`) conforming to Shiraz Excel Sheet 1 (`ACTIVITY`) columns, explicitly including `source_discipline`, `parcel`, block, floor, location detail, activity description, shift, subcontractor, headcount, quantity, unit, and report view reference.

### FR-010 — E13

منبع: [specs/039-auto-daily-rollup/spec.md:188](../../specs/039-auto-daily-rollup/spec.md#L188) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: پشتیبان A.1 / عملیات A.8

- **FR-010**: System MUST provide multi-select filtering support by `source_discipline` and `parcel` on the Activity Master Log API endpoint and within the frontend filter bar component.

### FR-011 — E11

منبع: [specs/039-auto-daily-rollup/spec.md:189](../../specs/039-auto-daily-rollup/spec.md#L189) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: پشتیبان A.1 / عملیات A.8

- **FR-011**: System MUST invalidate and purge all cached responses for the project activity log immediately upon execution of `approve_report` on any daily report within that project.

### FR-012 — H02

منبع: [specs/039-auto-daily-rollup/spec.md:190](../../specs/039-auto-daily-rollup/spec.md#L190) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-012**: System MUST select the most severe weather condition among submitted discipline sub-reports using the hierarchy `clear < cloudy < rainy < snowy < stormy`.

### FR-013 — W05

منبع: [specs/039-auto-daily-rollup/spec.md:191](../../specs/039-auto-daily-rollup/spec.md#L191) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-013**: System MUST preserve site manager manual weather overrides (`weather_override=True`) across rollup recalculations, recording metadata `weather_source='overridden_by_manager'` and displaying an explanatory badge in the UI.

### FR-014 — D02

منبع: [specs/039-auto-daily-rollup/spec.md:192](../../specs/039-auto-daily-rollup/spec.md#L192) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-014**: Frontend UI MUST render an orange alert banner (`IncompletenessBanner`) enumerating missing discipline sub-reports when reporting for active disciplines is incomplete (`is_partial=True`).

### FR-015 — D02

منبع: [specs/039-auto-daily-rollup/spec.md:193](../../specs/039-auto-daily-rollup/spec.md#L193) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-015**: Frontend UI MUST render a green success banner with the message «تمام گزارش‌های دیسیپلین دریافت و تجمیع شدند» (All discipline reports received and aggregated) when all active discipline sub-reports have been received and incorporated (`is_partial=False` and `completeness.state === "complete"`).

### FR-016 — D02

منبع: [specs/039-auto-daily-rollup/spec.md:194](../../specs/039-auto-daily-rollup/spec.md#L194) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-016**: System MUST include a localized Persian date-time string `aggregated_at_jalali` in aggregation metadata alongside the UTC ISO timestamp `aggregated_at`.

### FR-017 — D11

منبع: [specs/039-auto-daily-rollup/spec.md:195](../../specs/039-auto-daily-rollup/spec.md#L195) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-017**: System MUST group and algebraically sum received and consumed quantities of identical materials within the materials summary projection.

### SC-001 — H06

منبع: [specs/039-auto-daily-rollup/spec.md:211](../../specs/039-auto-daily-rollup/spec.md#L211) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-001**: 100% of calendar date navigations to `/by-date/` successfully return a valid daily report shell within 2 seconds without ever throwing a 404 Not Found error, regardless of whether sub-reports existed beforehand.

### SC-002 — H06

منبع: [specs/039-auto-daily-rollup/spec.md:212](../../specs/039-auto-daily-rollup/spec.md#L212) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-002**: 100% of read-only users with project view authorization can inspect the daily report shell without needing manual administrator intervention or elevated write permissions.

### SC-003 — D06

منبع: [specs/039-auto-daily-rollup/spec.md:213](../../specs/039-auto-daily-rollup/spec.md#L213) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-003**: 100% of distinct subcontractors logging manpower under identical job titles remain separated in the daily labor report, with zero instances of unauthorized headcount flattening.

### SC-004 — W03

منبع: [specs/039-auto-daily-rollup/spec.md:214](../../specs/039-auto-daily-rollup/spec.md#L214) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-004**: 100% of manual POST/DELETE requests targeting derived collections on auto-summary reports are rejected with error code `derived_collection_read_only`.

### SC-005 — E11

منبع: [specs/039-auto-daily-rollup/spec.md:215](../../specs/039-auto-daily-rollup/spec.md#L215) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: پشتیبان A.1 / عملیات A.8

- **SC-005**: 100% of activities from newly approved daily reports are queryable and visible in the Activity Master Log within 1 second of approval, eliminating the previous 300-second cache delay.

### SC-006 — E13

منبع: [specs/039-auto-daily-rollup/spec.md:216](../../specs/039-auto-daily-rollup/spec.md#L216) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: پشتیبان A.1 / عملیات A.8

- **SC-006**: The Activity Master Log UI provides full filtering and display coverage for all 12 Shiraz Excel Sheet 1 columns, specifically including source discipline and site parcel.

### SC-007 — D02

منبع: [specs/039-auto-daily-rollup/spec.md:217](../../specs/039-auto-daily-rollup/spec.md#L217) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: وابستگی A.1 / عملیات A.8

- **SC-007**: When all active project disciplines have submitted their daily reports, 100% of inspected views display the green confirmation banner confirming complete rollup.

### SC-008 — W05

منبع: [specs/039-auto-daily-rollup/spec.md:218](../../specs/039-auto-daily-rollup/spec.md#L218) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-008**: 100% of manager manual weather overrides remain intact through subsequent sub-report submissions with verified `overridden_by_manager` metadata attribution.

---


## specs/044-shiraz-excel-parity-pdf/spec.md

### FR-001 — E01

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:179](../../specs/044-shiraz-excel-parity-pdf/spec.md#L179) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-001**: System MUST provide an authorized export endpoint (`GET /api/v1/projects/{project_pk}/daily-reports/{id}/excel/`) that returns a fully formatted Microsoft Excel spreadsheet (`.xlsx`) adhering to Shiraz template FILE 4.

### FR-002 — E01

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:180](../../specs/044-shiraz-excel-parity-pdf/spec.md#L180) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-002**: The FILE 4 Excel workbook MUST configure right-to-left worksheet orientation (`ws.sheet_view.rightToLeft = True`) and use Persian-compatible typography.

### FR-003 — H04

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:181](../../specs/044-shiraz-excel-parity-pdf/spec.md#L181) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-003**: The FILE 4 Excel header (Rows 1–8) MUST present project name, contract number, Jalali date, Persian day of the week, shifts 1–3 operating hours, workshop operational status (active/inactive with reason), and atmospheric weather conditions with minimum and maximum temperatures.

### FR-004 — D08

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:182](../../specs/044-shiraz-excel-parity-pdf/spec.md#L182) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-004**: The FILE 4 Excel Section A MUST populate all 34 standard Shiraz indirect/staff labor positions (from branch manager to guest) with recorded shift numbers, absence count, and an Excel native `=SUM(...)` subtotal formula row.

### FR-005 — D08

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:183](../../specs/044-shiraz-excel-parity-pdf/spec.md#L183) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-005**: The FILE 4 Excel Section B MUST populate all 32 standard Shiraz direct/craft labor positions with recorded counts, an Excel native `=SUM(...)` subtotal formula row, and a grand total manpower row summing Sections A and B using a native spreadsheet addition formula.

### FR-006 — E02

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:184](../../specs/044-shiraz-excel-parity-pdf/spec.md#L184) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-006**: The FILE 4 Excel workbook MUST include formatted tables for Incoming Materials (Section C), Concrete Casting Volumes (Section D), Machinery/Equipment status and operating hours (Section E), and Daily Executed Activities (Section F) with proper borders and alignments.

### FR-007 — E10

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:185](../../specs/044-shiraz-excel-parity-pdf/spec.md#L185) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: مرتبط با A.1؛ ورود داده در A.8

- **FR-007**: System MUST provide an authorized sub-report Excel export endpoint (`GET /api/v1/projects/{project_pk}/units/{unit}/daily-reports/{id}/excel/`) generating trade-specific spreadsheets for Civil (FILE 5) and Electrical (FILE 6).

### FR-008 — E10

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:186](../../specs/044-shiraz-excel-parity-pdf/spec.md#L186) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: مرتبط با A.1؛ ورود داده در A.8

- **FR-008**: The Civil sub-report Excel (FILE 5) MUST include columns for Row Number, Shift, Contractor/Crew Name, Master Craftsmen, Laborers, Parcel (`قطعه`), Block (`بلوک`), Floor (`طبقه`), Activity Description, Unit, Quantity, and Execution Percentage (`درصد اجرا`) formatted with spreadsheet percentage styling (`0.0%`).

### FR-009 — E10

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:187](../../specs/044-shiraz-excel-parity-pdf/spec.md#L187) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: مرتبط با A.1؛ ورود داده در A.8

- **FR-009**: The Electrical sub-report Excel (FILE 6) MUST include columns for Row Number, Shift, Crew Name, Master Craftsmen, Laborers, Block, Floor, Electrical Activity Description, Unit, and Quantity, and MUST NOT include parcel or execution percentage columns.

### FR-010 — E09

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:188](../../specs/044-shiraz-excel-parity-pdf/spec.md#L188) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-010**: System MUST enforce that both whole-site and sub-report Excel downloads require `view_reports` permission and verified project membership (`IsProjectMember`).

### FR-011 — E05

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:189](../../specs/044-shiraz-excel-parity-pdf/spec.md#L189) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-011**: System MUST set the HTTP `Content-Disposition` attachment filename for PDF downloads strictly to `daily-report-{report_date}-{shift}.pdf`.

### FR-012 — E06

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:190](../../specs/044-shiraz-excel-parity-pdf/spec.md#L190) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-012**: System MUST generate an unapproved daily report PDF (`draft`, `submitted`, `under_review`, `rejected`) with a prominent, semi-transparent diagonal watermark across each page stating "پیش‌نویس — غیرقابل استناد رسمی (DRAFT)".

### FR-013 — E06

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:191](../../specs/044-shiraz-excel-parity-pdf/spec.md#L191) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-013**: System MUST omit the draft watermark when generating a PDF for a daily report whose status is `approved`.

### FR-014 — E07

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:192](../../specs/044-shiraz-excel-parity-pdf/spec.md#L192) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-014**: The daily report PDF MUST include a formal three-tier signature section on its concluding page comprising three discrete boxes:
  1. "تنظیم‌کننده (سرپرست کارگاه)": submitter name, role, and submission timestamp.
  2. "بررسی‌کننده (دفتر فنی)": reviewer name, role, and review timestamp.
  3. "تأییدکننده (مدیر پروژه / ناظر مقیم)": approver name, role, approval timestamp, and cryptographic audit hash.

### FR-015 — E08

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:196](../../specs/044-shiraz-excel-parity-pdf/spec.md#L196) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-015**: System MUST compute a deterministic cryptographic Audit Hash (SHA-256 fingerprint) for each report based on immutable identifiers, date, shift, status, and approval lineage, printing the fingerprint in the approved PDF signature block.

### FR-016 — E12

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:197](../../specs/044-shiraz-excel-parity-pdf/spec.md#L197) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-016**: The frontend Daily Reports list page (`daily-reports-list.tsx`) MUST synchronize all filter controls (`date_from`, `date_to`, `status`, `discipline`, `contractor`, `block`) with the browser URL query string using `useSearchParams`.

### FR-017 — E13

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:198](../../specs/044-shiraz-excel-parity-pdf/spec.md#L198) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: پشتیبان A.1 / عملیات A.8

- **FR-017**: The frontend Project Activity Log (`project-activity-log.tsx`) MUST synchronize all multi-dimensional filters (`date_from`, `date_to`, `discipline`, `parcel`, `zone`, `block`, `subcontractor`, `page`) with the browser URL query string using `useSearchParams`.

### FR-018 — E11

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:199](../../specs/044-shiraz-excel-parity-pdf/spec.md#L199) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: پشتیبان A.1 / عملیات A.8

- **FR-018**: The Project Activity Log MUST provide an export action that downloads the full filtered activity dataset as a flat Excel spreadsheet matching Shiraz FILE 1 (ACTIVITY), retaining all applied filters.

### FR-019 — E14

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:200](../../specs/044-shiraz-excel-parity-pdf/spec.md#L200) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **ناقص** · فاز: پشتیبان A.1 / عملیات A.8

- **FR-019**: The Project Activity Log MUST display a prominent summary bar calculating total worker headcount (man-days) and aggregated physical quantities categorized by measurement unit for the filtered result set.

### FR-020 — Q04

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:201](../../specs/044-shiraz-excel-parity-pdf/spec.md#L201) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-020**: The system's decision tree in `docs/decision-tree/` MUST be updated with dedicated nodes for FILE 4 Excel download (`[export-report-excel]`), trade sub-report Excel download (`[export-sub-report-excel]`), updated official PDF specifications (`[export-report-pdf]`), and URL query persistence documentation (`filter-and-change-view`).

---

### SC-001 — E03

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:219](../../specs/044-shiraz-excel-parity-pdf/spec.md#L219) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-001**: 100% of exported master daily report spreadsheets (FILE 4) and sub-report spreadsheets (FILE 5/6) maintain native right-to-left (`RTL`) sheet orientation and render with zero formula evaluation errors (`#REF!`, `#VALUE!`, `#NAME?`) when opened in standard spreadsheet software.

### SC-002 — Q02

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:220](../../specs/044-shiraz-excel-parity-pdf/spec.md#L220) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-002**: Technical office users can export and download any master daily report spreadsheet (FILE 4) or official PDF for a typical site day (15–30 activities, 20 materials/equipment rows) in under 3.0 seconds over standard broadband.

### SC-003 — E07

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:221](../../specs/044-shiraz-excel-parity-pdf/spec.md#L221) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-003**: 100% of approved PDF reports contain valid three-tier digital signature blocks with verifiable audit hashes, and 100% of unapproved reports display the diagonal draft watermark.

### SC-004 — E13

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:222](../../specs/044-shiraz-excel-parity-pdf/spec.md#L222) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: پشتیبان A.1 / عملیات A.8

- **SC-004**: Any bookmarked or shared activity log URL reproduces 100% identical filter inputs, pagination state, and filtered record sets when opened by another authorized project member.

### SC-005 — E10

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:223](../../specs/044-shiraz-excel-parity-pdf/spec.md#L223) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: مرتبط با A.1؛ ورود داده در A.8

- **SC-005**: 100% of exported civil sub-reports (FILE 5) feature valid percentage formatting (`0.0%`) for execution percentages, while 100% of electrical sub-reports (FILE 6) omit parcel and percentage columns in full compliance with Shiraz standards.

### SC-006 — Q04

منبع: [specs/044-shiraz-excel-parity-pdf/spec.md:224](../../specs/044-shiraz-excel-parity-pdf/spec.md#L224) · نوع: مشخصات feature؛ الزام منبع، نه گواه تحویل

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-006**: System decision tree documentation in `docs/decision-tree/` accurately reflects 100% of newly added export actions, permission gates, and navigation pathways with zero broken reference links.

---


## reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md

### FR-DR-001 — H01

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:54](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L54) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-DR-001**: گزارش روزانه MUST پروژه، محل/جبهه کاری، تاریخ شمسی، شیفت، ثبت‌کننده و وضعیت آب‌وهوا را داشته باشد.

### FR-DR-002 — D04

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:55](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L55) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-DR-002**: بخش فعالیت‌ها MUST شامل WBS/فعالیت، شرح کار، مقدار انجام‌شده، واحد، محل، مسئول و عکس/مدرک باشد.

### FR-DR-003 — D06

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:56](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L56) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-DR-003**: بخش نیروی انسانی MUST تعداد افراد به تفکیک گروه یا پیمانکار، ساعات کار و غیبت را ثبت کند.

### FR-DR-004 — D09

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:57](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L57) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-DR-004**: بخش ماشین‌آلات MUST نوع/شناسه، ساعت کارکرد، توقف و علت توقف را بگیرد.

### FR-DR-005 — D12

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:58](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L58) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-DR-005**: بخش مصالح MUST مقدار ورودی، مصرف، برگشتی یا ضایعات را با واحد و محل مصرف نشان دهد.

### FR-DR-006 — D14

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:59](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L59) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: وابستگی A.1 / عملیات A.8

- **FR-DR-006**: حوادث، توقف کار، دستورهای کارگاهی و موانع MUST با مسئول پیگیری و موعد ثبت شوند.

### FR-DR-007 — W01

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:60](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L60) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-DR-007**: وضعیت‌ها MUST حداقل شامل پیش‌نویس، تأیید سرپرست و قفل مدیر/نقش تعیین‌شده باشند.

### FR-DR-008 — W02

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:61](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L61) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-DR-008**: اصلاح گزارش قفل‌شده MUST از مسیر درخواست اصلاح با دلیل و حفظ نسخه قبلی باشد.

### FR-DR-009 — W06

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:62](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L62) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-DR-009**: تاریخ گزارش، تاریخ ثبت و زمان تأیید MUST جدا نگهداری شوند.

### FR-DR-010 — D05

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:63](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L63) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **پیاده‌سازی موجود** · فاز: A.1

- **FR-DR-010**: برای فیلدهای اجباری، «ثبت‌نشده» MUST از «صفر» متمایز باشد.

### FR-DR-011 — Q03

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:64](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L64) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **ناقص** · فاز: A.1

- **FR-DR-011**: ثبت گزارش MUST روی موبایل و رایانه قابل انجام باشد و پیوست پشتیبانی شود.

### SC-DR-001 — Q01

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:76](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L76) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-DR-001**: گزارش روزانه قابل ثبت در موبایل/رایانه، دارای پیوست و گردش تأیید است.

### SC-DR-002 — Q01

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:77](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L77) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-DR-002**: جمع مصرف مصالح ثبت‌شده با موجودی قابل تطبیق است (در صورت وجود داده موجودی مرتبط).

### SC-DR-003 — Q01

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:78](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L78) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-DR-003**: در ۱۰۰٪ موارد، ویرایش مستقیم گزارش قفل‌شده بدون درخواست اصلاح ممکن نیست.

### SC-DR-004 — Q01

منبع: [reports_documentation/01-core-requirements-and-excel-blueprints/07-گزارش روزانه کارگاه.md:79](../../reports_documentation/01-core-requirements-and-excel-blueprints/07-%DA%AF%D8%B2%D8%A7%D8%B1%D8%B4%20%D8%B1%D9%88%D8%B2%D8%A7%D9%86%D9%87%20%DA%A9%D8%A7%D8%B1%DA%AF%D8%A7%D9%87.md#L79) · نوع: پیش‌نویس نیازمندی پایه روزانه

وضعیت گروه/معیار: **معیار پذیرش؛ تأیید کامل فعلی احراز نشده** · فاز: A.1

- **SC-DR-004**: کاربر می‌تواند گزارش معتبر را در کمتر از ۵ دقیقه برای یک شیفت معمولی ثبت کند.

