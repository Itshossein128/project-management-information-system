# گزارش بازبینی تضمین کیفیت (QA Verification Report) - نیازمندی A.1.01

- **شناسه نیازمندی:** `A.1.01`
- **فاز تحویل:** `A.1` (تطبیق و تحویل اولیه گزارش روزانه)
- **مرحله:** `Stage 1.2` (ارزیابی نیازمندی از دید کاربر نهایی و آزمونگر QA)
- **عنوان نیازمندی:** قواعد داده و fixture کامل روز مرجع
- **معیار پذیرش:** قاعده null/صفر، شیفت، شمارش نفر و منبع هر بخش ثبت شود.
- **وضعیت پیاده‌سازی و آزمون:** `implemented_and_verified` (QA Status: `qa_passed`)
- **تاریخ ارزیابی:** ۲۲ نوامبر ۲۰۲۶

---

## ۱. ارزیابی قواعد داده (Data Contract Rules)

بر اساس بررسی فایل قرارداد داده مرجع `apps/api/core/field_reports/contracts/daily_report_contract_v1.json` و پیاده‌سازی متناظر آن در سرویس‌های دیتابیس و اعتبارسنجی:

1. **تفکیک صفر معتبر و ناشناخته/null (قاعده C02):**
   - مقدار ثبت‌شده `0` یا `0.00` یک مقدار عددی معتبر و اندازه‌گیری‌شده است.
   - مقادیر ثبت‌نشده یا خالی به صورت صریح `null` باقی می‌مانند و به هیچ عنوان به صفر تبدیل نمی‌شوند (no silent coercion).
   - تابع `coerce_optional_decimal` و ستون‌های دیتابیس به درستی تمایز صفر و ناشناخته را حفظ می‌کنند.

2. **قواعد شیفت و مدت زمان کارکرد واقعی (قاعده C03):**
   - شناسه‌های استاندارد شیفت به صورت یکپارچه به عنوان مقادیر استاندارد `1`، `2`، `3` بین سربرگ، نیروی انسانی و فعالیت‌ها نگهداری می‌شوند.
   - نفر-ساعت کارکرد صرفاً بر مبنای مدت‌زمان واقعی ثبت‌شده در هر شیفت محاسبه می‌شود و هرگونه کسری به عنوان مقدار ناشناخته محاسبه شده و از پیش‌فرض ۸ ساعت اجتناب می‌شود.

3. **شمارش نفرات و کاتالوگ عناوین شغلی (قاعده C04):**
   - تفکیک کاتالوگ قابل تنظیم عناوین شغلی از الگوی فرم مرجع شیراز (۳۴ عنوان ستادی/غیرمستقیم و ۳۲ عنوان اجرایی/مستقیم).
   - عناوین سفارشی یا مازاد بر ساختار ۳۴/۳۲ در بخش پیوست (Appendix) اختصاصی ثبت می‌شوند تا ساختار استاندارد فرم مخدوش نشود.

4. **ثبت منبع و ردپای هر بخش (Provenance & Attribution):**
   - تمامی ۱۸ بخش تفصیلی گزارش روزانه دارای متادیتای انتساب، ردپای منبع و اثرانگشت هش یکپارچگی داده‌ها (metadata fingerprint) هستند.

---

## ۲. راستی‌آزمایی روز مرجع مصنوعی (Synthetic Reference Day Fixture)

- **کد پروژه مرجع:** `SIM-A1-001`
- **برچسب پروژه:** `[SYNTHETIC A.1 REFERENCE]`
- **تاریخ شمسی گزارش:** `1406-03-01` (تاریخ میلادی: `2027-05-22`)
- **روز پروژه:** `12` (با احتساب تاریخ شروع واقعی `1406-02-21`)
- **شماره رسمی گزارش:** `SIM-A1-001-12-1406-03-01`
- **دستور بارگذاری:** `seed_a1_reference_fixture`
- **تکرارپذیری (Idempotency):** دستور بارگذاری بارها اجرا شده و از بازنویسی یا آلوده‌سازی پروژه‌های واقعی سیستم جلوگیری می‌کند.

---

## ۳. نتایج آزمون‌های خودکار (Automated Test Execution)

مجموعه آزمون‌های تخصصی این نیازمندی در فایل `field_reports/tests/test_a1_b01_data_contract.py` بر روی دیتابیس PostgreSQL 16 و حافظه کش Redis اجرا شدند:

```text
============================= test session starts ==============================
collected 11 items

field_reports/tests/test_a1_b01_data_contract.py::test_seed_is_idempotent_and_scoped PASSED [  9%]
field_reports/tests/test_a1_b01_data_contract.py::test_seed_refuses_existing_non_fixture_project PASSED [ 18%]
field_reports/tests/test_a1_b01_data_contract.py::test_contract_permissions_and_query_params PASSED [ 27%]
field_reports/tests/test_a1_b01_data_contract.py::test_measured_zero_and_unknown_are_distinct PASSED [ 36%]
field_reports/tests/test_a1_b01_data_contract.py::test_canonical_shifts_and_actual_duration PASSED [ 45%]
field_reports/tests/test_a1_b01_data_contract.py::test_form_profile_has_fixed_slots_and_preserves_appendix PASSED [ 54%]
field_reports/tests/test_a1_b01_data_contract.py::test_numbering_observed_weather_and_summary PASSED [ 63%]
field_reports/tests/test_a1_b01_data_contract.py::test_legacy_summary_warns_without_merging_reports PASSED [ 72%]
field_reports/tests/test_a1_b01_data_contract.py::test_b01_migrations_preserve_legacy_and_enforce_uniqueness PASSED [ 81%]
field_reports/tests/test_a1_b01_data_contract.py::test_published_contract_covers_reference_form_fields_and_governance PASSED [ 90%]
field_reports/tests/test_a1_b01_data_contract.py::test_forecast_uses_local_days_caches_and_degrades PASSED [100%]

================== 11 passed, 2 warnings in 170.07s (0:02:50) ==================
```

---

## ۴. جمع‌بندی نهایی

نیازمندی **A.1.01** به صورت کامل پیاده‌سازی شده، تمام معیارهای پذیرش (قاعده null در برابر صفر، شیفت، شمارش نفرات بر مبنای کاتالوگ و پیوست، و رهگیری منبع هر بخش) با موفقیت در محیط دیتابیس واقعی بررسی و تأیید گردید و هیچ نقصی (Zero Defects) در این بخش مشاهده نشد.
