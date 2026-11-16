# بسته تحویل فنی A.7 — ۲۰۲۶/۱۱/۱۶

نسخه منبع: `2090da13f90756e9512070ffcd4feb87dcf5fd7a`
نسخه حاوی شواهد و راهنما: `97dbc26b4c22c6843a970729b3d57008d8ce4069`

آمادگی فنی `ready_for_acceptance` است. نتیجه انسانی `pending` و صورت‌جلسه بدون امضا است. دامنه و محدودیت‌های مصوب در guide.md آمده است. این بسته برای پذیرش مستقل در Linux x86_64 دارای systemd، cgroup v2 و Docker Compose آماده شده است. تمام سرویس‌ها روی localhost هستند.

## کنترل و راه‌اندازی بدون دانلود وابستگی

از همین پوشه:

```bash
sha256sum -c SHA256SUMS
gunzip -c runtime-images.tar.gz | docker load
tar -xzf source.tar.gz
cd source
ops/a7-p5/prepare-host.sh
cp -n ops/a7-p5/.env.acceptance.example ops/a7-p5/.env.acceptance
chmod 600 ops/a7-p5/.env.acceptance
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml -f ops/a7-p5/compose.web.yml up -d --no-build --pull never
```

تصاویر API، workerها، وب کامپایل‌شده، PostgreSQL و Redis داخل آرشیو هستند. برای شروع نیاز به pnpm، نصب package یا build مجدد ندارید. Runtime وب همان باینری Node آزموده‌شده و وابستگی‌های قفل‌شده را دارد؛ لایه پایه آن با API مشترک است. اگر پوشه خروجی وب جداگانه لازم است، از ریشه source، فایل ../web-build.tar.gz را باز کنید.

پس از healthy شدن API و آماده شدن worker:

```bash
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec -T api python manage.py verify_import_runtime --preflight
docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml exec -T api python manage.py maintain_import_jobs --operation recovery
python3 ops/a7-p5/seed-delivery.py
```

preflight تا آماده شدن worker ممکن است نیاز به تکرار داشته باشد. بازکردن `http://127.0.0.1:15173/login` و ورود با پنج حساب فایل خصوصی ops/a7-p5/.runtime-delivery.json، نقطه شروع guide.md است. فایل حساب‌ها فقط روی همین محیط با مجوز 0600 ساخته می‌شود و داخل بسته عمومی نیست. اسکریپت seed تنها روی دیتابیس خصوصی a7p5 اجرا می‌شود.

API روی 18000، پایگاه خصوصی روی 55434، Redis خصوصی روی 56379 و وب روی 15173 است. پورت پایگاه با A7P5_POSTGRES_PORT قابل تغییر است. فایل plan.mpp و fixtureها در source/real-data و specs هستند. منبع دارای Git با تاریخچه محدود به دو commit تحویل است؛ هیچ remote خصوصی یا تاریخچه نامرتبطی صادر نشده است.

## بازبینی و آزمون

از ریشه source با Python 3:

```bash
python3 specs/056-a7-p6-delivery-acceptance/evidence/validate_package.py
git log --oneline -2
```

اعتبارسنج بدون سرویس، تمامیت شواهد ثبت‌شده، نسخه و منبع را بررسی می‌کند؛ اجرای دوباره آزمون‌ها از quickstart.md به وابستگی‌های توسعه، Node/pnpm، مرورگر Playwright و PostgreSQL/Redis تست میزبان نیاز دارد. تصاویر آماده برای اجرای نمایش کارفرما به این ابزارهای توسعه نیاز ندارند. محیط پذیرش، حساب‌ها و داده آزمایشی مستقل‌اند؛ اتصال داده واقعی یا انتشار عمومی جزء اجرای این راه‌اندازی نیست.

مستندات: guide.md مسیر نمایش؛ minutes.md محل ثبت نظر و امضای نماینده؛ handoff.md و release-verification.json هویت و شواهد؛ RELEASE.json شناسه تصویرها؛ SHA256SUMS کنترل فایل‌ها. تمام ۵۶ ردیف و ۲۸ سناریو در source/specs/056-a7-p6-delivery-acceptance/evidence قرار دارند. M04 تعیین تکلیف شرطی دامنه است و ادعای آزمون Excel عمومی ندارد.

برای توقف فقط همین محیط از همان دو فایل Compose و دستور down استفاده کنید. حذف داده‌های پذیرش با down -v تنها پس از نگهداری شواهد جلسه انجام شود. سرویس‌های مشترک و تولیدی را تغییر ندهید.
