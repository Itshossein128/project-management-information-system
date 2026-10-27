# Feature Specification: Daily Report Validation Codes and Unset Semantics

**Feature Branch**: `036-validation-codes-unset-semantics`

**Created**: 2026-10-27

**Status**: Draft

**Input**: User description: "Standardize daily-report workflow validation codes and make an unset activity quantity visibly distinct from an explicitly recorded zero, as required by US-DR-11 and US-DR-14."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Submit Only Complete Measured Quantities (Priority: P1)

As a report author, I need submission to stop when a measured activity has no recorded quantity, while accepting an explicitly recorded zero, so that reviewers can trust the difference between “not entered” and “no work performed.”

**Why this priority**: Treating an unknown quantity as zero hides incomplete operational data, while rejecting a legitimate zero prevents an accurate report from progressing through approval.

**Independent Test**: Prepare otherwise-valid draft reports containing, in turn, a measured activity with no quantity, a measured activity with `0.00`, and a measured activity with a positive quantity; submit each report and verify that only the unset case is refused with the approved code and message.

**Acceptance Scenarios**:

1. **Given** an otherwise-valid draft or rejected report contains an activity marked as measured with no quantity, **When** an authorized author submits it, **Then** submission is refused with the stable code `quantity_unset_invalid` and, in Persian locale, the exact message `مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود`.
2. **Given** an otherwise-valid draft or rejected report contains an activity marked as measured with an explicitly recorded quantity of `0` or `0.00`, **When** an authorized author submits it, **Then** that quantity passes this validation and remains recorded as numeric zero.
3. **Given** multiple activity rows contain quantities, **When** submission validation runs, **Then** every measured row is checked and any measured-but-unset row prevents submission without changing explicit zero values.

---

### User Story 2 - Receive Stable Workflow Validation Feedback (Priority: P1)

As a report author or reviewer, I need invalid submit and reject actions to return stable, specific validation codes with localized explanations, so that I can understand and correct the exact workflow problem without relying on ambiguous generic text.

**Why this priority**: Submission and rejection are control points in the report lifecycle. Ambiguous errors slow operational work and make client behavior unreliable across Persian and English experiences.

**Independent Test**: Attempt to submit a report from each non-submittable state, reject without a reason, reject with whitespace only, reject with a trimmed reason shorter than 10 characters, and reject with a valid reason; verify the distinct outcomes and that the valid rejection proceeds.

**Acceptance Scenarios**:

1. **Given** a report is in a state other than draft or rejected, **When** an authorized user attempts to submit it, **Then** the action is refused with code `report_not_in_submittable_state` and, in Persian locale, the exact message `فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند`.
2. **Given** a submitted or under-review report, **When** an authorized reviewer rejects it without a reason or with a whitespace-only reason, **Then** the action is refused with code `rejection_reason_required` and, in Persian locale, the exact message `دلیل رد الزامی است`.
3. **Given** a submitted or under-review report, **When** an authorized reviewer supplies a non-empty trimmed reason shorter than 10 characters, **Then** the action is refused with code `rejection_reason_min_length_10` and, in Persian locale, the exact message `دلیل رد باید حداقل ۱۰ کاراکتر باشد`.
4. **Given** a submitted or under-review report, **When** an authorized reviewer supplies a trimmed reason of at least 10 characters, **Then** rejection proceeds under the existing workflow and none of the missing-or-short reason codes is returned.

---

### User Story 3 - Distinguish Unset from Zero at a Glance (Priority: P2)

As a report author, reviewer, or manager, I need activity tables to show an unset or not-measured quantity differently from numeric zero, so that I can identify incomplete measurement data without opening an editor or guessing what a blank cell or dash means.

**Why this priority**: Once validation protects submission, the same distinction must remain visible wherever users review activity quantities; otherwise users can still misread an unknown value as zero work.

