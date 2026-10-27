# شواهد ممیزی SPEC-04

مبنای اجرا: `develop@765e54b`، 2026-10-27. تمام دستورها در همین checkout اجرا شده‌اند. داده واقعی پروژه تغییر نکرد؛ تست‌های Django از دیتابیس‌های تست مستقل استفاده کردند. env از فایل ریشه بارگذاری شد و محتوای آن در گزارش چاپ نشده است.

## نتایج

- `pytest-sync-batch.txt`: مجموعه موجود، **17 passed**، دو warning، **87.07s**. warningها مربوط به reportlab و وابستگی آینده pandas به pyarrow هستند.
- `probe-backend.txt`: چهار probe، **4 passed**، دو warning، **88.47s**. assertionها عمداً رفتار معیوب فعلی را تأیید می‌کنند. این عدد «چهار تست پذیرش موفق» نیست.
- `probe-frontend.txt`: شش سناریوی بررسی منطق، exit code صفر. پنج سناریو رفتار ناقص را نشان می‌دهند و سناریوی آخر کنترل مثبت انتقال آخرین labor snapshot به builder است. این harness، IndexedDB یا browser را اجرا نمی‌کند.

## بازاجرای تست موجود

از ریشه مخزن:

```bash
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
export TEST_DATABASE_NAME=test_spec04_audit_20261027_01
export AUDIT_LOG_ASYNC=false
export CELERY_TASK_ALWAYS_EAGER=true
../.venv/bin/python -m pytest field_reports/tests/test_sync_batch.py -q
```

برای اجرای همزمان یا اجرای بعدی، نام دیتابیس تست جدید انتخاب کنید. pytest-django دیتابیس تست را ایجاد و در پایان حذف می‌کند؛ این دستور دیتابیس توسعه را reset نمی‌کند. باید سرویس PostgreSQL و دسترسی ایجاد دیتابیس تست موجود باشند. fixtureهای پروژه cache را در تست به locmem تغییر می‌دهند؛ این اجرا به معنی تست Redis در مسیر زنده نیست.

## بازاجرای probe بک‌اند

probe از fixtureهای `apps/api/core/conftest.py` استفاده می‌کند. برای اطمینان از discovery همان fixtureها، نسخه موقت در محل تست‌های canonical قرار می‌گیرد. ابتدا اطمینان حاصل کنید فایل مقصد وجود ندارد؛ فایل موجود را overwrite نکنید.

```bash
cd /home/hossein/Desktop/projects/building-management
python3 - <<'PY'
from pathlib import Path
src = Path('reports_gaps/04/evidence/probe_backend.py')
dst = Path('apps/api/core/field_reports/tests/test_spec04_audit_probe.py')
with dst.open('x') as handle:
    handle.write(src.read_text())
PY
cd /home/hossein/Desktop/projects/building-management/apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
export TEST_DATABASE_NAME=test_spec04_probe_20261027_01
export AUDIT_LOG_ASYNC=false
export CELERY_TASK_ALWAYS_EAGER=true
../.venv/bin/python -m pytest field_reports/tests/test_spec04_audit_probe.py -q -s
```

پس از پایان، فقط فایل موقتی را که خودتان ساخته‌اید حذف کنید. در ممیزی حاضر محتوا با `probe_backend.py` یکسان بود و فایل موقت پس از اجرای موفق حذف شد؛ هیچ تست canonical تغییر نکرد.

چهار probe این موارد را تأیید کردند:

1. child POST عادی روی summary برابر 400؛ batch با `activities: []` برابر 200/merged؛ ردیف derived حذف شد.
2. هدر نامعتبر برابر per-item error؛ shell جدید در دیتابیس باقی ماند.
3. پس از تغییر persisted status به approved بین خواندن و merge، ذخیره instance قدیمی آن را draft کرد.
4. approved پیداشده در ensure، notes جدید دریافت کرد و نتیجه created بود.

موارد ۳ و ۴ با monkeypatch ترتیب رخدادها را قطعی می‌کنند؛ تست همزمان دو connection نیستند. در مورد ۴ monkeypatch رکورد approved را پیش از فراخوانی ensure واقعی می‌سازد و خود ensure واقعی اجرا می‌شود.

## بازاجرای probe فرانت‌اند

```bash
cd /home/hossein/Desktop/projects/building-management
node reports_gaps/04/evidence/probe_frontend.cjs
```

این فایل TypeScript نصب‌شده همین checkout (`5.9.3`) را از node_modules بارگذاری می‌کند، متن جاری دو فایل `offlineWrite.ts` و `syncService.ts` را transpile و در VM اجرا می‌کند. فقط در نسخه حافظه‌ای، export آزمایشی برای دو تابع داخلی اضافه می‌شود؛ فایل محصول تغییر نمی‌کند. API و storage mock هستند، ولی parser، builder، تصمیم acknowledgment، نگاشت وضعیت و انتخاب صف، همان کد جاری‌اند.

تغییر snapshot کد ممکن است assertionها را fail کند؛ این می‌تواند نشانه رفع رفتار مورد ممیزی باشد و باید دوباره بررسی شود. خروجی قدیمی را به عنوان نتیجه کد جدید استفاده نکنید.

## موارد اجرا نشده

Playwright، refresh و restart واقعی مرورگر، Service Worker build تولید، محدودیت quota/eviction، چند تب، کنترل همزمان دو اتصال PostgreSQL و MinIO اجرا نشدند. typecheck و مجموعه کامل تست‌ها هم اجرا نشد؛ کار محصول تغییر نکرده و شواهد این ممیزی محدود به تست‌های ذکرشده است.
