# Research: Daily Report Header and Weather Controls

## Decision 1 — Treat weather as one shared vocabulary

**Decision**: Replace the backend `WeatherCondition` choices with exactly `clear`, `cloudy`, `rainy`, `snowy`, and `stormy`, then update every direct consumer: `DailyReport`, `WeatherLog`, `DisciplineSubReport`, aggregation severity, seed data, API types, specialty contribution form, standalone weather UI/icons/colors, daily-report UI, offline payloads, tests, and endpoint documentation.

**Rationale**: The current enum in `apps/api/core/field_reports/models.py` is imported by `sub_reports/models.py` and also backs standalone `WeatherLog`. Updating only the daily-report selector would leave accepted data and display contracts inconsistent.

**Alternatives considered**:
- Maintain separate enums per surface: rejected because it permits contradictory weather values for the same project-day.
- Translate retired values only in the frontend: rejected because direct clients and stored rows would remain nonstandard.

## Decision 2 — Normalize legacy data before restricting choices

**Decision**: Use ordered migrations: normalize `sunny → clear`, `partly_cloudy → cloudy`, and `foggy → cloudy` in `daily_reports` and `weather_logs`; then alter their choice metadata and add new fields/validators. A dependent `sub_reports` migration normalizes `discipline_sub_reports` before altering its choices. Run pre/post counts and require a database backup for non-development deployments.

**Rationale**: Existing rows are known to use all retired values. Normalizing first preserves readability and prevents the application from encountering enum values it can no longer label. `sub_reports` is a separate Django app and needs an explicit migration dependency on the field-report vocabulary migration.

**Alternatives considered**:
- Change choices without a data migration: rejected because old rows would survive with invalid values and serializer label conversion could fail.
- Add compatibility aliases indefinitely: rejected because the approved requirement removes retired values completely.

**Rollback boundary**: The schema migration can be reversed, but exact legacy categories cannot be reconstructed after `partly_cloudy` and `foggy` merge into existing `cloudy`. Treat semantic normalization as intentionally lossy; restore from the pre-migration backup if exact rollback is required.

## Decision 3 — Enforce temperature rules at model, serializer, and client boundaries

**Decision**: Attach inclusive `MinValueValidator(-40)` and `MaxValueValidator(60)` to both daily-report and standalone weather-log temperature fields. Add model-level cross-field validation and serializer validation that merges PATCH input with the stored instance. Return the reversed-range error on `temp_max` using `CodedValidationError`/coded `ErrorDetail` so the existing exception handler emits `temp_max_must_be_gte_temp_min`. Mirror the same rules in shared client validation with `min`, `max`, `step=0.1`, field errors, and server-error mapping.

**Rationale**: Model validators document the domain and drive serializer fields; explicit serializer logic is required for partial updates and stable field/code placement. Client validation gives immediate recovery guidance but is not the security boundary. Standalone `WeatherLog` uses the same domain values and should not accept a range the daily header rejects.

**Alternatives considered**:
- Client-only validation: rejected because direct API/offline-sync writes bypass it.
- Compare only values present in the PATCH body: rejected because a single-field update can contradict the persisted peer value.

## Decision 4 — Allow legacy/derived drafts to be incomplete, but never finalize or user-save them invalidly

**Decision**: Add `inactivity_reason` as a blank-default choice field for migration compatibility and add conditional model/serializer/workflow validation: an inactive report cannot be explicitly saved, submitted, reviewed, or approved without a valid reason. Do not fabricate reasons for existing inactive reports or for site status derived from specialty reports. Preserve a previously selected reason while the report remains inactive; clear it server-side whenever the saved/derived status becomes active. Expose the missing reason in the editor for human classification.

**Rationale**: Existing and automatically derived inactive reports have no trustworthy source for one of the five reasons. Guessing `weather` or `holiday` would corrupt business history. A transitional draft may therefore be incomplete, but every user mutation/finalization is guarded and the official finalized report is complete.

**Alternatives considered**:
- Backfill all inactive rows with `weather`: rejected as fabricated data.
- Add a database check constraint immediately: rejected because aggregation can derive inactive before a human supplies a reason and legacy rows cannot be truthfully backfilled.
- Add reasons to specialty reports in this feature: rejected as a wider authoring redesign not approved by the specification.

## Decision 5 — Keep notes/reasons summary-owned across rebuilds and corrections

**Decision**: `weather_impact_notes` and `inactivity_reason` are project-summary metadata. Automatic rebuilds never overwrite notes; they preserve the reason while inactive and clear it when active. Correction/version creation copies both new fields plus the existing override flags and management metadata needed to preserve the header meaning. Offline sync conflict comparison includes both fields.

**Rationale**: They are not additive specialty rows. Losing them on rebuild, correction, or sync would violate the same end-to-end consistency rule that protects management opinion and overrides.

**Alternatives considered**:
- Derive or concatenate notes from specialty reports: rejected because no approved source field exists and the feature defines a project-level narrative.

## Decision 6 — Reduce aggregation weather severity to five deterministic values

**Decision**: Replace `WEATHER_SEVERITY` with `stormy > snowy > rainy > cloudy > clear`. Continue to ignore blank specialty weather, continue to preserve `weather_override`, and reject any new retired value before it reaches aggregation.

**Rationale**: This matches the approved five categories and retains the existing most-severe reconciliation behavior from the automatic-summary feature.

**Alternatives considered**:
- Last report wins: rejected because ordering would make the summary unstable.
- Average/combined label: rejected because the approved contract permits one value only.

