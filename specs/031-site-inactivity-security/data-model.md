# Data Model: Site Inactivity Reasons, Conflict Guard, and Daily-Report Access Hardening

**Feature**: `specs/031-site-inactivity-security` | **Date**: 2026-10-22

## 1. Inactivity Reason Vocabulary

One language-independent vocabulary, already defined by `InactivityReason` in `apps/api/core/field_reports/models.py`:

| Value | Persian label | English label |
|-------|---------------|---------------|
| `weather` | نامساعد بودن شرایط جوی | Unfavorable weather |
| `holiday` | تعطیل رسمی / تقویمی | Official / calendar holiday |
| `strike_or_dispute` | اختلاف یا اعتصاب | Labor dispute or strike |
| `client_stop_order` | دستور توقف کارفرما / مشاور | Client / consultant stop order |
| `safety_incident` | حادثه ایمنی | Safety incident |

Catalog locations (already present): `fa.json` / `en.json` → `dailyReports.inactivityReasons.{value}`.

## 2. Daily Report — header fields touched by this feature

| Field | Representation | Default / optionality | Rules (existing, verified) |
|-------|----------------|----------------------|----------------------------|
| `site_status` | `active` \| `inactive` | default `active` | Meaning required only for final saved state |
| `inactivity_reason` | one of the five values or `''` | `blank=True`, default `''`, `max_length=30` | Required while saved status is inactive; cleared when status is active |

### Conditional invariant (effective-state)

For any write that yields a candidate record:

1. If candidate `site_status == 'inactive'` and candidate `inactivity_reason` is empty → reject with field-specific error, stable code `inactivity_reason_required`, attached to `inactivity_reason`. Candidate state merges supplied values with stored values for partial updates (the same effective-state approach as spec 030 temperatures).
2. If candidate `site_status == 'active'` → `inactivity_reason` is set to `''` on save (model `save()` and `clean()` both enforce this; no stale reason remains on an active record).
3. Equal-meaning special case: switching inactive → active → (save) → inactive requires selecting a reason again; nothing about an earlier reason is silently reused.

### Enforcement surfaces (all exist)

| Surface | Location |
|---|---|
| Model invariants | `DailyReport.clean()` / `save()` |
| Header serializer | `field_reports/serializers.py` validate — code `inactivity_reason_required` on `inactivity_reason` |
| Lifecycle paths | `daily_report_views.py` submit / review / approve rechecks |
| Offline replay | sync-batch → same serializer rules |
| Summary rebuild | `daily_report_aggregation.py` preserves a validly chosen reason; clears it when the reconciled status is active |

## 3. Activity Row — inactive-day guard input

| Field | Guard trigger |
|-------|---------------|
| `quantity` (decimal, nullable) | Warning triggers iff candidate row quantity is strictly `> 0` and the report's `site_status == 'inactive'` |
| `quantity_measured` (boolean) | When `false`, measured quantity is treated as not supplied → no warning |

Client predicate: `shouldWarnInactiveSiteActivity(siteStatus, qty)` in `apps/web/src/components/daily_reports/activity-guard.ts` (blank/null/NaN never trigger; both new-row creation and edit go through `beforeSaveRow`).

## 4. Copy and localization artifacts (residual deltas)

| Artifact | Current state | Required state |
|---|---|---|
| Fallback warning constants (`INACTIVE_ACTIVITY_WARNING_FA/EN`) in `activity-guard.ts` | «…ثبت کارکرد اجرایی اطمینان دارید؟» | Exact approved text: «کارگاه در این تاریخ تعطیل ثبت شده است؛ آیا از ثبت فعالیت اجرایی با حجم مثبت اطمینان دارید؟» and the matching English equivalent; constants and catalog keys must carry identical text |
| Component locale key in `ActivityTab.tsx` | Requests `dailyReports.inactiveActivityWarning` (missing key → fallback always) | Request the catalog key `dailyReports.inactiveSiteActivityWarning` |
| Dialog title + footer buttons (`ActivityTab.tsx`) | Inline Persian strings | Localized from catalog (title key added; buttons reuse existing `confirmActivity` / `cancelActivity`) |
| Shared option labels (`INACTIVITY_REASONS` in `api/daily-reports.ts`) | Hardcoded Persian labels | Values stay here; labels rendered via `dailyReports.inactivityReasons` in `ReportHeader.tsx` and `daily-report-view.tsx` |

## 5. Preserved behaviors (no change required)

| Operation | Existing behavior (verified) |
|-----------|------------------------------|
| Correction / version copy | `correction_service.py` copies `inactivity_reason` |
| Sync conflict comparison | `inactivity_reason` appears in `conflict_fields` (dedicated test) |
| Readback | Serializers expose `inactivity_reason_label`; summary view appends the localized reason |
| PDF | Header table shows the reason label when inactive and reason non-empty; shows nothing fabricated when active or reason empty |
| by-date permissions | POST requires `edit_reports` (403 for viewers tested); GET keeps `view_reports` |

## 6. Migration and Rollback

No new migration is required or permitted for the residual scope: the field, choices, and committed history exist (`0018_daily_header_weather.py` records `inactivity_reason`). Schema is verified with `manage.py verify_blueprint_schema`. If a copy/key change required a behavior rollback, restoring the two constants and two catalog JSON files is its complete inverse.
