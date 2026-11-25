# گزارش ارزیابی و راستی‌آزمایی تضمین کیفیت (QA Verification Report) - نیازمندی A.1.01

- **شناسه نیازمندی:** `A.1.01`
- **فاز تحویل:** `A.1` (گزارش روزانه و خروجی‌ها)
- **مرحله:** `Stage 1.2` (ارزیابی نیازمندی از دید کاربر نهایی و آزمونگر QA)
- **عنوان نیازمندی:** نهایی‌کردن قواعد اطلاعات روزانه
- **معیار پذیرش:** قرارداد داده روزانه برای هر فیلد شامل منبع، واحد، تبدیل، قاعده null/zero، خروجی و provenance نسخه‌دار باشد؛ fixture اجرایی روز مرجع برچسب‌گذاری شود و تصمیم‌های مؤثر بر خروجی رسمی (هوا، شیفت، مدت، نیروی انسانی و unknown در برابر zero) ثبت و قابل آزمون باشند.
- **وضعیت پیاده‌سازی و آزمون:** `implemented_and_verified` (QA Status: `qa_passed`)
- **تاریخ ارزیابی:** ۲۴ نوامبر ۲۰۲۶

---

## ۱. ارزیابی قرارداد داده روزانه (Data Contract v1.0.0)

بر اساس قرارداد داده مرجع موجود در `apps/api/core/field_reports/contracts/daily_report_contract_v1.json` و اندپوینت رسمی `/api/v1/projects/{project_id}/daily-reports/contract/`:

1. **نسخه‌گذاری و پوشش فیلدها:**
   - نسخه قرارداد: `1.0.0`
   - نسخه فرم مرجع: `shiraz-file4-v1`
   - تعداد نگاشت‌های فیلد (`field_mappings`): ۱۲۸ فیلد مشخص و استاندارد در ۱۸ بخش جامع روزانه.
   - هر فیلد دارای `label_fa`، `label_en`، `source_document`، `source_field_or_cell`، `unit`، `conversion_rule`، `zero_unset_rule`، `print_location` و `drill_down_path` است.

2. **قواعد معنایی صفر و مقدار ثبت‌نشده (Rule C02):**
   - مقدار ثبت‌شده `0` یا `0.00` به عنوان صفر اندازه‌گیری‌شده معتبر تلقی می‌شود.
   - مقادیر خالی یا اندازه‌گیری‌نشده به صورت صریح `null` باقی می‌مانند و از تبدیل خاموش (silent coercion) به صفر جلوگیری شده است.

3. **قواعد شیفت‌های متعارف و ساعات کارکرد واقعی (Rule C03):**
   - شناسه‌های استاندارد شیفت (`1`، `2`، `3`) در سربرگ، نیروی انسانی و فعالیت‌ها یکپارچه شده‌اند.
   - محاسبه نفر-ساعت کارکرد مستقیماً بر مبنای مدت زمان واقعی کارکرد هر شیفت انجام می‌پذیرد.

4. **کاتالوگ عناوین شغلی و پروفایل شیراز (Rule C04):**
   - ساختار ثابت ۳۴ عنوان ستادی و ۳۲ عنوان اجرایی الگوی شیراز حفظ شده است.
   - عناوین اضافی یا سفارشی پروژه به پیوست (Appendix) اختصاصی ارجاع می‌شوند تا ساختار چاپ مخدوش نگردد.

5. **ثبت منبع، ردپا و تصمیم‌های ثبت‌شده (Scope Decisions):**
   - ۱۱ تصمیم رسمی ثبت‌شده شامل `C01` تا `C10` و `GOV-01` با تفکیک دقیق وضعیت، رفتار مشاهده‌شده، متن تصمیم، عامل و تاریخ تصویب نگهداری می‌شوند.

---

## ۲. راستی‌آزمایی فیکسچر روز مرجع (Synthetic Reference Day Fixture)

- **کد پروژه مرجع:** `SIM-A1-001`
- **برچسب پروژه:** `[SYNTHETIC A.1 REFERENCE] کارگاه آزمایشی شیراز`
- **تاریخ گزارش:** `1406-03-01` (میلادی: `2027-05-22`)
- **شماره رسمی گزارش:** `SIM-A1-001-12-1406-03-01`
- **دستور بارگذاری داده مرجع:** `seed_a1_reference_fixture`
- **شناسه گزارش مرجع:** `fb9bcd42-a786-4b19-ba7b-1548c9526393`
- **ویژگی عدم اثر جانبی (Idempotency):** دستور ایجاد و بارگذاری روز مرجع مجدداً بررسی شد و از ایجاد پروژه‌های تکراری یا تغییر ناخواسته در پروژه‌های واقعی ممانعت می‌کند.

---

## ۳. کنترل دسترسی و امنیت (RBAC & Security)

- **دسترسی مدیر (Admin):** کد وضعیت `200 OK` به همراه بازگردانی کامل ساختار قرارداد داده و فیلدهای نگاشت.
- **دسترسی بازدیدکننده (Visitor):** کد وضعیت `403 Forbidden` بر روی پروژه مرجع به درستی اعمال گردید.
- **دسترسی کاربر احرازهویت‌نشده (Anonymous):** کد وضعیت `401 Unauthorized` اعمال گردید.

---

## ۴. نتایج آزمون‌های خودکار تخصصی (Automated Verification)

تمام ۱۱ آزمون جامع سوئیت `field_reports/tests/test_a1_b01_data_contract.py` روی PostgreSQL 16 و Redis با موفقیت اجرا شدند:

```text
============================= test session starts ==============================
collected 11 items

field_reports/tests/test_a1_b01_data_contract.py::test_seed_is_idempotent_and_scoped PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_seed_refuses_existing_non_fixture_project PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_contract_permissions_and_query_params PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_measured_zero_and_unknown_are_distinct PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_canonical_shifts_and_actual_duration PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_form_profile_has_fixed_slots_and_preserves_appendix PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_numbering_observed_weather_and_summary PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_legacy_summary_warns_without_merging_reports PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_b01_migrations_preserve_legacy_and_enforce_uniqueness PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_published_contract_covers_reference_form_fields_and_governance PASSED
field_reports/tests/test_a1_b01_data_contract.py::test_forecast_uses_local_days_caches_and_degrades PASSED

================== 11 passed, 2 warnings in 188.11s (0:03:08) ==================
```

---

## ۵. جمع‌بندی نهایی

نیازمندی **A.1.01** به صورت کامل و دقیق پیاده‌سازی شده، تمامی معیارهای پذیرش (قرارداد داده نسخه‌دار ۱۲۸ فیلدی، تفکیک صفر و null، قواعد شیفت و آب‌وهوا، ثبت و تصویب تصمیم‌های C01 تا C10 و GOV-01، فیکسچر تکرارپذیر روز مرجع SIM-A1-001 و کنترل دسترسی RBAC) در محیط واقعی بک‌اند و فرانت‌اند ارزیابی شده و تأیید می‌گردد. هیچ نقص یا کمبودی (Zero Defects) در این نیازمندی وجود ندارد.