## Decision 7 — Separate read-only lookup from creation-capable date access

**Decision**: `GET /daily-reports/by-date/` requires `view_reports`, performs no write or rebuild, and returns an existing current full-day summary or 404. `POST /daily-reports/by-date/` requires `edit_reports`, ensures/rebuilds the summary, and remains idempotent. The list page calls POST only for editors; viewers call GET and receive a localized no-data state if no summary exists. `POST /daily-reports/` remains `400 auto_summary_only` for every caller.

**Rationale**: The current `GET` creates an empty shell when none exists and the permission dispatcher classifies both methods as view-only. That lets a viewer mutate state. Method-aware permission and behavior eliminate the mutation before authorization ambiguity.

**Alternatives considered**:
- Keep GET-as-ensure but require edit permission: rejected because viewers must still read existing summaries.
- Let viewers POST only when specialty data exists: rejected because record creation is still an edit operation.

## Decision 8 — Serialize concurrent ensure on the authoritative project row

**Decision**: Inside the existing transaction, lock the project row before checking/creating the current full-day summary, then rely on the existing conditional uniqueness constraint as a second line of defense. Test with PostgreSQL transactions that concurrent POSTs return one logical report.

**Rationale**: `transaction.atomic` alone does not prevent two requests from both observing no report and racing to insert. Locking a stable parent serializes the check/create/rebuild sequence.

**Alternatives considered**:
- Catch `IntegrityError` after `get_or_create`: rejected because transaction recovery and rebuild ownership become harder to reason about.
- Application-local mutex: rejected because it does not coordinate multiple workers.

## Decision 9 — Use one header-state contract on every editable header surface

**Decision**: Extend `HeaderState`/`HeaderPayload` with `weather_impact_notes` and `inactivity_reason`, fix shift to `full` in project-summary mode, and centralize weather/reason metadata and validation helpers. Update both `ReportHeader` (legacy/editable header path) and the actual auto-summary metadata editor in `daily-report-view.tsx`; do not leave the latter with its separate seven-value select. Server error details map back to `temp_max` and `inactivity_reason` fields.

**Rationale**: `ReportHeader` is not currently used by the auto-summary view, while `daily-report-view.tsx` contains a duplicate override editor. Both must share the approved vocabulary and validation or the primary user path would remain incomplete.

**Alternatives considered**:
- Update only `ReportHeader`: rejected because auto-summary users edit metadata elsewhere.
- Fully replace the summary page with the legacy form: rejected because it would expose derived row editing and revive the retired authoring model.

## Decision 10 — Guard the shared save pipeline before online or offline persistence

**Decision**: Add an optional asynchronous pre-save guard to the grid save pipeline. `ActivityTab` supplies current header site status (not only a possibly stale refetched report) and requests confirmation when the normalized numeric quantity is greater than zero and status is inactive. Both manual save and autosave must pass the guard before API mutation or IndexedDB queueing. Use the existing accessible Radix dialog pattern, restore focus on close, and suppress repeat autosave prompts for the same canceled row snapshot until the row changes or the user explicitly retries.

**Rationale**: The warning must cover create and edit, online and offline. Guarding only the API helper would miss queued writes; guarding only the button would miss autosave. Snapshot suppression prevents an infinite dialog loop after cancel.

**Alternatives considered**:
- `window.confirm`: rejected because it is not theme/localization friendly and offers weaker focus/test control.
- Server rejection: rejected because the approved behavior is warning plus acknowledgment, not prohibition.
- Guard only creates: rejected because the requirement explicitly includes edits.

## Decision 11 — Version and normalize the offline representation

**Decision**: Add the new header fields to offline report/header/sync payloads and conflict comparison. Increment the IndexedDB version with a data-only upgrade that normalizes retired weather values in both cached reports and pending queue payloads. New UI writes emit only the five approved values; the server still rejects retired values received from external/new clients.

**Rationale**: A user may reconnect after deployment with a pending `sunny`, `partly_cloudy`, or `foggy` payload. Rejecting it without local migration would strand legitimate pre-upgrade work.

**Alternatives considered**:
- Normalize every retired value server-side forever: rejected because it weakens the new input contract.
- Drop old offline records: rejected because it loses user data.

## Decision 12 — Verify PDF content, not only the PDF signature

**Decision**: Add focused generator/endpoint tests that extract text from the generated PDF (or render/extract with Poppler in validation) and assert the weather-impact note and localized inactivity reason. Keep the existing `%PDF` smoke assertion as a separate format check.

**Rationale**: The current test proves only that a PDF file starts with the correct signature. It cannot prove the required rows or Persian text exist.

**Alternatives considered**:
- Raw byte substring assertions: rejected because ReportLab compression/font shaping makes them unreliable.
- Visual-only manual review: rejected as insufficient regression protection; retain one visual check in addition to automated extraction.

## Decision 13 — TDD and evidence boundaries

**Decision**: Implementation tasks must establish failing tests first for migration normalization, API codes/permissions, partial updates, aggregation, correction/offline preservation, PDF content, and UI warning/validation; then implement minimal changes and rerun focused plus relevant regression suites. Report backend, migration, typecheck, Playwright, PDF, offline, and bilingual evidence separately.

**Rationale**: The constitution and prior daily-summary work both require behavioral proof; a checked task list or one narrow green suite is not completion.

**Alternatives considered**:
- Rely on source review and typecheck: rejected because neither proves permissions, migration preservation, PDF contents, or interaction behavior.
