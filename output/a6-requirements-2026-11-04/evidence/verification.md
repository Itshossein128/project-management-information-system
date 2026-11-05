# حدود شواهد این بررسی

نسخه کد: `2e9a82e97e92ac4410e040298ffbdfba2bfa85ca`؛ تاریخ: 2026-11-04.

- اجرای منتخب بک‌اند: ۱۲۶ موفق، صفر خطا/شکست/تست ردشده؛ ۸۲٫۱۸ ثانیه. فایل‌های tests.log و test-results.xml شاهدند.
- سه آزمون بازتولید نقص با `xfail(strict=True)` اجرا شد: هر سه نقص بازتولید شدند. برچسب skipped در XML برای XFAIL است، نه سه آزمون موفق پذیرش. خروجی probes.log نتیجه HTTP و اثر واقعی را ثبت کرده است.
- پایگاه آزمون مستقل: `test_velora_a6_inventory_20261104`؛ دادهٔ محیط اصلی برای این آزمون‌ها تغییر نکرد.
- آزمون گزارش HTML: نمایش ۵۴ نیازمندی، فیلتر ۲ مورد یافت‌نشده، جست‌وجوی A6-R29، بازشدن جزئیات، ۹ بسته، ۲۰ سناریو و ۲۹ حوزه؛ بدون خطای جاوااسکریپت و بدون بیرون‌زدگی افقی در عرض ۳۹۰ پیکسل. این آزمون مربوط به گزارش خروجی است و آزمون مرورگر خود محصول نیست.
- بررسی TypeScript فایل canvas موفق بود. این بررسی، اجرای رابط خود محصول یا پذیرش مشتری را ثابت نمی‌کند.
- نمایه knowledge در پایان بررسی hybrid و fresh=true بود. اصل اسناد با source-manifest.json قابل تطبیق است.

## بازاجرای مجموعه منتخب

از ریشه مخزن، تنظیمات محلی را بدون چاپ محتوا بارگذاری کنید. به PostgreSQL و Redis محلی نیاز است. دستور زیر همان محدودهٔ آزمون اجراشده را مشخص می‌کند:

```bash
cd apps/api/core
set -a
source /home/hossein/Desktop/projects/building-management/.env
set +a
export AUDIT_LOG_ASYNC=false
export CELERY_TASK_ALWAYS_EAGER=true
export TEST_DATABASE_NAME=test_velora_a6_inventory_20261104
../.venv/bin/python -m pytest permissions/tests authentication/tests projects/tests/test_members.py projects/tests/test_stakeholder_contacts_acl.py projects/tests/test_role_dashboard_packs.py master_data/tests/test_org_refs.py hr/tests/test_wage_acl_and_cost_estimate.py documents/tests/test_attachment_signing_security.py sub_reports/tests/test_unit_report_permissions.py audit/tests.py -q --reuse-db
```

فایل `test_characterization.py` فقط برای بازتولید سه نقص و خارج از مجموعه رسمی محصول نوشته شده است. در همین محیط تنظیم‌شده، آن را با `-c pytest.ini` و مسیر مطلق فایل اجرا کنید. پس از رفع نقص، شرط xfail باید بازبینی شود؛ تغییر نتیجه به XPASS در این قالب عمداً خطا محسوب می‌شود.

## چیزهایی که این شواهد ثابت نمی‌کنند

تکمیل کل ماتریس دسترسی تمام ماژول‌ها، رابط کاربری محصول، سرویس فایل واقعی، همه حالت‌های همزمانی، محیط تولید و تأیید نهایی کارفرما در این بررسی اجرا نشده‌اند. نقص‌ها شناسایی و مستند شدند؛ محصول در این نوبت اصلاح نشده است.
