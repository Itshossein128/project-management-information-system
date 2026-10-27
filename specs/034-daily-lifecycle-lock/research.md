# Research: Daily Report Lifecycle Lock

## Correction transition serialization

**Decision**: Lock and reload the authoritative current source report before correction eligibility/open-request checks; lock the correction/result/source set before cancellation. Keep state changes and cloning in the existing atomic correction-service boundary.

**Rationale**: The current open path checks a caller-supplied record and an existence query before moving `is_current`. An atomic block alone does not prevent two parallel requests from passing that check. Locking makes `correction_already_open` deterministic instead of exposing an integrity failure or stale restoration.

**Alternatives considered**: Database uniqueness alone was rejected because it can yield a server failure; hiding the UI action was rejected because direct requests bypass it.

## Model-aware correction cloning

**Decision**: Extend the existing explicit clone specification with the required semantic fields for activity, machinery, general-activity, visit, and incident rows. Do not copy row ids, audit fields, deletion markers, report ownership, or derived/rebuild-only state. Continue excluding soft-deleted rows.

**Rationale**: Explicit field sets prevent copying identities and audit history into a new version. Current code loses activity crew/workforce/parcel/contractor data, entire requested child-row families, and incident severity.

**Alternatives considered**: Reflectively copying every model field was rejected because it can copy identity/audit/derived state. Copying only the five activity fields was rejected because other requested rows still disappear.

## Source-discipline compatibility

**Decision**: Preserve `source_discipline` where it exists today: on `DailyReportActivity`. Preserve incident `severity` and its existing source-provenance fields. Do not add a new incident `source_discipline` column in this feature.

**Rationale**: The current incident model has no `source_discipline` field, so adding it to clone fields would fail and creating an uncontracted empty column would not preserve data. This is the schema-compatible interpretation of the supplied requirement and avoids a speculative migration.

**Alternatives considered**: Adding a nullable incident column was rejected because no writer, reader, taxonomy, or existing value is defined. Ignoring source discipline was rejected because the existing activity field would still be lost.

## Version lineage metadata

**Decision**: Extend version output with `modifier_name`, `correction_reason`, and `approved_at`. Resolve the reason only from the correction request whose result is that version; return null for a root/no-associated version. Fetch modifier and result-correction data with the lineage query.

**Rationale**: Linking a reason to the predecessor misattributes a successor correction. Existing approval time is already persisted and the frontend has a Jalali date-time formatter.

**Alternatives considered**: Browser-side correlation duplicates server lineage rules; showing the source report’s reason on every version is semantically wrong.

## Correction cancellation UI

**Decision**: Add typed list/cancel helpers. The status bar locates the open request whose result id matches the displayed current draft, asks for explicit confirmation, invokes cancellation, invalidates report/history state, and navigates using the returned source id.

**Rationale**: The detail response lacks the correction request id, while the existing project-scoped request list provides it. The returned source id is authoritative after restoration.

**Alternatives considered**: Inferring a request id from version number is invalid; a UI-only guard cannot protect direct calls.

## Workflow errors and unset quantities

**Decision**: Emit stable localized workflow errors from submit/reject actions. Allow a measured activity with blank quantity while editing; reject it only on submit with `quantity_unset_invalid` and the approved Persian message. Preserve explicit numeric zero in storage, submission, and display.

**Rationale**: Current row validation rejects measured/null data at edit time, preventing the required submit-time lifecycle validation and unset UI state. Zero and null already have distinct storage semantics.

**Alternatives considered**: Keeping write-time rejection would prevent the requested submit check; coercing null to zero silently changes missing data into a claimed measurement.

## Shared quantity presentation

**Decision**: Add a narrow reusable quantity display helper/component and an ActivityTab-specific grid display hook. Reuse it for disabled/read-only activity cells and the summary activity table; retain the current numeric editor for editing.

**Rationale**: The generic grid currently uses disabled inputs and the summary uses a plain dash. A central rule prevents semantic drift across views.

**Alternatives considered**: Per-table conditionals drift; changing the generic numeric grid everywhere is an unnecessary broad behavior change.

## Auto-summary boundary

**Decision**: Do not broaden correction eligibility for derived auto-summary reports. The UI offers lifecycle actions only where the server authorizes correction, preserving canonical-source and rebuild rules.

**Rationale**: Correcting a derived summary can create a mutable successor detached from specialty-unit sources. This feature repairs the established lifecycle and does not create an alternate derived-summary correction path.

## Verification strategy

**Decision**: Use focused backend tests for state/data/error contracts and Playwright for browser behavior. Run migration-drift and type checks as supplemental gates, reporting known pre-existing type failures separately.

**Rationale**: API-only checks cannot prove confirmation, navigation, Jalali history, or visual zero/unset distinction; browser-only checks cannot prove concurrency, authorization, and data preservation.
