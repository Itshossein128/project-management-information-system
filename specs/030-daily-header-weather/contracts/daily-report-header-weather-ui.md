# UI Contract: Standardized Daily Weather and Temperature

## 1. Covered daily-report surfaces

The same weather/temperature/note behavior applies to:

- the reusable `ReportHeader` used by the daily-report form;
- the comprehensive auto-summary metadata editor in the daily-report detail route;
- the read-only comprehensive report detail/summary display.

The editable surfaces share one ordered weather metadata source, one selector behavior, one temperature validator, the same locale keys, and the same field-error mapping. This feature does not change report-entry permissions, shift controls, site status, or activity editing.

## 2. Weather selector

Presentation order:

1. `clear` — آفتابی / صاف — Clear / sunny
2. `cloudy` — ابری — Cloudy
3. `rainy` — بارانی — Rainy
4. `snowy` — برفی — Snowy
5. `stormy` — طوفانی / گرد و غبار — Stormy / dust

Requirements:

- Display exactly five choices and no retired value.
- Reuse a single ordered metadata source; do not duplicate abbreviated labels in another editor.
- Expose one selected value through radio semantics.
- Provide visible localized text in addition to the decorative icon.
- Support pointer and keyboard selection; checked/selected state is programmatically exposed.
- When read-only, display the localized label rather than the raw stable value.
- An API-returned `null` is represented as no observation according to the existing optional behavior; it is never silently converted to a fabricated weather observation on read.

## 3. Temperature interaction

Both inputs:

- use decimal-capable numeric entry;
- expose `min=-40`, `max=60`, and `step=0.1`;
- allow intentional blank values;
- retain string state until a valid edit is committed.

### Immediate validation

1. A complete numeric value below `-40` or above `60` receives a localized field error.
2. When both completed values are valid numbers but the maximum is lower, only `temp_max` receives `temp_max_must_be_gte_temp_min` guidance.
3. Equal values are valid.
4. A temporarily incomplete in-focus token is not converted to `null`, does not trigger an unrelated pair error, and is not autosaved.
5. On blur or explicit save, an incomplete/invalid token becomes an actionable field error.

### Save gate

The same validation result must block all header write paths before they call the API or queue an offline mutation:

- explicit save from the daily-report form;
- debounced/autosave from the daily-report form;
- explicit save from the auto-summary metadata editor;
- offline header queueing.

When valid, a blank committed value is serialized as `null`; a complete numeric value is sent in the existing accepted decimal representation.

### Server errors

The UI consumes `ApiRequestError.code` and `ApiRequestError.details`. It does not inspect an Axios-style `response` object or parse localized message text.

- `temp_max_must_be_gte_temp_min` maps to the same inline `temp_max` error region.
- Bound errors map to the temperature field named in details.
- Toasts may supplement inline feedback but never replace it.

## 4. Weather-impact notes

- Provide a localized, labelled multi-line control in each editable daily-report header surface.
- The field is optional and its local empty representation is always `""`.
- Initialize local state from `report.weather_impact_notes ?? ""` before dirty-checking or autosave starts.
- Preserve line breaks and mixed Persian/English text through save, refetch, route reload, and read-only display.
- Use `dir="auto"` on editable and displayed narrative text where necessary for mixed-language readability.
- Do not add an arbitrary business character limit or rich-text behavior.
- Do not clear or hide the field when the selected weather condition changes.

## 5. Read-only display and PDF handoff

- Read-only daily-report views show non-empty notes with whitespace preserved.
- Empty notes may be omitted from the on-screen narrative card, but the API value remains `""`.
- Downloading the official PDF uses the existing endpoint.
- The PDF itself always contains the exact row label «توضیحات و اثرات شرایط جوی», including when the value is empty.

## 6. Offline compatibility

- Cached reports and queued header payloads normalize `sunny→clear`, `partly_cloudy→cloudy`, and `foggy→cloudy` during the existing data upgrade.
- Queue identity, ordering, retry count, timestamps, unrelated fields, and note text remain unchanged.
- New queued writes contain only approved weather values.
- Temperature validation runs before queue insertion; invalid or incomplete edits produce no queued mutation.
- `weather_impact_notes` survives queueing, replay, server refetch, and conflict display.

## 7. Localization and accessibility

- Labels, weather names, helper text, placeholders, and validation messages come from both `fa` and `en` locale catalogs.
- Persian renders under RTL and English under LTR; mixed note content remains readable.
- Each temperature label is associated with its input.
- Inline errors have stable IDs, are referenced by `aria-describedby`, set `aria-invalid`, and are announced through an appropriate alert/live region.
- The weather group has a localized accessible group name; each choice has the same localized accessible and visible name.
- Focus remains on or can return directly to the invalid field after a failed save.

## 8. Acceptance scenarios

1. In Persian and English, both editable header surfaces expose exactly the five approved weather choices in the documented order and never show a retired value.
2. Keyboard selection changes the checked weather choice without relying on icon or color alone.
3. `-40`, `60`, and equal minimum/maximum values save successfully.
4. `-40.1`, `60.1`, and a maximum below the minimum show the correct inline error and cause zero API/offline writes.
5. A temporarily incomplete numeric token causes no autosave; completing or correcting it restores normal save behavior.
6. A structured server reversed-range error is displayed beside `temp_max` in the active locale.
7. Clearing one temperature intentionally sends `null` and leaves the other valid value intact.
8. Multi-line Persian/English notes survive save, refetch, route reload, summary rebuild, correction, and offline replay.
9. Reopening the legacy daily-report form hydrates saved notes before autosave, preventing accidental erasure.
10. The downloaded PDF contains the exact weather-impact label and either the saved text or an empty cell.