**Independent Test**: In Persian and English, view the requested read-only activity table and daily-report summary states with one unset quantity, one not-measured quantity, one explicit zero, and one positive quantity; verify the correct labels, warning treatment, and numeric values.

**Acceptance Scenarios**:

1. **Given** an activity quantity is null, **When** a user views it in a requested read-only activity table or daily-report activity summary, **Then** the cell shows the visually distinct label `ثبت‌نشده` in Persian or `Unset` in English instead of a blank, dash, or zero.
2. **Given** an activity is marked as not measured, **When** a user views it in a requested read-only activity table, **Then** the same localized unset label and visual treatment are shown even if no numeric quantity is available.
3. **Given** an activity is marked measured and has an explicitly recorded quantity of zero, **When** a user views any requested activity-table or summary surface, **Then** the cell shows numeric `0`, not the unset label.
4. **Given** an unset label is shown, **When** a user scans the table, **Then** its compact muted appearance and clearly visible caution border distinguish it from both ordinary numeric values and critical errors.

---

### Edge Cases

- A rejection reason containing only spaces, tabs, or line breaks is treated as missing and returns `rejection_reason_required`.
- Leading and trailing whitespace does not count toward the 10-character minimum for a rejection reason.
- A rejection reason with exactly 10 non-whitespace characters is valid for the minimum-length rule.
- Numeric zero remains valid regardless of whether it is presented as `0`, `0.0`, or `0.00`; display formatting must not convert it to unset.
- If an inconsistent or legacy row is marked not measured but also contains a numeric quantity, the not-measured state governs read-only display and the row is shown as unset; this feature does not silently rewrite either stored value.
- Negative or positive non-zero quantities continue to follow existing quantity-domain rules; this feature changes only the distinction between explicit zero and unset.
- If one report contains several measured-but-unset activities, submission is refused consistently and no row is silently converted to zero.
- A row marked not measured is displayed as unset in the requested read-only surfaces, but this feature does not redefine whether that row participates in calculations.
- Unknown validation codes continue to use the product's existing fallback behavior; the four codes in this feature must always have Persian and English messages.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow the existing submit workflow only when the report is in draft or rejected state.
- **FR-002**: A submit attempt from any other state MUST be refused with the language-independent code `report_not_in_submittable_state`; the Persian feedback MUST be exactly `فقط گزارش‌های پیش‌نویس یا رد شده قابل ارسال هستند`, and English feedback MUST communicate the same corrective meaning.
- **FR-003**: A missing, null, empty, or whitespace-only rejection reason MUST be refused with the language-independent code `rejection_reason_required`; the Persian feedback MUST be exactly `دلیل رد الزامی است`, and English feedback MUST communicate the same corrective meaning.
- **FR-004**: A non-empty rejection reason whose trimmed content is shorter than 10 characters MUST be refused with the language-independent code `rejection_reason_min_length_10`; the Persian feedback MUST be exactly `دلیل رد باید حداقل ۱۰ کاراکتر باشد`, and English feedback MUST communicate the same minimum.
- **FR-005**: A rejection reason whose trimmed content contains at least 10 characters MUST satisfy the reason-length rule and allow the existing authorized rejection workflow to proceed.
- **FR-006**: Submission MUST be refused when any activity is marked measured and its quantity is unset, using the language-independent code `quantity_unset_invalid` and the exact Persian feedback `مقدار کارکرد باید مشخص شود؛ در صورت عدم کارکرد عدد صفر وارد شود`; English feedback MUST communicate the same corrective instruction.
- **FR-007**: An explicitly recorded numeric zero, including decimal representations such as `0.00`, MUST be accepted as a valid measured quantity and MUST NOT trigger `quantity_unset_invalid`.
- **FR-008**: The system MUST preserve the semantic distinction between an explicitly recorded zero and an unset quantity throughout submission validation and every requested activity-quantity presentation.
- **FR-009**: In the requested read-only activity-row views and daily-report activity summary, a null quantity MUST be rendered as the localized unset label rather than as a blank cell, plain dash, or numeric zero.
- **FR-010**: In the requested read-only activity-row views, an activity marked not measured MUST use the same localized unset presentation even if an inconsistent legacy row also contains a numeric quantity.
- **FR-011**: An activity marked measured with an explicitly recorded zero MUST be rendered as numeric zero in every requested activity-row and summary view.
- **FR-012**: The unset presentation MUST use the localized text `ثبت‌نشده` in Persian and `Unset` in English, compact text, a muted neutral background, and a clearly visible low-severity caution border.
- **FR-013**: Persian and English localization MUST cover `report_not_in_submittable_state`, `rejection_reason_required`, `rejection_reason_min_length_10`, `quantity_unset_invalid`, and the daily-report unset-quantity label.
- **FR-014**: Validation identifiers MUST remain stable and language-independent; changing locale MUST change only the user-facing message or label, not the code used to identify the outcome.
- **FR-015**: The specified invalid submit, missing-reason, short-reason, measured-but-unset, explicit-zero, and localized unset-display outcomes MUST have automated regression coverage.
- **FR-016**: All behavior in this feature MUST remain within the existing project membership, report viewing, editing, submission, and approval authorization boundaries.

