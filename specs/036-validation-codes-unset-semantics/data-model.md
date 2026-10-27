# Data Model: Existing State and Presentation Rules

This feature adds no table, column, enum, migration, backfill or persistence layer. Existing relationships, audit records, provenance and precision remain authoritative.

## DailyReport

Existing project-scoped report with identity, project reference, status, submission/review timestamps and actors, rejection_reason, and child activity rows. Status values: draft, submitted, under_review, approved, rejected. Current correction/lock/version metadata is unchanged.

- Authorized submit: draft or rejected → submitted after readiness checks. Existing submit clears rejection_reason and records submission actor/time.
- Authorized reject: submitted or under_review → rejected after reason checks. Existing reject persists trimmed reason and reviewer actor/time.
- Invalid action: HTTP 400 with stable validation code; no lifecycle field or child quantity is changed.
- Unauthorized/foreign-project action: preserve current denial semantics and project scoping; no mutation. Permission failures take precedence over exposing validation details.

## DailyReportActivity / Activity Quantity State

Existing child relationship: report → many activities. Relevant fields: id, quantity (nullable decimal, max_digits=18, decimal_places=4), quantity_measured (boolean, default true), is_deleted. Submission reads non-deleted rows only.

- true + null: measured-but-unset. Submission refuses with quantity_unset_invalid; display unset.
- true + numeric zero (0, 0.0, 0.00): valid for the completeness rule; display numeric zero and retain numeric value.
- true + positive/non-zero numeric: display numeric; existing domain validation still governs sign/range/precision.
- false + null: not-measured; display unset; existing submission/calculation rules unchanged.
- false + numeric legacy value: display unset even for zero; do not rewrite flag or quantity. Existing submission inconsistency validation remains unchanged.

Null and explicit zero must survive serialization and client state without truthiness-based coalescing. Empty-string normalization is an existing write-path concern, not a new persisted state. Shared UI tolerates undefined values as unset without broadening the API schema.

## GeneralActivityRow

Existing summary activity row with id, row_number, activity_description, location, quantity (decimal string or null), unit, notes and provenance. No quantity_measured field exists here. Render null as unset and numeric zero as numeric; do not infer or add a measured state. This is a presentation change only.

## Rejection Reason

Request field `reason` supplies existing report.rejection_reason. Missing/null/empty/whitespace-only → rejection_reason_required. Apply leading/trailing whitespace trim before length: 1–9 characters → rejection_reason_min_length_10; at least 10 characters → eligible under existing workflow. Internal whitespace counts normally, matching existing Python string length semantics. Non-string payload validation remains outside this feature's requested cases; do not silently redefine its contract.

## Validation Outcome

Existing transient envelope: error.code (stable string), error.message (localized flattened string), error.details (original field/detail tree). The four scoped codes are report_not_in_submittable_state, rejection_reason_required, rejection_reason_min_length_10, quantity_unset_invalid. Locales change presentation only. No error state is persisted.

## Unset Quantity Presentation

Derived UI state only: localized label, compact typography, muted background, local caution outline. Quantity arithmetic, stored values, exported/PDF numeric policies and provenance do not consume this presentation state. See contracts/quantity-ui.md for exact rules.
