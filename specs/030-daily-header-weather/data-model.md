# Data Model: Standardized Daily Weather and Temperature

## 1. Shared Weather Condition

One language-independent vocabulary is shared by the existing daily report, standalone weather log, and specialty report models.

| Value | Persian label | English label | Aggregation severity |
|-------|---------------|---------------|----------------------|
| `clear` | آفتابی / صاف | Clear / sunny | 10 |
| `cloudy` | ابری | Cloudy | 20 |
| `rainy` | بارانی | Rainy | 30 |
| `snowy` | برفی | Snowy | 40 |
| `stormy` | طوفانی / گرد و غبار | Stormy / dust | 50 |

Blank remains allowed only where the existing field is optional. Retired and unknown values are invalid for all new writes.

### Legacy normalization

| Legacy value | New value | Affected persisted/offline data |
|--------------|-----------|---------------------------------|
| `sunny` | `clear` | Daily reports, weather logs, specialty reports, cached daily reports, pending daily-report payloads |
| `partly_cloudy` | `cloudy` | Same |
| `foggy` | `cloudy` | Same |

Normalization changes only the weather value. Record identity, project/date relationships, lifecycle state, note text, queue metadata, and all unrelated fields are preserved.

## 2. Daily Report

Existing identity and lifecycle behavior remain unchanged: the project summary is the current, non-deleted full-day report for its project/date under the automatic-summary architecture.

### Header fields

| Field | Representation | Default / optionality | Rules |
|-------|----------------|-----------------------|-------|
| `weather_condition` | nullable shared weather choice | `null` allowed | Non-empty value is one of five; derived by severity unless the existing project override is active |
| `temp_min` | decimal with one fractional digit | `null` allowed | Inclusive `-40..60` Celsius |
| `temp_max` | decimal with one fractional digit | `null` allowed | Inclusive `-40..60`; when both are known, `temp_max >= temp_min` |
| `weather_impact_notes` | plain multi-line text | blank, default `''` | Project-level narrative; preserved through readback, rebuild, correction, sync, and official PDF |
| `weather_override` | boolean | existing default | When true, an approved explicit daily-report weather value is not replaced by aggregation |

### Effective-state validation

For an update, compute the candidate state by taking each submitted value and falling back to the stored value for any omitted field.

1. `temp_min` is `null` or within `[-40, 60]`.
2. `temp_max` is `null` or within `[-40, 60]`.
3. If both candidate values are non-null, `temp_max >= temp_min`.
4. A reversed pair produces code `temp_max_must_be_gte_temp_min` attached to `temp_max`.
5. Equal values are valid.
6. Clearing one temperature persists `null` and suspends the ordering rule until both values are known again.

### Preservation rules

| Operation | Required effect |
|-----------|-----------------|
| Read detail/header | Return weather, both temperatures, and complete impact-note text |
| Automatic summary rebuild | Recompute weather only when no approved override exists; never overwrite impact notes |
| Correction/version copy | Copy weather, temperatures, impact notes, and the existing weather override |
| Offline sync/merge | Include the same fields in payload comparison and conflict details |
| PDF generation | Render weather and temperatures in existing rows; always render the exact weather-impact row |

## 3. Specialty Report Compatibility Surface

`DisciplineSubReport.weather_condition` uses the shared five-value vocabulary and remains optional. Eligible specialty reports continue to contribute nonblank approved values to daily-summary weather.

No new note or temperature field is added to specialty reports by this feature.

### Aggregation transition

| Input state | Daily-report result when no override exists |
|-------------|---------------------------------------------|
| One or more approved nonblank values | Highest severity: `stormy > snowy > rainy > cloudy > clear` |
| Only blank values or no eligible contributors | `null`; do not retain a stale previously derived value |
| Unknown persisted value mixed with approved values | Unknown is ignored for ranking and reported by integrity verification |
| Unknown persisted value only | `null` plus integrity failure evidence; never expose it as the official result |
| Approved project override active | Preserve the project value; do not recalculate it |

## 4. Standalone Weather Log Compatibility Surface

`WeatherLog.weather_condition` uses the same shared vocabulary and remains required. Its existing fields and lifecycle remain separate from the daily-report header.

This feature requires legacy weather normalization and regression coverage for this surface because the enum is shared. It does not add `weather_impact_notes` or create a new standalone-weather user story. Temperature behavior outside the daily-report header is not expanded by this specification; any already-shared validator remains a compatibility invariant rather than new scope.

## 5. Client Header State

The editable daily-report header state uses a single representation across `ReportHeader` and the auto-summary metadata editor.

| State field | Client representation | Commit conversion |
|-------------|-----------------------|-------------------|
| `weather_condition` | approved weather value or `null` | same value |
| `temp_min` | string while editing | complete valid decimal string, or `null` when intentionally blank |
| `temp_max` | string while editing | complete valid decimal string, or `null` when intentionally blank |
| `weather_impact_notes` | string, never `undefined` in local state | exact string, including line breaks |

### Temperature editing states

- **Blank**: valid optional value; conversion to `null` occurs only when the edit is committed.
- **Incomplete while focused**: examples include a lone minus sign or unfinished decimal token; do not autosave and do not emit an unrelated cross-field error.
- **Invalid completed token**: attach a field error and block every write path.
- **Valid completed token**: parse as a decimal and apply range validation.
- **Valid pair**: apply the ordering rule and attach any violation only to `temp_max`.

## 6. Offline Representation

Cached daily reports and pending header mutations mirror:

- `weather_condition`
- `temp_min`
- `temp_max`
- `weather_impact_notes`
- existing identity, retry, timestamp, and conflict metadata

The IndexedDB data upgrade normalizes retired weather strings without deleting or reordering queued work. New offline writes use only approved values and pass the same temperature validator before queue insertion.

## 7. PDF Representation

The official header table contains one unconditional row:

| Label | Value |
|-------|-------|
| `توضیحات و اثرات شرایط جوی` | Exact saved note text, or an empty cell when the note is empty |

The value is treated as plain text. Markup-significant characters are escaped, line breaks are preserved for layout, and no placeholder is inserted as though it were user-authored content.

## 8. Migration and Rollback

The committed migration sequence is:

1. Normalize known legacy values in daily reports and weather logs.
2. Add the daily-report weather-impact field and daily-report temperature validators as recorded in model state.
3. Narrow the shared weather choices.
4. Run the dependent specialty-report migration to normalize its rows and narrow its choices.
5. Upgrade offline cached/queued representations on first client open.

Implementation rules:

- Do not edit already-committed migration files; corrections use a new forward migration.
- Before a production-like apply, back up the database and count each legacy and unexpected nonblank value in all three server tables.
- After apply, assert zero retired/unexpected values and unchanged row identities/unrelated columns.
- Schema/model-state reversal does not restore original category meaning. Exact semantic rollback requires backup restoration.
