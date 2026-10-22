# Feature Specification: Daily Report Header and Weather Controls

**Feature Branch**: `N/A — no before_specify branch hook configured`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Apply the approved daily-report header, standardized weather, temperature validation, weather-impact notes, inactive-site reason, inactive-day activity warning, and date-based creation permission requirements from GAP-SPEC-01 while preserving the automatic full-day summary architecture."

**Source References**:
- `reports_gaps/01/GAP-SPEC-01-DAILY-HEADER-WEATHER.md`
- `reports_documentation/01-core-requirements-and-excel-blueprints/مستندات فرم‌های اکسل شیراز (Shiraz Excel Forms Documentation).md`
- `specs/028-auto-daily-report-summary/spec.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open the authorized full-day summary (Priority: P1)

An authorized project user opens a date and receives the single 24-hour project daily report assembled from specialty-unit reports. The report header represents the whole day, while shift detail remains on activity and personnel rows. A viewer can inspect an existing summary but cannot cause a new summary record to be created.

**Why this priority**: This preserves the approved source-of-truth and permission boundary. Any parallel blank-create flow or viewer-triggered creation would undermine the automatic summary model.

**Independent Test**: Open the same project/date as an editor and as a viewer, then attempt both the date-based create-or-open operation and direct blank creation. Verify that only the editor can cause the date summary shell to be created, direct blank creation remains unavailable, and the resulting header is full-day.

**Acceptance Scenarios**:

1. **Given** a project date has eligible specialty-unit reports and no project summary shell yet, **When** a user with report-edit permission requests that date through the date-based operation, **Then** exactly one full-day project summary is created or returned and populated through the approved aggregation flow.
2. **Given** a user has report-view permission but not report-edit permission, **When** the user requests an existing summary by date without creating data, **Then** the user can view it.
3. **Given** a user has report-view permission but not report-edit permission and no summary exists for the requested date, **When** the user invokes the creation-capable date-based operation, **Then** creation is denied and no report or child rows are persisted.
4. **Given** any authenticated user attempts direct blank project-report creation, **When** the request is submitted, **Then** it is rejected with status 400 and stable error code `auto_summary_only`.
5. **Given** a user visits the project daily-report list, **When** the page is displayed, **Then** no «گزارش جدید» / “New report” control or equivalent raw-create path is available.
6. **Given** a project daily report is displayed, **When** the user reviews the header and detail rows, **Then** the header indicates full-day coverage, activity rows use `shift_1`, `shift_2`, or `shift_3`, and personnel data uses the three shift-count columns rather than a header-level shift selector.

---

### User Story 2 - Record standardized weather and valid temperatures (Priority: P1)

An authorized editor records the daily weather using the five official Shiraz-form categories and, when known, minimum and maximum temperatures. Invalid weather values, physically out-of-policy temperatures, and reversed minimum/maximum values are stopped with field-specific guidance before the header is saved.

**Why this priority**: Weather and temperature are core header facts used in operational review, aggregation, and the official report. Inconsistent categories or invalid ranges make cross-day reporting unreliable.

**Independent Test**: Save one header for each allowed weather category, then try each retired category, both temperature boundaries, values just outside the boundaries, and a maximum below the minimum. Verify accepted and rejected outcomes and their field-specific error codes.

**Acceptance Scenarios**:

1. **Given** an editor is updating a project summary or an eligible specialty-unit report, **When** the editor selects `clear`, `cloudy`, `rainy`, `snowy`, or `stormy`, **Then** the value is accepted and shown with the correct localized label.
2. **Given** an editor or external client submits `sunny`, `partly_cloudy`, `foggy`, or any other nonstandard weather value as new input, **When** the record is validated, **Then** the value is rejected as unsupported.
3. **Given** historical data contains `sunny`, **When** the standardized weather set is introduced, **Then** the historical value is represented as `clear` without losing the associated report.
4. **Given** historical data contains `partly_cloudy` or `foggy`, **When** the standardized weather set is introduced, **Then** those records are normalized to `cloudy` and no retired weather value remains in stored or user-visible data.
5. **Given** either temperature is supplied within -40°C through +60°C inclusive, **When** the header is validated, **Then** the value is accepted.
6. **Given** either supplied temperature is below -40°C or above +60°C, **When** the header is validated, **Then** saving is blocked and the error is attached to the invalid temperature field.
7. **Given** both temperatures are supplied and `temp_max` is less than `temp_min`, **When** the header is validated, **Then** saving is blocked, the error is attached to `temp_max`, and the stable error code is `temp_max_must_be_gte_temp_min`.
8. **Given** valid weather values from multiple specialty-unit reports differ, **When** the project summary is reconciled without an explicit project-level override, **Then** the deterministic order `stormy` > `snowy` > `rainy` > `cloudy` > `clear` selects the summary weather.

---

### User Story 3 - Explain an inactive worksite (Priority: P1)

When an authorized editor marks the site inactive, the editor must select one standardized reason. The reason appears only when relevant, is retained on later views, and is understandable in Persian and English.

**Why this priority**: An inactive day without a reason is operationally ambiguous and weakens auditability, schedule analysis, and the usefulness of official reports.

**Independent Test**: Toggle the site between active and inactive, attempt to save without a reason, then save once for each allowed reason and reopen the report.

**Acceptance Scenarios**:

1. **Given** the site status is changed to inactive, **When** the header form updates, **Then** a required reason selector becomes visible with exactly `weather`, `holiday`, `strike_or_dispute`, `client_stop_order`, and `safety_incident` as choices.
2. **Given** the site status is inactive and no reason is selected, **When** the editor attempts to save, **Then** saving is blocked, the error is attached to `inactivity_reason`, and the stable error code is `inactivity_reason_required`.
3. **Given** the site status is inactive and an allowed reason is selected, **When** the report is saved and reopened, **Then** the reason remains selected and its localized label is displayed.
4. **Given** the site status changes from inactive to active, **When** the change is saved, **Then** the prior inactivity reason is cleared and is not presented as a reason for the active day.
5. **Given** a submitted inactivity reason is not one of the five allowed values, **When** the header is validated, **Then** saving is blocked with a field-specific validation response.

---

### User Story 4 - Preserve weather impact context in the official report (Priority: P2)

An authorized editor can add optional notes explaining how weather affected work. Reviewers can see the same text in the report details and in the official PDF, alongside any applicable inactive-site reason.

**Why this priority**: A weather label alone does not explain lost hours, disrupted work, or mitigations. The narrative must survive from entry through official output.

**Independent Test**: Save multilingual weather-impact text, reopen the report, produce the official PDF, and compare the displayed text and inactive reason with the saved header.

**Acceptance Scenarios**:

1. **Given** an editor leaves weather-impact notes empty, **When** a valid header is saved, **Then** saving succeeds because the notes are optional.
2. **Given** an editor enters weather-impact notes, **When** the header is saved and reopened, **Then** the text is preserved without silent truncation or loss of Persian/English characters.
3. **Given** weather-impact notes exist, **When** the official daily-report PDF is generated, **Then** the notes appear in a clearly labeled header-information row.
4. **Given** the site is inactive with a selected reason, **When** the official daily-report PDF is generated, **Then** the localized inactivity reason appears in the header information.

---

### User Story 5 - Confirm activity on an inactive day (Priority: P2)

If the site is marked inactive but a user adds or edits an execution activity whose quantity is greater than zero, the system asks for explicit confirmation before saving the activity.

**Why this priority**: The data may be legitimate, but it is an important contradiction that should be consciously acknowledged rather than silently recorded.

**Independent Test**: On an inactive report, create and edit rows with zero and positive quantities, then cancel and confirm the warning. Repeat on an active report to verify the warning boundary.

**Acceptance Scenarios**:

1. **Given** the site is inactive and an activity row to be created or edited has `quantity > 0`, **When** the user attempts to save it, **Then** a confirmation dialog displays «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت کارکرد اجرایی اطمینان دارید؟» before the mutation proceeds.
2. **Given** the warning is displayed, **When** the user cancels, **Then** the activity mutation is not persisted and the user can continue editing.
3. **Given** the warning is displayed, **When** the user confirms, **Then** the requested activity mutation proceeds through the normal validation and authorization rules.
4. **Given** the site is active or the activity quantity is zero, **When** the user saves the row, **Then** this inactive-site warning is not shown.
5. **Given** a positive-quantity row already exists on an inactive day, **When** the user edits and saves that row, **Then** confirmation is required again for that save attempt.

### Edge Cases

- One or both temperatures are omitted: each supplied value is range-checked; the maximum-versus-minimum rule applies only when both values are present.
- Temperatures exactly at -40°C or +60°C are valid.
- Decimal temperatures within the allowed range follow the report’s existing numeric precision and are compared numerically.
- A partial header update that changes only one temperature is validated against the other currently stored value.
- A historical retired weather value must be normalized before the allowed-value restriction takes effect, so existing reports remain readable.
- Conflicting specialty weather values use the approved severity order unless an authorized project-level override exists.
- Changing an inactive report to active removes a stale inactivity reason so exports and later reads cannot imply the site remained closed.
- The inactive-day activity confirmation is an acknowledgment, not a blanket prohibition; all existing activity validation and authorization rules still apply after confirmation.
- Two simultaneous date-based create attempts must still result in one logical full-day summary for the project/date.
- A denied viewer creation attempt must not leave a shell, audit side effect implying creation, or derived child rows.
- PDF generation with empty weather-impact notes must remain valid and must not display placeholder text as if it were user-entered content.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST maintain exactly one logical project daily summary per project and calendar date, and that summary MUST represent the full 24-hour day.
- **FR-002**: The project daily summary MUST remain derived from eligible specialty-unit reports; the project daily-report surface MUST NOT expose a manual blank-create action.
- **FR-003**: A direct project daily-report creation request MUST remain rejected with status 400 and stable error code `auto_summary_only`, regardless of the caller’s ability to edit reports.
- **FR-004**: A read-only date lookup MUST require report-view permission, while any date-based operation capable of creating the summary shell MUST require report-edit permission before any data is created.
- **FR-005**: Header-level shift selection MUST NOT be offered for a project daily summary; the header MUST display full-day coverage.
- **FR-006**: Shift detail MUST remain limited to `shift_1`, `shift_2`, and `shift_3` on execution-activity rows and to `shift_1_count`, `shift_2_count`, and `shift_3_count` on personnel rows.
- **FR-007**: Weather input and stored weather state for project daily summaries and specialty-unit reports MUST use exactly five values: `clear`, `cloudy`, `rainy`, `snowy`, and `stormy`.
- **FR-008**: User-facing weather labels MUST communicate `clear` as آفتابی / صاف, `cloudy` as ابری, `rainy` as بارانی, `snowy` as برفی, and `stormy` as طوفانی / گرد و غبار in Persian, with equivalent English labels in the English locale.
- **FR-009**: Newly submitted weather values outside the five-value set MUST be rejected; retired values MUST NOT remain available in selectors, contracts, aggregation rules, or acceptance tests.
- **FR-010**: Existing `sunny` data MUST normalize to `clear`; existing `partly_cloudy` and `foggy` data MUST normalize to `cloudy`; normalization MUST preserve the owning reports and all unrelated report data.
- **FR-011**: Weather reconciliation for the project summary MUST rank allowed values in descending severity as `stormy`, `snowy`, `rainy`, `cloudy`, then `clear`, unless an authorized project-level weather override is present.
- **FR-012**: Each supplied `temp_min` and `temp_max` value MUST be within -40°C through +60°C inclusive.
- **FR-013**: When both temperatures are known, `temp_max` MUST be greater than or equal to `temp_min`.
- **FR-014**: A violation of FR-013 MUST be reported on `temp_max` with stable error code `temp_max_must_be_gte_temp_min` and a clear localized recovery message.
- **FR-015**: Temperature range and cross-field rules MUST be enforced for every supported save path, and the interactive form MUST identify the invalid field before or when the user submits.
- **FR-016**: The project daily-report header MUST support optional `weather_impact_notes` and preserve entered Persian and English text across save, read, and subsequent update operations.
- **FR-017**: The official daily-report PDF MUST show non-empty weather-impact notes in a clearly labeled header-information row.
- **FR-018**: The system MUST support exactly five inactive-site reasons: `weather`, `holiday`, `strike_or_dispute`, `client_stop_order`, and `safety_incident`, each with localized labels.
- **FR-019**: When `site_status` is `inactive`, `inactivity_reason` MUST be present and valid; omission MUST be reported on `inactivity_reason` with stable error code `inactivity_reason_required`.
- **FR-020**: When `site_status` is active, the saved report MUST NOT retain or expose an inactive-site reason.
- **FR-021**: The header form MUST reveal and require the inactivity-reason selector when inactive is selected, and MUST hide it when the site is active.
- **FR-022**: The official daily-report PDF MUST show the localized inactivity reason whenever the site is inactive.
- **FR-023**: Creating or editing an activity with `quantity > 0` while the report is inactive MUST require an explicit user confirmation displaying the approved Persian warning text before the mutation proceeds.
- **FR-024**: Cancelling the inactive-day activity warning MUST leave persisted activity data unchanged; confirming MUST resume the normal save flow without bypassing any validation or authorization rule.
- **FR-025**: The inactive-day activity warning MUST NOT appear for an active site or for an activity whose quantity is zero.
- **FR-026**: All new labels, allowed-value descriptions, validation messages, and recovery guidance MUST be available in Persian and English without translating stable machine-readable values or error codes.
- **FR-027**: Existing project-level weather or site-status overrides MUST remain intact across automatic summary rebuilds, provided their values satisfy the standardized rules.

### Interface Compatibility Constraints

- The existing date-based daily-report operation (`/daily-reports/by-date/`) remains the only operation allowed to create the project summary shell, and its creation-capable request requires `edit_reports`.
- The existing direct collection creation operation (`POST /daily-reports/`) remains blocked with `400 auto_summary_only`.
- Existing consumers may continue to rely on the stable validation codes `temp_max_must_be_gte_temp_min` and `inactivity_reason_required`.

### Key Entities *(include if feature involves data)*

- **Project Daily Report**: The single project/date, full-day summary derived from eligible specialty-unit reports. Holds project-level weather and site-status overrides, temperature bounds, weather-impact notes, and an optional inactive-site reason that becomes mandatory when inactive.
- **Specialty-Unit Report**: A unit-authored source report contributing to the project summary. Its weather value uses the same five-category vocabulary.
- **Weather Condition**: One of five language-independent values (`clear`, `cloudy`, `rainy`, `snowy`, `stormy`) with localized labels and an approved severity order for reconciliation.
- **Temperature Range**: Optional minimum and maximum Celsius values, each bounded inclusively from -40 to +60, with the maximum not lower than the minimum when both are present.
- **Inactive-Site Reason**: One of five standardized explanations linked to an inactive project daily report; absent for active reports.
- **Weather Impact Notes**: Optional project-level narrative explaining operational effects of the day’s weather and carried into the official report.
- **Execution Activity**: A shift-specific work row whose positive quantity on an inactive day triggers explicit confirmation before creation or update.

### Scope Boundaries

**In scope**:
- Full-day header behavior and preservation of row-level shift detail.
- Standardization and historical normalization of weather values.
- Temperature bounds and cross-field validation.
- Weather-impact notes and inactive-site reasons through data entry, readback, and official PDF output.
- Client confirmation for positive execution activity on an inactive day.
- Permission separation between date lookup and creation-capable date access.
- Regression protection for automatic aggregation and blocked raw creation.

**Out of scope**:
- Reintroducing manual project daily-report creation.
- Creating separate project summary records per shift.
- Adding a weather forecast provider or automatically importing weather observations.
- Preventing all activity on an inactive day at the server level; this feature requires warning and acknowledgment, not prohibition.
- Redesigning specialty-unit authoring flows beyond the shared weather vocabulary.
- Changing the approved aggregation eligibility or approval lifecycle defined by the automatic-summary feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across a test matrix covering project summaries and specialty-unit reports, 100% of the five approved weather values are accepted and 100% of retired or unknown values are unavailable for new entry and rejected if submitted directly.
- **SC-002**: After historical normalization, 100% of sampled reports with `sunny`, `partly_cloudy`, or `foggy` remain accessible, preserve unrelated data, and contain only an approved weather value.
- **SC-003**: In boundary testing, -40°C and +60°C are accepted, values immediately outside the range are rejected, and every maximum-below-minimum case reports `temp_max_must_be_gte_temp_min` on the maximum field.
- **SC-004**: In inactive-site testing, all five approved reasons can be saved, and 100% of attempts to save an inactive report without a reason are blocked with `inactivity_reason_required`.
- **SC-005**: In document comparison tests, 100% of generated PDFs for reports with weather-impact notes reproduce the saved notes, and 100% of inactive-report PDFs show the selected localized reason.
- **SC-006**: In interaction testing, every create or edit attempt for a positive-quantity activity on an inactive day displays the approved warning before persistence; cancellation produces zero persisted changes.
- **SC-007**: In authorization testing, a view-only user can read an existing date summary but cannot create one; 100% of denied creation attempts leave no new summary or derived child data.
- **SC-008**: In raw-create regression testing, 100% of direct blank project-report creation attempts return status 400 with `auto_summary_only`, and the project daily-report page exposes zero raw-create controls.
- **SC-009**: In usability checks, at least 90% of representative Persian and English users can correct an invalid temperature or missing inactivity reason on the first retry using the field-level guidance.
- **SC-010**: For every project/date exercised under concurrent or repeated date access, users observe one logical full-day summary and no shift-specific duplicate headers.

## Assumptions

- `temp_min` and `temp_max` remain optional; range validation applies to either supplied value, and ordering validation applies when both current values are known.
- `partly_cloudy` and `foggy` normalize to `cloudy` as the closest approved category; `sunny` normalizes to `clear` as explicitly approved.
- A project-level weather or site-status override remains the authoritative header value during automatic rebuilds, consistent with the existing summary behavior.
- Clearing `inactivity_reason` when the site becomes active is preferable to retaining hidden stale data because the reason no longer describes the saved status.
- The inactive-day activity warning is intentionally confirmatory. It does not grant additional permission and does not waive quantity, project-scope, or other activity validation.
- Existing localization, permission, PDF, and audit mechanisms remain the shared delivery paths; this feature extends their behavior rather than introducing parallel mechanisms.
- Eligible specialty-unit reports, summary rebuild timing, and project-level approval behavior remain governed by the approved automatic-summary specification.

## Dependencies

- The automatic project daily-report summary behavior defined in `specs/028-auto-daily-report-summary/spec.md` is present and remains the architectural baseline.
- Existing project permissions distinguish report viewing from report editing.
- Official daily-report PDF generation and the shared report-header/activity entry surfaces remain available for extension.
- Historical weather data can be enumerated and normalized before the retired values are disallowed.
