# Research: Standardized Daily Weather and Temperature

## Decision 1 — Keep one authoritative five-value weather vocabulary

**Decision**: Retain the existing shared `WeatherCondition` vocabulary with exactly `clear`, `cloudy`, `rainy`, `snowy`, and `stormy`. Update or verify every direct consumer of that vocabulary: `DailyReport`, `WeatherLog`, `DisciplineSubReport`, aggregation severity, seed/fixture data, API types, daily-report controls, specialty/standalone weather controls, icons/colors, offline payloads, tests, and endpoint documentation.

**Rationale**: `WeatherLog` and `DisciplineSubReport` import the enum owned by field reports. Narrowing only the daily-report header would leave inputs capable of producing values the summary cannot consistently rank or display.

**Alternatives considered**:
- Separate enums for each model: rejected because the same project-day could acquire incompatible weather values.
- Translate legacy values only in the browser: rejected because direct clients, stored rows, aggregation, and offline replay would remain inconsistent.

## Decision 2 — Treat committed normalization migrations as immutable and semantically forward-only

**Decision**: Preserve the committed ordered normalization: `sunny → clear`, `partly_cloudy → cloudy`, and `foggy → cloudy` in daily reports and weather logs, followed by the dependent specialty-report normalization. Because migrations `field_reports.0018_daily_header_weather` and `sub_reports.0004_standardize_weather` are already committed on `develop`, implementation MUST verify them rather than rewrite them. Any corrective schema/data work uses a new forward migration.

**Rationale**: The ordering normalizes data before restricting application choices, and the cross-app dependency prevents specialty rows from lagging behind the shared enum. Rewriting a committed migration risks divergent histories in environments where it has already run.

**Alternatives considered**:
- Edit or split the committed migration to remove formerly bundled scope: rejected because deployment application state cannot be assumed and migration history must remain stable.
- Add indefinite request-time aliases: rejected because retired values must be rejected as new input.

**Rollback boundary**: Exact reversal is impossible because normalized `cloudy` does not reveal whether its source was `cloudy`, `partly_cloudy`, or `foggy`. Schema reversal is not a semantic rollback. Production rollback requires the pre-migration database backup or a forward corrective migration.

## Decision 3 — Reject unknown new values and make aggregation deterministic for invalid or absent inputs

**Decision**: Accept only the five approved values at write boundaries. Aggregation ranks only keys present in the approved severity table using `stormy > snowy > rainy > cloudy > clear`; blank inputs are ignored. Unknown persisted values are not eligible to win aggregation and must be surfaced by integrity checks. If no valid contribution exists and there is no project override, the derived summary weather becomes `null` rather than retaining a stale previously derived value. An explicit approved project override remains authoritative.

**Rationale**: The current generic score fallback can select an unknown value when it is the only nonblank contribution, and leaving the previous value untouched when no valid source exists can misstate the current report day.

**Alternatives considered**:
- Give unknown values a severity of zero: rejected because they can still become the selected result.
- Preserve the previous derived value when no contributors remain: rejected because it has no current provenance.
- Last contribution wins: rejected because queryset order would affect the official result.

## Decision 4 — Enforce temperature rules through model metadata and effective-state API validation

**Decision**: Keep optional decimal values at the existing precision. Attach inclusive `-40`/`60` validators to the daily-report fields and validate the effective pair after merging incoming PATCH attributes with the stored instance. When both values exist and `temp_max < temp_min`, return HTTP 400 with `error.code=temp_max_must_be_gte_temp_min` and details under `temp_max`. Use decimal comparison and cover model `full_clean()` separately from the supported API path.

**Rationale**: Field validators define the domain for generated serializer fields, while object-level serializer validation is required for cross-field and partial-update correctness. Django `save()` does not automatically run `full_clean()`, so supported service/API paths cannot rely on model `clean()` alone.

**Alternatives considered**:
- Client-only validation: rejected because direct API and offline-sync writes bypass it.
- Compare only fields present in a PATCH: rejected because a changed value can contradict its stored peer.
- Depend on model `save()` to run validators: rejected because Django does not do so automatically.

## Decision 5 — Use one client validator and gate every header write

**Decision**: Keep editable temperatures as strings and use one pure validator shared by `ReportHeader`, the auto-summary metadata editor, manual save, debounced autosave, and offline queueing. It distinguishes blank optional values, incomplete in-focus numeric tokens, invalid completed tokens, out-of-range values, and a reversed completed pair. Invalid or incomplete committed input blocks mutation; the reversed error belongs only to `temp_max`.

**Rationale**: The existing inline calculations do not block legacy manual/autosave paths, and the summary editor validates only after click using toast-only feedback. A single write gate prevents UI drift and prevents autosave from persisting or clearing partially typed data.

