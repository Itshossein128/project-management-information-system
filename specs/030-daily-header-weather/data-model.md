# Data Model: Daily Report Header and Weather Controls

## 1. Shared Weather Condition

One language-independent vocabulary is shared by `DailyReport`, `WeatherLog`, and `DisciplineSubReport`.

| Value | Persian label | English label | Aggregation severity |
|-------|---------------|---------------|----------------------|
| `clear` | آفتابی / صاف | Clear / sunny | 10 |
| `cloudy` | ابری | Cloudy | 20 |
| `rainy` | بارانی | Rainy | 30 |
| `snowy` | برفی | Snowy | 40 |
| `stormy` | طوفانی / گرد و غبار | Stormy / dust | 50 |

Blank remains allowed only where it is already optional (`DailyReport`, `DisciplineSubReport`). `WeatherLog.weather_condition` remains required.

### Legacy normalization

| Legacy value | New value | Applies to |
|--------------|-----------|------------|
| `sunny` | `clear` | Daily reports, weather logs, specialty reports, offline cached/pending payloads |
| `partly_cloudy` | `cloudy` | Same |
| `foggy` | `cloudy` | Same |

After normalization, retired values are not valid new input and are absent from choices, metadata maps, icons/colors, severity rules, seeds, fixtures, and tests.

## 2. Project Daily Report

Existing identity and aggregation behavior remain unchanged: one current, non-deleted report for `(project, report_date, shift)` and auto-summary shells use `shift=full`.

### Added and changed header fields

| Field | Type / default | Rules |
|-------|----------------|-------|
| `weather_condition` | nullable shared weather choice | Five values only; derived by severity unless `weather_override=true` |
| `temp_min` | decimal(5,1), nullable | Inclusive -40..60 |
| `temp_max` | decimal(5,1), nullable | Inclusive -40..60; must be `>= temp_min` when both are known |
| `weather_impact_notes` | text, blank, default `''` | Project-level narrative; preserved through rebuild, correction, sync, and PDF |
| `site_status` | `active` / `inactive` | Existing field; active state clears inactive reason |
| `inactivity_reason` | choice, blank, default `''`, max length sufficient for `strike_or_dispute` and `client_stop_order` | Required whenever an explicit save/finalization leaves `site_status=inactive` |
| `weather_override` | boolean | Existing; rebuild must not replace weather when true |
| `site_status_override` | boolean | Existing; rebuild must not replace site status when true |

### Inactive-site reasons

| Value | Persian label | English label |
|-------|---------------|---------------|
| `weather` | نامساعد بودن شرایط جوی | Adverse weather |
| `holiday` | تعطیل رسمی / تقویمی | Official / calendar holiday |
| `strike_or_dispute` | اختلاف یا اعتصاب | Strike or dispute |
| `client_stop_order` | دستور توقف کارفرما / مشاور | Client / consultant stop order |
| `safety_incident` | حادثه ایمنی | Safety incident |

### Validation invariant

For the effective state after merging PATCH input with the stored instance:

1. Each supplied temperature is within `[-40, 60]`.
2. When both exist, `temp_max >= temp_min`.
3. If `site_status=inactive`, `inactivity_reason` is one of the five values.
4. If `site_status=active`, persist `inactivity_reason=''` even if a stale client sends a value.
5. Stable validation codes are `temp_max_must_be_gte_temp_min` and `inactivity_reason_required`.

The field remains blank-capable at the schema level so pre-feature/derived inactive drafts can be loaded without invented history. User saves and workflow transitions enforce the invariant.

### Rebuild behavior

| Condition | Weather result | Site/reason result |
|-----------|----------------|--------------------|
| Override flag true | Preserve project value | Preserve project status; validate reason on user save/finalization |
| No weather override | Most severe nonblank specialty value | N/A |
| No site override; any contributing specialty inactive | N/A | Set inactive; preserve existing valid reason, otherwise leave draft requiring classification |
| No site override; contributing specialties all active | N/A | Set active and clear inactivity reason |
| Weather-impact notes | Never derived | Always preserve |

## 3. Standalone Weather Log

`WeatherLog` continues to have one active row per project/date.

| Field | Change |
|-------|--------|
| `weather_condition` | Uses the five-value shared vocabulary; required |
| `temp_min`, `temp_max` | Gain the same inclusive range and cross-field validation |

No inactivity reason or weather-impact notes are added to `WeatherLog`; those are approved project daily-summary fields.

## 4. Specialty-Unit Report

`DisciplineSubReport.weather_condition` uses the five-value shared vocabulary and remains optional. `site_status` remains `active|inactive`; this feature does not add specialty inactivity reasons. Submitted/approved specialty reports continue to contribute to the project summary.

## 5. Execution Activity

No schema change is required.

| Existing field | Guard rule |
|----------------|------------|
| `quantity` | Normalize to a number; values greater than zero on an inactive report require confirmation before save/queue |
| `shift` | Remains one of `shift_1`, `shift_2`, `shift_3` |
| derived/provenance flags | Remain protected by the auto-summary behavior |

The warning is a client acknowledgment and does not change the activity record or bypass server authorization/validation.

## 6. Offline Representation

The browser cache and queue mirror these header fields:

- `weather_condition`
- `temp_min`, `temp_max`
- `site_status`
- `inactivity_reason`
- `weather_impact_notes`
- existing notes/override metadata already supported by the relevant flow

IndexedDB upgrade normalizes retired weather strings in both `offline_daily_reports` and pending/failed `offline_queue` payloads without deleting queue identity, retry state, or unrelated payload fields.

## 7. Correction and Sync Copies

Creating a correction version copies:

- weather, temperatures, impact notes
- site status and inactivity reason
- weather/site override flags
- existing summary-owned notes and management opinion

Sync conflict comparison includes both new fields so simultaneous server/client edits are surfaced rather than overwritten.

## 8. State Transitions

| From | Action | To | Required effect |
|------|--------|----|-----------------|
| Active | User selects inactive | Inactive draft | Reveal reason selector; block save until selected |
| Inactive | User selects active | Active | Clear reason client-side and server-side |
| Derived active | Specialty rebuild finds any inactive source | Inactive draft | Preserve a valid existing reason or mark as requiring classification; never guess |
| Derived inactive | Rebuild finds all contributing sources active | Active | Clear stale reason |
| Inactive draft without reason | Submit/review/approve | No transition | Reject with `inactivity_reason_required` |
| Inactive + positive activity edit | Save attempt | Pending confirmation | Cancel: no write; confirm: resume normal validation/mutation |

## 9. Migration and Rollback

1. Count and back up retired weather values in all three server tables.
2. Normalize `field_reports` rows before altering field choices/additional validation metadata.
3. Add daily-report fields with non-destructive blank defaults.
4. Normalize specialty rows in the dependent `sub_reports` migration, then alter choices.
5. Upgrade offline data before pending records are synced by the new client.
6. Verify no retired server or offline value remains.

Exact reversal of `partly_cloudy`/`foggy` is impossible after merging to `cloudy`; production rollback requiring exact legacy categories uses the pre-migration backup.