### Key Entities *(include if feature involves data)*

- **Daily Report**: A project-scoped operational record with a lifecycle state that determines whether it is eligible for submission or rejection.
- **Activity Quantity State**: The combination of whether an activity is measured and whether a numeric quantity is present; it distinguishes measured values, explicit zero, measured-but-unset, and not-measured states.
- **Rejection Reason**: Reviewer-provided, trimmed explanatory text that must be present and at least 10 characters before an eligible report may be rejected.
- **Validation Outcome**: A refused workflow action represented by a stable language-independent code and a locale-appropriate corrective message.
- **Unset Quantity Presentation**: The localized, visually distinct read-only representation of a null or not-measured activity quantity.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of acceptance cases covering non-submittable states, missing rejection reasons, and short rejection reasons, users receive the specified stable validation code and the correct locale-appropriate corrective message.
- **SC-002**: In 100% of acceptance cases, a measured activity with no quantity prevents submission with `quantity_unset_invalid`, while explicit `0` and `0.00` quantities pass this rule without being changed or misclassified.
- **SC-003**: Across every requested read-only activity-table and summary state in both Persian and English, 100% of null or not-measured quantities show the localized unset label and 100% of measured explicit-zero quantities show numeric zero.
- **SC-004**: Automated regression checks cover all four stable validation codes, the 10-character rejection boundary, explicit-zero acceptance, measured-but-unset refusal, and both locale variants of the unset label.
- **SC-005**: During acceptance review, a reviewer can correctly distinguish unset, explicit-zero, and positive activity quantities on first inspection without opening an editor or consulting raw data.

## Assumptions

- Existing report lifecycle transitions, permissions, project isolation, and successful submit/reject behavior remain authoritative and are not redesigned by this feature.
- Rejection reasons are evaluated after trimming leading and trailing whitespace; exactly 10 remaining characters satisfies the minimum.
- The existing quantity domain rules continue to govern non-zero values. This feature adds no new unit, precision, sign, or calculation rule.
- The requested display scope is the read-only quantity cells in activity-row views and the activity quantity column in the daily-report summary; unrelated numeric fields are outside scope.
- The compact muted warning treatment follows the established accessible design and localization systems while preserving sufficient contrast in supported themes.
- Stable validation codes are the integration contract; Persian and English messages are presentation content selected by locale.

## Scope Boundaries

- This feature standardizes only the submit/reject validation outcomes and zero-versus-unset quantity semantics described in US-DR-11 and US-DR-14.
- It does not change correction cloning, correction cancellation, version-lineage metadata, report locking, approval rules, or correction conflict handling.
- It does not convert existing null quantities to zero, infer quantities, or change report calculations.
- It does not broaden who may view, edit, submit, review, reject, or approve a daily report.
