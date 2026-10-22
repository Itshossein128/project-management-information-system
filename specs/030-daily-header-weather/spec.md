# Feature Specification: Standardized Daily Weather and Temperature

**Feature Branch**: `N/A — no before_specify branch hook configured`

**Created**: 2026-10-22

**Status**: Draft

**Input**: User description: "Standardize the 24-hour daily-report header to five approved weather conditions, validate minimum and maximum temperatures, and preserve weather-impact notes in report details and the official PDF."

**Source References**:
- `reports_gaps/01/speckit-specify-prompts/02-PROMPT-MODULAR-WEATHER-TEMPERATURE.md`
- `reports_gaps/01/GAP-SPEC-01-DAILY-HEADER-WEATHER.md`
- `reports_documentation/01-core-requirements-and-excel-blueprints/مستندات فرم‌های اکسل شیراز (Shiraz Excel Forms Documentation).md`
- `specs/028-auto-daily-report-summary/spec.md`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Record one of five standard weather conditions (Priority: P1)

An authorized report editor records the weather for the project's comprehensive 24-hour daily report using the five official Shiraz-form categories. Reviewers see the same standardized value everywhere the daily report is displayed or summarized.

**Why this priority**: A single weather vocabulary is required for reliable daily summaries, historical comparison, and official documentation.

**Independent Test**: Save and reopen one report for each approved weather value, try every retired and unknown value, inspect the available header choices, and reconcile reports with different weather severities.

**Acceptance Scenarios**:

1. **Given** an editor is updating a daily-report header, **When** the editor selects `clear`, `cloudy`, `rainy`, `snowy`, or `stormy`, **Then** the selected value is accepted and displayed with its localized label.
2. **Given** an editor opens the weather selector, **When** all choices are displayed, **Then** exactly the five approved values are available and `sunny`, `partly_cloudy`, and `foggy` are absent.
3. **Given** a new save request contains a retired or unknown weather value, **When** the report is validated, **Then** saving is rejected with a field-specific unsupported-value error.
4. **Given** a historical report contains `sunny`, **When** the standardized vocabulary is introduced, **Then** its weather is converted to `clear` while the report and all unrelated data remain intact.
5. **Given** a historical report contains `partly_cloudy` or `foggy`, **When** the standardized vocabulary is introduced, **Then** its weather is converted to `cloudy` while the report and all unrelated data remain intact.
6. **Given** contributing weather observations contain multiple approved values and no project-level override applies, **When** the daily summary weather is calculated, **Then** the most severe value is selected using `stormy` > `snowy` > `rainy` > `cloudy` > `clear`.

---

### User Story 2 - Enter valid minimum and maximum temperatures (Priority: P1)

An authorized report editor can enter optional minimum and maximum temperatures in Celsius. The header immediately identifies out-of-range or reversed values and prevents invalid data from being saved.

**Why this priority**: Temperature values affect the credibility of the official daily record and must remain physically plausible and internally consistent.

**Independent Test**: Enter each boundary, values immediately outside each boundary, a maximum below the minimum, equal minimum and maximum values, and a partial update that changes only one temperature.

**Acceptance Scenarios**:

1. **Given** either temperature is entered from -40°C through +60°C inclusive, **When** the header is validated, **Then** the value is accepted.
2. **Given** either temperature is below -40°C or above +60°C, **When** the editor enters or submits the value, **Then** the invalid field is identified and saving is blocked.
3. **Given** both temperatures are known and `temp_max` is lower than `temp_min`, **When** the header is validated, **Then** saving is blocked, the error is attached to `temp_max`, and the stable error code is `temp_max_must_be_gte_temp_min`.
4. **Given** `temp_max` equals `temp_min`, **When** the header is validated, **Then** saving is allowed.
5. **Given** one or both temperatures are omitted, **When** all supplied values are valid, **Then** the header can be saved because temperatures remain optional.
6. **Given** an editor changes only one temperature on an existing report, **When** the header is validated, **Then** the changed value is checked against the other stored temperature before saving.

---

### User Story 3 - Preserve weather impacts in the official record (Priority: P2)

An authorized report editor can record optional notes describing how adverse weather affected work fronts, productivity, delays, mitigation, or contractual claims. Reviewers see the same narrative in the report details and the official PDF.

