# شش پرامپت اجرای A.6 با Spec Kit

تهیه: ۱۵ آبان ۱۴۰۵ / 2026-11-05.

هر فایل زیر مستقل و قابل کپی است. کل محتوای فایل فاز مورد نظر را در یک گفتگوی اجرایی بده؛ عامل از speckit-specify شروع می‌کند و پس از رفع ابهام مؤثر، مهارت‌های بعدی را به ترتیب اجرا می‌کند. این بسته صرفاً آماده‌سازی پرامپت‌هاست؛ هنوز Feature یا پیاده‌سازی جدید ساخته نشده است.

ترتیب: specify → clarify → plan → tasks → analyze → implement → converge؛ اگر converge کار افزود، implement و سپس converge دوباره اجرا شوند. analyze خواندنی است؛ converge فقط پس از implement و به‌صورت append-only روی tasks عمل می‌کند. جزئیات در خود هر فایل تکرار شده تا به متن مشترک جدا وابسته نباشد.

فازها به ترتیب اجرا شوند؛ پس از پایان هر فاز، مسیر Feature واقعی و قرارداد تحویل آن ثبت شود و فاز بعد بر همان شواهد شروع شود. شماره پوشه specها از قبل رزرو نشده و Feature فعال فعلی بازنویسی نمی‌شود.

- [پرامپت مستقل A6-P1 — تثبیت سیاست‌ها و رفع نقص‌های فوری](</home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/prompts/01-a6-p1-access-policy.md>).
- [پرامپت مستقل A6-P2 — نقش، سمت و مجوز مؤثر در محدوده پروژه](</home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/prompts/02-a6-p2-project-roles.md>).
- [پرامپت مستقل A6-P3 — گردش کامل حساب و تیم پروژه](</home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/prompts/03-a6-p3-team-lifecycle.md>).
- [پرامپت مستقل A6-P4 — پوشش یکسان دسترسی و محرمانگی در همه ماژول‌های موجود](</home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/prompts/04-a6-p4-module-access.md>).
- [پرامپت مستقل A6-P5 — تکمیل ممیزی و تاریخچه قابل استفاده](</home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/prompts/05-a6-p5-access-history.md>).
- [پرامپت مستقل A6-P6 — آزمون مستقل، راهنمای مدیر و پذیرش کارفرما](</home/hossein/Desktop/projects/building-management/output/a6-requirements-2026-11-04/prompts/06-a6-p6-delivery-acceptance.md>).

تمام ۵۳ ردیف غیر اختیاری، فاز اصلی مشخص دارند؛ موارد مشترک و تکمیل تدریجی آن‌ها در متن هر پرامپت آمده است. A6-R54 فقط با تصمیم صریح وارد دامنه می‌شود.

این متن تاریخ تحویل یا برآورد مقطوع نیست. ظرفیت قبلی یک توسعه‌دهنده با روزی چهار ساعت و هر هفت روز هفته است؛ اجرای موازی اجباری پیشنهاد نمی‌شود.