**Alternatives considered**:
- Rely on native `min`/`max` attributes: rejected because programmatic and autosave writes do not necessarily trigger native form validation.
- Convert state to numbers immediately: rejected because intermediate input such as `-` or a trailing decimal cannot be represented safely and may be mistaken for empty input.

## Decision 6 — Centralize the weather selector and consume localization keys

**Decision**: Define one ordered client metadata tuple containing the five stable values, icons, and translation keys; derive the TypeScript union from it where practical. Reuse one accessible selector in both `ReportHeader` and the actual auto-summary metadata editor. The selector presents the approved order, visible localized text, icon-as-decoration, checked state, and keyboard navigation.

**Rationale**: The client currently duplicates the type and option lists. The two daily-report editors already display different labels and control types, demonstrating real contract drift. Hard-coded Persian prevents the English experience required by the constitution.

**Alternatives considered**:
- Keep separate option maps/selectors: rejected because label, order, and accepted-value drift has already occurred.
- Use icon/color alone: rejected because weather meaning must remain perceivable without visual color/icon interpretation.

## Decision 7 — Treat weather-impact notes as summary-owned plain text

**Decision**: Store `weather_impact_notes` directly on `DailyReport` as optional plain multi-line text with `''` as the persisted empty value. Include it in header writes, detail reads, editable-field allowlists, correction copies, sync snapshots/conflicts, and automatic-summary preservation. Initialize every client header state from the fetched value before autosave can run.

**Rationale**: The field is project-summary context, not an additive specialty row. The legacy form currently omits the field during detail-to-state mapping, so reopening followed by autosave can erase existing notes.

**Alternatives considered**:
- Derive or concatenate notes from specialty reports: rejected because no approved specialty source field exists.
- Make local state optional: rejected because `undefined`, missing, and empty string create unnecessary dirty-check and accidental-clear ambiguity.
- Add rich text or a new note entity: rejected as outside scope.

## Decision 8 — Normalize offline legacy values without accepting them as new server input

**Decision**: Preserve the existing IndexedDB data-only upgrade that maps retired weather values in cached reports and pending queue payloads. Keep queue identity, order, retry state, timestamps, unrelated fields, temperature strings, and notes unchanged. New browser writes emit only approved values, and the server rejects retired values from stale or external clients.

**Rationale**: Offline work created before deployment must not be stranded or deleted, but permanent server-side coercion would weaken the new contract.

**Alternatives considered**:
- Drop old cached/queued data: rejected because it loses user work.
- Coerce all retired input forever at the API: rejected because stale clients would remain invisible.

## Decision 9 — Make the PDF row unconditional, exact, and safe for plain text

**Decision**: Always add the header-table row labeled exactly «توضیحات و اثرات شرایط جوی». Use an empty cell when the note is empty. Render note content as escaped plain text with preserved line breaks before passing it to ReportLab, then verify format, extracted content, and visual layout.

**Rationale**: The current implementation conditionally emits a shorter «تأثیرات جوی» row and therefore violates official-form parity. Passing raw user text through paragraph markup can mishandle line breaks or characters such as `&` and `<`.

**Alternatives considered**:
- Omit the row when empty: rejected because the approved official form requires a stable documentation row.
- Assert only the `%PDF` signature: rejected because it does not prove label/content presence.
- Raw byte substring assertions: rejected because font embedding, shaping, and compression make them unreliable.

## Decision 10 — Map structured API errors to field-associated bilingual feedback

**Decision**: Consume the existing `ApiRequestError.code` and `details` fields rather than inspecting Axios-shaped response objects or searching message strings. Associate temperature messages with stable element IDs, `aria-describedby`, `aria-invalid`, and an announced error region. Source labels, help, placeholders, and messages from Persian and English locale catalogs; use `dir="auto"` for mixed-language note content.

**Rationale**: The API client already preserves stable structured errors. The current summary editor reads an error shape that the client never throws, and toast-only feedback does not provide a reliable correction path or accessible field association.

**Alternatives considered**:
- Parse localized error messages: rejected because message text changes by locale and is not a stable contract.
- Keep hard-coded Persian: rejected because the product and constitution require Persian and English behavior.

## Decision 11 — Verify the feature with explicit proof boundaries

**Decision**: Use red → minimal green → regression sequencing for migration normalization, strict API codes, aggregation edge cases, notes preservation, PDF exact/empty/multiline behavior, shared client validation, and bilingual browser flows. Report migration, backend, frontend, offline, PDF, browser, accessibility, and broad regression evidence separately.

**Rationale**: Existing focused tests cover several happy paths but do not prove migration execution, exact stable-code propagation, empty PDF row, safe multiline rendering, autosave blocking, structured client error mapping, or English behavior.

**Alternatives considered**:
- Treat committed code or checked tasks as completion proof: rejected because neither demonstrates final behavior.
- Use only typecheck and serializer tests: rejected because they do not prove migration preservation, browser interaction, offline replay, or PDF output.
