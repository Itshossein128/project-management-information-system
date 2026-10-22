# UI Contract: Daily Report Header and Weather Controls

## 1. Daily-report entry

- `/projects/:id/daily-reports` has no **New report** button and no raw report-creation form.
- Opening a date uses `POST by-date` only when the current member has `edit_reports`.
- A viewer uses `GET by-date`; an absent report produces a localized no-data state and never creates a shell.
- The report header represents the full project day. It does not expose day/evening/night header-shift controls.
- Activity rows retain `shift_1`, `shift_2`, and `shift_3`; workforce rows retain their three shift-count columns.

## 2. Header state

Both `ReportHeader` and the auto-summary metadata editor use the same typed state, metadata, labels, and validators for:

- `weather_condition`
- `temp_min`
- `temp_max`
- `weather_impact_notes`
- `site_status`
- `inactivity_reason`
- the existing weather/site override controls where applicable

The five weather choices, in presentation order, are:

1. `clear` — آفتابی / صاف — Clear / sunny
2. `cloudy` — ابری — Cloudy
3. `rainy` — بارانی — Rainy
4. `snowy` — برفی — Snowy
5. `stormy` — طوفانی / گرد و غبار — Stormy / dust

No UI metadata, icon mapping, default, fixture, or fallback emits `sunny`, `partly_cloudy`, or `foggy`.

## 3. Temperature interaction

- Minimum and maximum inputs accept decimals with `step=0.1` and expose `min=-40`, `max=60`.
- Blank remains allowed.
- Client validation checks each bound and the effective min/max pair before mutation or queueing.
- When `temp_max < temp_min`, the error appears beside/following `temp_max`, focuses or associates with that field, and uses the localized message mapped from `temp_max_must_be_gte_temp_min`.
- Server field details override or supplement local errors without losing the stable code.

## 4. Weather-impact notes

- The header contains a localized multiline text field for `weather_impact_notes`.
- It is optional and does not disappear when weather changes.
- Saved text survives refetch, rebuild, correction creation, online sync, and offline replay.

## 5. Site status and inactivity reason

When `site_status=inactive`, reveal a required select containing exactly:

- adverse weather (`weather`)
- official/calendar holiday (`holiday`)
- strike or dispute (`strike_or_dispute`)
- client/consultant stop order (`client_stop_order`)
- safety incident (`safety_incident`)

Behavior:

- Switching from active to inactive reveals the selector and blocks save until a reason is chosen.
- Switching from inactive to active immediately clears the local reason; the server also clears stale values.
- A derived inactive draft without a reason opens with an actionable missing-reason state, not a fabricated selection.
- `inactivity_reason_required` maps to the reason select and its localized recovery guidance.
- The reason control is removed from focus order while hidden.

## 6. Inactive-site execution guard

### Trigger

Before creating or editing an activity row, normalize `quantity` using the same numeric rules as the grid. If the value is greater than zero and the current header state is inactive, pause the save and open a confirmation dialog.

The Persian prompt is exactly:

```text
کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت کارکرد اجرایی اطمینان دارید؟
```

An equivalent localized English prompt is supplied through the locale catalog.

### Confirm

- Close the dialog.
- Resume the original save exactly once through the normal online API or offline queue path.
- Preserve all ordinary authorization, validation, provenance, conflict, and error handling.
- Confirmation is an acknowledgment only; it does not alter site status or the activity payload.

### Cancel

- Close the dialog and restore focus to the initiating row/control.
- Do not call the API, enqueue an offline mutation, or mark the row saved.
- Keep the user's draft available for correction.
- Suppress repeated autosave prompts for the identical canceled row snapshot until the row changes or the user explicitly retries.

### Coverage boundary

The guard applies to both new and edited activity rows, manual save and autosave, and online and offline modes. It does not prompt for blank, zero, or negative/non-executable quantities, nor when the effective current header status is active.

## 7. Save pipeline and stale-state prevention

- `ActivityTab` receives the current editable header status, not only the last server-refetched report.
- An optional asynchronous pre-save guard is invoked before the save pipeline selects online mutation versus offline queueing.
- Changing the row after cancel invalidates the canceled-snapshot suppression.
- Changing the header from inactive to active before save prevents the prompt; changing it to inactive makes the next positive save eligible.
- Double confirmation/clicking cannot issue duplicate writes.

## 8. Offline compatibility

- IndexedDB schema version increments without deleting user data.
- Cached reports and pending/failed queue payloads normalize `sunny→clear`, `partly_cloudy→cloudy`, and `foggy→cloudy` during upgrade.
- Queue identity, order, retry count, timestamps, failure details, and unrelated payload properties are preserved.
- The new fields participate in offline serialization, replay, and conflict display.
- The activity guard runs before queue insertion, so cancellation is mutation-free even without connectivity.

## 9. Localization and accessibility

- All new field labels, choice labels, validation messages, empty states, and dialog controls come from `fa` and `en` locale files; stable API identifiers are never shown as fallback copy.
- Persian layout remains RTL and English remains LTR.
- Labels are programmatically associated with controls; required/error state is announced.
- The confirmation uses the existing accessible dialog primitive with a labelled title/description, keyboard-operable confirm/cancel actions, focus trap, Escape/cancel behavior, and focus restoration.
- Weather meanings are conveyed by text in addition to icons/color.

## 10. Acceptance scenarios

1. An editor opens a missing date; one full-day summary is ensured. Reopening it does not duplicate the report.
2. A viewer opens an existing date via GET and can view it; opening a missing date shows no data and causes no database write.
3. The five weather choices appear consistently in daily header, specialty form, and standalone weather log.
4. Invalid temperature bounds and reversed range block online and offline writes with the error on the correct field.
5. Selecting inactive reveals the reason select; save is blocked until a reason is selected; selecting active clears it.
6. Weather-impact notes survive save/refetch and appear in the official PDF.
7. A positive activity quantity on an inactive day prompts; cancel writes nothing; confirm writes once.
8. The same guard behavior works while offline and after reconnect/replay.
9. Persian and English labels/messages are complete, and the dialog works using keyboard-only navigation.
