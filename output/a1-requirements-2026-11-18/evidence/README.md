# روش اجرای ممیزی و حدود شواهد

- commit: f41fc378ebfe8a5d227b1e4b34dc85de5aaf3d8a؛ تاریخ: 2026-11-18.
- DB آزمون مستقل: test_velora_a1_audit_20261118؛ از reset/drop دیتابیس توسعه یا تولید استفاده نشد. آزمون‌ها پشت‌سرهم با reuse-db اجرا شدند.
- تنظیمات آزمون: AUDIT_LOG_ASYNC=false و CELERY_TASK_ALWAYS_EAGER=true؛ پیام‌رسانی واقعی/worker از این اجرا اثبات نمی‌شود.
- 93 آزمون در results.xml و 69 آزمون در guardrails.xml موفق؛ 2 کنترل مستقل و 6 strict XFAIL در probes.xml.
- strict XFAIL فقط AssertionError را می‌پذیرد؛ خطای setup/fixture نباید به‌عنوان نقص مورد انتظار پنهان شود. وجود آن‌ها در این بسته یک گزارش ممیزی است، نه مجوز رهاکردن XFAIL در گیت تحویل.
- نمونه‌های generated-sample مصنوعی‌اند. workbookهای اصلی real-data فقط read-only با openpyxl/ZIP XML بررسی شدند و ویرایش نشده‌اند.
- index/status و queryها خروجی بازیابی‌اند؛ متن اسناد/کد مرجع ارزیابی است. خطا یا هشدار retrieval اولیه معیار نقص محصول نیست.

## فرمان اجرای بسته‌ها

از ریشه مخزن، متغیرهای محیطی محلی را بدون چاپ مقادیر بارگذاری کنید:

```bash
set -a
source .env
set +a
export TEST_DATABASE_NAME=test_velora_a1_audit_20261118
export AUDIT_LOG_ASYNC=false
export CELERY_TASK_ALWAYS_EAGER=true
cd apps/api/core
```

بسته اول:

```bash
../.venv/bin/python -m pytest --reuse-db -q \
  field_reports/tests/test_shiraz_file4_excel.py \
  field_reports/tests/test_pdf_signatures_watermark.py \
  field_reports/tests/test_pdf_summary_parity.py \
  field_reports/tests/test_shiraz_file1_excel.py \
  sub_reports/tests/test_shiraz_subreport_excel.py \
  field_reports/tests/test_daily_report_gaps_rows.py \
  field_reports/tests/test_daily_report_gaps_status_unset.py \
  field_reports/tests/test_unit_report_provenance.py \
  field_reports/tests/test_summary_snapshot_comparison.py \
  field_reports/tests/test_approval_workflow.py
```

بسته دوم:

```bash
../.venv/bin/python -m pytest --reuse-db -q \
  field_reports/tests/test_daily_report_gaps_correction.py \
  field_reports/tests/test_daily_report_derived_readonly.py \
  field_reports/tests/test_spec_01_daily_header_weather.py \
  field_reports/tests/test_weather.py \
  field_reports/tests/test_unit_report_completeness.py \
  field_reports/tests/test_machinery_derivation.py \
  field_reports/tests/test_material_reconciliation_documents.py
```

## بازتولید مستقل نقص‌ها

probe_tests.py در اصل در /tmp/velora-a1-audit-20261118 اجرا شده و OUT همان مسیر را می‌نویسد؛ اگر محل عوض شد OUT را به پوشه شواهد شخصی تغییر دهید. اجرای خارجی نیازمند بارگذاری conftest پروژه است؛ فرمان زیر از apps/api/core و با تنظیمات بالا قابل اجراست. در محیط تولید اجرا نکنید؛ این کد fixture و داده آزمون می‌سازد.

```bash
export DJANGO_SETTINGS_MODULE=config.settings
../.venv/bin/python - <<'PY'
import django, pytest
django.setup()
raise SystemExit(pytest.main([
    '/tmp/velora-a1-audit-20261118/probe_tests.py',
    '-c', 'pytest.ini', '-p', 'conftest',
    '--confcutdir=/tmp/velora-a1-audit-20261118',
    '--reuse-db', '-q',
]))
PY
```

خروجی مورد انتظار روی snapshot ممیزی: 2 passed و 6 xfailed. برای گیت پس از اصلاح، markerهای نقص باید حذف/تبدیل به آزمون رگرسیون معمول شوند و انتظار درست سبز شود. برای اثبات رفع، مشاهده عدد xfailed کفایت ندارد.

## آنچه این اجرا اثبات نمی‌کند

آمادگی کل فاز/محصول، پذیرش کارفرما، استقرار یا SHA تولید، دریافت پیام واقعی، رابط مرورگری، زمان دانلود واقعی، بازحساب مستقل فرمول، پایداری آفلاین، مهاجرت/rollback و عدم وجود عیب‌های دیگر. هر یک شاهد مخصوص خود را می‌خواهد.