**Why this priority**: A weather category alone cannot document operational or contractual impact; the explanatory narrative must survive into the formal record.

**Independent Test**: Save multi-line Persian and English notes, reopen the report, inspect both header and detail views, and compare the generated PDF with the saved text. Repeat with an empty note.

**Acceptance Scenarios**:

1. **Given** an editor leaves weather-impact notes empty, **When** an otherwise valid header is saved, **Then** saving succeeds because the notes are optional.
2. **Given** an editor enters Persian, English, or mixed-language weather-impact notes, **When** the report is saved and reopened, **Then** the complete text remains available in both header and detail views without silent truncation or character loss.
3. **Given** weather-impact notes were saved, **When** the official daily-report PDF is generated, **Then** the row labeled «توضیحات و اثرات شرایط جوی» contains the same text.
4. **Given** weather-impact notes are empty, **When** the official daily-report PDF is generated, **Then** the labeled row remains present with an empty value and no fabricated placeholder content.

### Edge Cases

- Temperatures exactly at -40°C and +60°C are valid; values immediately outside either boundary are invalid.
- Decimal temperatures within the existing supported precision are compared numerically rather than lexically.
- The maximum-versus-minimum rule applies only when both current values are known, including when one value comes from the stored report during a partial update.
- Historical weather normalization occurs before retired values are disallowed, preventing existing reports from becoming unreadable.
- A project-level weather override that already uses an approved value remains authoritative under the existing daily-summary rules.
- An empty weather value remains governed by the report's existing optionality rules; this feature standardizes non-empty values and does not make weather mandatory.
- Weather-impact notes may contain line breaks and Persian/English characters; output must remain readable in the report and PDF.
- A PDF with empty notes must still be generated successfully and must retain the labeled documentation row.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The comprehensive daily report MUST use exactly five non-empty weather values: `clear`, `cloudy`, `rainy`, `snowy`, and `stormy`.
- **FR-002**: User-facing labels MUST communicate `clear` as آفتابی / صاف, `cloudy` as ابری, `rainy` as بارانی, `snowy` as برفی, and `stormy` as طوفانی / گرد و غبار in Persian, with equivalent labels in English.
- **FR-003**: Retired values `sunny`, `partly_cloudy`, and `foggy` MUST NOT be offered for new entry or accepted in new saves.
- **FR-004**: Existing `sunny` values MUST be normalized to `clear` without deleting the owning report or changing unrelated report data.
- **FR-005**: Existing `partly_cloudy` and `foggy` values MUST be normalized to `cloudy` without deleting the owning report or changing unrelated report data.
- **FR-006**: When daily-summary weather is derived from multiple contributing approved values and no explicit project-level override applies, the system MUST select the most severe value using this descending order: `stormy`, `snowy`, `rainy`, `cloudy`, `clear`.
- **FR-007**: All daily-report input, stored-data, readback, summary, and user-interface representations of non-empty weather MUST share the same five-value vocabulary.
- **FR-008**: `temp_min` and `temp_max` MUST remain optional Celsius values, and each supplied value MUST be within -40°C through +60°C inclusive.
- **FR-009**: When both current temperatures are known, `temp_max` MUST be greater than or equal to `temp_min`.
- **FR-010**: A violation of FR-009 MUST be reported on `temp_max` with the stable error code `temp_max_must_be_gte_temp_min` and clear localized recovery guidance.
- **FR-011**: Temperature bounds and ordering rules MUST be enforced for every supported create, full-update, and partial-update path so that bypassing the interactive header cannot persist invalid temperatures.
- **FR-012**: The interactive header MUST constrain each temperature input to the inclusive -40°C to +60°C range and MUST provide immediate, field-specific feedback for an out-of-range value or a maximum below the minimum before an invalid save completes.
- **FR-013**: The daily report MUST support optional `weather_impact_notes` for operational and contractual weather impacts.
- **FR-014**: Authorized editors MUST be able to enter and edit `weather_impact_notes` through a multi-line control in the daily-report header.
- **FR-015**: Saved `weather_impact_notes` MUST be returned consistently in both header and detailed report views and MUST preserve Persian, English, mixed-language, and multi-line content.
- **FR-016**: The official daily-report PDF MUST contain a header-table row labeled «توضیحات و اثرات شرایط جوی» and MUST reproduce the saved note exactly when present.
- **FR-017**: All new user-facing weather labels and validation guidance MUST be available in Persian and English, while stable weather values, field names, and error codes remain language-independent.

### Interface Compatibility Constraints

- Consumers may rely on the stable field names `temp_min`, `temp_max`, and `weather_impact_notes`.
- Consumers may rely on `temp_max_must_be_gte_temp_min` being attached to `temp_max` when the maximum is below the minimum.
- The existing comprehensive 24-hour daily-report and automatic-summary architecture remains unchanged except for the weather vocabulary, temperature rules, weather-impact note, and resulting PDF content defined here.

### Key Entities *(include if feature involves data)*

- **Daily Report**: The comprehensive 24-hour project record whose header holds the selected or aggregated weather condition, optional temperature values, and optional weather-impact notes.
- **Weather Condition**: One of five language-independent values with localized labels and a deterministic severity rank for summary calculation.
- **Temperature Range**: Optional minimum and maximum Celsius values, each inclusively bounded from -40 to +60, with the maximum not lower than the minimum when both are known.
- **Weather Impact Notes**: Optional multi-line narrative describing weather effects on work fronts, delays, mitigation, productivity, or contractual claims and reproduced in the official report.

### Scope Boundaries

**In scope**:
- The five-value daily-report weather vocabulary, localized labels, legacy normalization, and deterministic severity ranking.
- Minimum and maximum temperature bounds, cross-field validation, partial-update behavior, and immediate header feedback.
- Optional weather-impact notes across header entry, report readback, detail display, and official PDF output.
- Regression protection for the existing 24-hour automatic daily-summary flow where it consumes or preserves weather data.

**Out of scope**:
- Adding weather forecasts, external weather providers, or automatic meteorological data import.
- Changing site active/inactive rules, inactivity reasons, inactive-day activity warnings, or permissions for creating daily reports.
- Changing shift structure, specialty-report approval eligibility, or the broader automatic-summary lifecycle.
- Redesigning unrelated PDF sections or other daily-report header fields.
- Introducing new weather metrics such as humidity, wind speed, precipitation volume, or air quality.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Across a complete weather-value test matrix, 100% of the five approved values are available and accepted, while 100% of retired or unknown values are unavailable for selection and rejected when directly submitted.
- **SC-002**: After historical normalization, 100% of sampled reports containing `sunny`, `partly_cloudy`, or `foggy` remain accessible, preserve unrelated data, and contain only an approved weather value.
- **SC-003**: For every tested combination of approved contributing conditions, the displayed daily-summary weather matches the documented five-level severity order.
- **SC-004**: In temperature boundary testing, -40°C and +60°C are accepted, values immediately outside the range are rejected, and 100% of maximum-below-minimum cases identify `temp_max` with code `temp_max_must_be_gte_temp_min`.
- **SC-005**: In interactive testing, 100% of invalid temperature entries are identified at the relevant field before an invalid header save completes, while valid boundary and equal-temperature cases save successfully.
- **SC-006**: For every tested report with weather-impact notes, the complete saved text is visible after reopening and is reproduced in the official PDF; reports without notes still generate a valid PDF with the labeled row and no invented content.
- **SC-007**: At least 90% of representative Persian- and English-language editors can select weather, enter valid temperatures, correct one invalid temperature, and record weather-impact notes on the first attempt without external assistance.

## Assumptions

- `temp_min`, `temp_max`, and `weather_impact_notes` remain optional because this request defines validation and documentation behavior but does not make them mandatory.
- `partly_cloudy` and `foggy` normalize to `cloudy` as the closest approved data-preserving category; `sunny` normalizes to `clear` as explicitly required.
- Existing approved project-level weather overrides continue to take precedence during automatic summary rebuilds.
- Weather-impact notes are plain multi-line text. No new business-specific character limit or rich-text formatting requirement is introduced.
- Existing authorization, audit, localization, report retrieval, and PDF-generation behavior remains in force; this feature changes only the scoped weather and temperature data.

## Dependencies

- The existing comprehensive 24-hour daily-report header and official PDF output remain available for extension.
- The automatic daily-summary flow can expose and reconcile the weather values contributed to a project/date.
- Historical weather records can be normalized before retired values are rejected.
- Existing Persian and English localization paths can provide the new labels and validation guidance.
